from typing import Set, List, Dict, Any, Type, TypedDict
import copy

from .metadata import VariablePool
from .config import NormalizedTaskSettings

Rankings = List[Dict[str, Any]]


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
    def __init__(self, metadata: VariablePool):
        self.metadata = metadata

    def discover_tasks(self) -> List[Type[Task]]:
        """
        Find all tasks and import their object classes but do not init them yet
        """
        raise NotImplementedError

    def load_task(self, task: Type[Task]) -> Task:
        metadata = copy.deepcopy(self.metadata)
        metadata.set_id(task.name)
        return task(metadata)


class BaseProcessManager(BaseTaskManager):

    """
    The following methods are identical, but we just need to change the return type
    """

    def discover_tasks(self) -> List[Type[Process]]:  # type: ignore[override]
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
        try:
            processes = self.discover_tasks()
        except Exception as e:
            # TODO: Log critical
            raise e
        process_names: Set[str] = set()
        for process in processes:
            try:
                if process.name is None:
                    raise AttributeError(f"Process name missing: ${process}")
                process_names.add(process.name)
            except AttributeError as e:
                # TODO: log error
                pass

        for task in task_list:
            # mypy typeddict bug
            if task.name not in process_names:  # type: ignore[attr-defined]
                # TODO: log warning
                continue

            try:
                process_instance = self.load_task(process)
            except Exception as e:
                # TODO: log error
                pass

            try:
                # mypy typeddict bug
                process_instance.main(**task.kwargs)  # type: ignore[attr-defined]
            except Exception as e:
                # TODO: log error
                pass


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
