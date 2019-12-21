from typing import Set, List, Dict, Any, Type, TypedDict, Optional
import copy
from logging import getLogger

from .metadata import VariablePool
from .config import NormalizedTaskSettings

Rankings = List[Dict[str, Any]]

logger = getLogger(__name__)

class Task:
    name: str

    def __init__(self, metadata: VariablePool):
        self.metadata = metadata.set_id(self.name)


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
    def __init__(self, metadata: VariablePool):
        self.metadata = metadata

    def discover_tasks(self) -> Dict[str, Type[Task]]:
        """
        Find all tasks and import their object classes but do not init them yet
        """
        if self._tasks is not None:
            return self._tasks

        try:
            # TODO: Discover tasks
            pass
        except Exception as e:
            logger.critical("Failed to discover processes")
            raise e
        self._tasks = {}

        return self._tasks

    def load_task(self, task: Type[Task]) -> Task:
        metadata = copy.deepcopy(self.metadata)
        metadata.set_id(task.name)
        return task(metadata)


class BaseProcessManager(BaseTaskManager):

    """
    The following methods are identical, but we just need to change the return type
    """

    def discover_tasks(self) -> Dict[str, Type[Process]]:  # type: ignore[override]
        """
        The methods are identical, but we just need to change the return type
        """
        return super().discover_tasks()  # type: ignore[return-value]

    def load_task(self, task: Type[Process]) -> Process:  # type: ignore[override]
        return super().load_task(task)  # type: ignore[return-value]

    def main(self, task_list: List[NormalizedTaskSettings]):
        """
        Discover all processes, then load and execute the ones found in the task
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
