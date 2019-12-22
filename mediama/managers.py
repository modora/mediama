from typing import Set, List, Dict, Any, Type, TypedDict, Optional
import copy
from logging import getLogger
from pathlib import Path

from .utils import (
    import_module_from_path,
    unload_module,
    get_subclasses_from_module,
    discover_modules,
    dirs,
)
from .metadata import VariablePool
from .config import NormalizedTaskSettings

Rankings = List[Dict[str, Any]]

logger = getLogger(__name__)


class Task:
    def __init__(self, metadata: VariablePool):
        self.metadata = metadata.set_id(self.__class__.__name__)


class Process(Task):
    def main(self, **kwargs: Any):
        raise NotImplementedError


class PreProcess(Process):
    pass


class PostProcess(Process):
    pass


class Source(Task):
    def fetch_series(self, **kwargs: Any) -> Rankings:
        raise NotImplementedError

    def fetch_episodes(self, **kwargs: Any) -> Rankings:
        raise NotImplementedError


class BaseTaskManager:
    _tasks: Optional[Dict[str, Type[Task]]] = None

    def __init__(
        self,
        metadata: Optional[VariablePool] = None,
        search_dirs: Optional[List[Path]] = None,
    ):
        self._metadata = metadata

        # plugin search directory from lowest priority to highest
        # if no search dirlist is provided use the default
        self.search_dirs = (
            search_dirs
            if search_dirs
            else [
                Path(d) / "plugins" for d in (dirs.site_data_dir, dirs.user_data_dir)  # type: ignore[has-type]
            ]
        )

    @property
    def metadata(self):
        if self._metadata is None:
            raise RuntimeError("VariablePool not defined")
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    def discover_tasks(self):
        """
        Dev expected to override
        """
        raise NotImplementedError

    def _discover_tasks(self, t_obj: Task) -> Dict[str, Type[Task]]:
        """
        Find all tasks subclassed by t_obj and import their object classes but
        do not init them yet
        """
        if self._tasks is not None:
            return self._tasks

        search_dirs = filter(lambda path: path.exists(), self.search_dirs)

        # Find all python modules
        try:

            def files_gen():
                for dir_ in search_dirs:
                    yield from discover_modules(dir_)

        except Exception as e:
            logger.critical("Failed to discover modules")
            raise e
        # We found modules, so load them and scan for any tasks within them
        self._tasks = {}
        for file in files_gen():
            # attempt to import the file/package
            # if import fails, skip
            try:
                module = import_module_from_path(file)
            except Exception as e:
                logger.debug(f"Failed to import {file} because {e}")
                continue

            # find all tasks within the module
            try:
                gen = get_subclasses_from_module(module, t_obj)
            except Exception as e:
                logger.warning(f"Failed to find subclasses in {module.__name__}")
                unload_module(module)

            # Add tasks to the cache
            self._tasks.update({task.__name__: task for task in gen})
        return self._tasks

    def load_task(self, task: Type[Task]) -> Task:
        metadata = copy.deepcopy(self.metadata)
        metadata.set_id(task.name)
        return task(metadata)


class BaseProcessManager(BaseTaskManager):
    def load_task(self, task: Type[Process]) -> Process:  # type: ignore[override]
        return super().load_task(task)  # type: ignore[return-value]

    def main(self, task_list: List[NormalizedTaskSettings]):
        """
        Load and execute the ones found in the task
        list
        """
        tasks = self.discover_tasks()

        for task in task_list:
            # mypy typeddict bug
            task_name = task.name  # type: ignore[attr-defined]
            if task_name not in tasks:
                logger.warning(f"{task_name} not found")
                continue

            try:
                process_instance = self.load_task(tasks[task_name])
            except Exception as e:
                logger.error(f"Failed to load {task_name}. Reason: {e}")

            try:
                # mypy typeddict bug
                process_instance.main(**task.kwargs)  # type: ignore[attr-defined]
            except Exception as e:
                logger.error(f"Failed to execute {task_name}. Reason: {e}")


class PreProcessManager(BaseProcessManager):
    pass


class PostProcessManager(BaseProcessManager):
    pass


class SourceManager(BaseTaskManager):
    def main(self, task_list: List[NormalizedTaskSettings]):
        """
        Discover all sources, load them, identify and fetch series metadata, and
        finally identify and fetch episode metadata
        """
        raise NotImplementedError
