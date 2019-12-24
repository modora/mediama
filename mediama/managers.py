from typing import Set, List, Dict, Any, Type, TypedDict, Optional, Tuple, Iterable
import copy
from logging import getLogger
from pathlib import Path

from .utils import (
    import_module_from_path,
    unload_module,
    get_subclasses_from_module,
    discover_modules,
    dirs,
    rank_aggregation,
    merge_ranking_metadata,
    normalize_ranking,
)
from .metadata import VariablePool, SourceMetadata, Metadata
from .config import NormalizedTaskSettings, NormalizedConfig

logger = getLogger(__name__)


class Task:
    pass


class Process(Task):
    def main(self, **kwargs: Any) -> Metadata:
        raise NotImplementedError


class PreProcess(Process):
    pass


class PostProcess(Process):
    pass


class Source(Task):
    def fetch_series(self, **kwargs: Any) -> List[SourceMetadata]:
        raise NotImplementedError

    def fetch_episodes(self, **kwargs: Any) -> List[SourceMetadata]:
        raise NotImplementedError


class BaseTaskManager:
    _tasks: Optional[Dict[str, Type[Task]]] = None

    def __init__(
        self, cfg: NormalizedConfig, metadata: VariablePool,
    ):
        self.metadata = metadata

        # plugin search directory from lowest priority to highest
        # if no search dirlist is provided use the default
        self.search_dirs = cfg["search_dirs"] or [Path(d) / "plugins" for d in (dirs.site_data_dir, dirs.user_data_dir)]  # type: ignore[has-type]

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
        return task(self.metadata)

    def execute_task(
        self,
        task: Task,
        id_: Optional[str] = None,
        name: Optional[str] = "main",
        **kwargs: Any,
    ) -> Metadata:
        func = getattr(task, name)
        data = func(**kwargs)
        if id_:
            self.metadata.set(data, id_=id_)
        return data


class PreProcessManager(BaseTaskManager):
    def discover_tasks(self) -> Dict[str, PreProcess]:
        return self._discover_tasks(PreProcess)


class PostProcessManager(BaseTaskManager):
    def discover_tasks(self) -> Dict[str, PostProcess]:
        return self._discover_tasks(PostProcess)


class SourceManager(BaseTaskManager):
    def __init__(self, cfg: NormalizedConfig, metadata: Metadata):
        super().__init__(cfg, metadata)
        self.num_ranks = cfg["ranks"]

    def discover_tasks(self) -> Dict[str, Source]:
        return self._discover_tasks(Source)

    def execute_task(
        self, task: Task, name: str, id_: Optional[str] = None, **kwargs: Any,
    ) -> List[Metadata]:
        if name == "fetch_series":
            return normalize_ranking(
                super().execute_task(
                    task, id_, name, **{"num_ranks": self.num_ranks, **kwargs}
                ),
                self.num_ranks,
            )
        elif name == "fetch_episodes":
            return super().execute_task(task, id_, name, **kwargs)
        else:
            raise AttributeError

    def aggregate(
        self, *rankings: Iterable[Tuple(str, float, SourceMetadata)]
    ) -> List[SourceMetadata]:
        name_rankings = [
            [result.name for result in ranking] for _, ranking, _ in rankings
        ]
        weights = [weight for _, _, weight in rankings]
        names = rank_aggregation(name_rankings, weights)

        return merge_ranking_metadata(
            names, [(id_, ranking) for id_, ranking, _ in rankings]
        )

    def disambiguate_series(self, ranking: List[SourceMetadata]) -> SourceMetadata:
        raise NotImplementedError

    def disambiguate_episodes(self, ranking: List[SourceMetadata]) -> SourceMetadata:
        raise NotImplementedError
