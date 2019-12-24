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
from .metadata import VariablePool, Metadata
from .config import NormalizedTaskSettings, NormalizedConfig

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
        self, cfg: NormalizedConfig, metadata: Optional[VariablePool] = None,
    ):
        self._metadata = metadata

        # plugin search directory from lowest priority to highest
        # if no search dirlist is provided use the default
        self.search_dirs = cfg["search_dirs"] or [Path(d) / "plugins" for d in (dirs.site_data_dir, dirs.user_data_dir)]  # type: ignore[has-type]

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


class PreProcessManager(BaseTaskManager):
    def discover_tasks(self):
        return self._discover_tasks(PreProcess)


class PostProcessManager(BaseTaskManager):
    def discover_tasks(self):
        return self._discover_tasks(PostProcess)


class SourceManager(BaseTaskManager):
    def discover_tasks(self):
        return self._discover_tasks(Source)

    def aggregate(self, *results: List[Metadata]) -> List[Metadata]:
        raise NotImplementedError
