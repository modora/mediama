from typing import List, Union, Dict, Any, TypedDict, Callable
from pathlib import Path


TaskSettings = List[Union[str, Dict[str, Any]]]


class NormalizedTaskSettings(TypedDict):
    name: str
    kwargs: dict
    id: str

Config = Dict[str, Any]


class NormalizedConfig(TypedDict):
    name: str
    pres: NormalizedTaskSettings
    sources: NormalizedTaskSettings
    posts: NormalizedTaskSettings
    key_sources: Dict[str, List[str]]
    aliases: Dict[str, List[str]]
    limit: int


def normalize_config(cfg: Config):
    default_config = load_config(Path(__file__).parent.joinpath("default_config.json"))
    for key, value in default_config:
        cfg.setdefault(key, value)

    normalize_pres(cfg["pres"])
    normalize_sources(cfg["sources"])
    normalize_posts(cfg["posts"])


def _base_normalizer(task_name: str) -> Callable:
    """
    Factory function that returns the task_normalization function
    """

    def normalize_tasks(tasks: List[Union[str, Dict[str, Any]]]):
        for i, task_ in enumerate(tasks):
            """
            Convert a string-specified task to a TaskSettings-dict
            Only the name is converted. All other keys are inheritted later
            """
            if isinstance(task_, str):
                task_ = {"name": task_}  # type: ignore[typeddict-item]

            """
            Only use the keys specific by the TaskSettings-dict
            Prefer the user-specified values; otherwise, use defaults
            """
            tasks[i] = {
                "name": task_["name"],
                "id": task_.get("id", f"{task_name}_{i}"),
                "kwargs": task_.get("kwargs", {}),
            }
        return tasks

    return normalize_tasks


def normalize_sources(sources: TaskSettings):
    _base_normalizer("src")(sources)


def normalize_pres(pres: TaskSettings):
    _base_normalizer("pre")(pres)


def normalize_posts(posts: TaskSettings):
    _base_normalizer("post")(posts)


def filter_duplicate_ids(tasks: List[NormalizedTaskSettings]):
    ids: set = set()
    for i, task in enumerate(tasks):
        id_ = task["id"]
        if id_ in ids:
            del tasks[i]
        else:
            ids.add(task["id"])
    return tasks


def load_config(path: Path) -> dict:
    raise NotImplementedError


def discover_config() -> Path:
    raise NotImplementedError
