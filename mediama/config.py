from typing import List, Union, Dict, Any, TypedDict
from pathlib import Path


class Task(TypedDict):
    name: str
    kwargs: dict
    id: str


class Config(TypedDict):
    name: str
    pres: List[Union[str, Task]]
    sources: List[Union[str, Task]]
    posts: List[Union[str, Task]]
    key_sources: Dict[str, List[str]]
    aliases: Dict[str, List[str]]
    limit: int


def normalize_config(cfg: Config):
    cfg.setdefault("name", "unnamed profile")
    cfg.setdefault("sources", [])
    cfg.setdefault("key_sources", {})
    cfg.setdefault("aliases", {})
    cfg.setdefault("limit", 5)
    cfg.setdefault("pres", [])
    cfg.setdefault("posts", [])

    normalize_pres(cfg["pres"])
    normalize_sources(cfg["sources"])
    normalize_posts(cfg["posts"])


def _base_normalizer(task: str):
    def normalize_tasks(tasks: List[Union[str, Task]]):
        for i, task_ in enumerate(tasks):
            """
            Convert a string-specified task to a Task-dict
            Only the name is converted. All other keys are inheritted later
            """
            if isinstance(task_, str):
                task_ = {"name": task_}  # type: ignore[typeddict-item]

            """
            Only use the keys specific by the Task-dict
            Prefer the user-specified values; otherwise, use defaults
            """
            tasks[i] = {
                "name": task_["name"],
                "id": task_.get("id", f"{task}_{i}"),
                "kwargs": task_.get("kwargs", {}),
            }
        return tasks

    return normalize_tasks


def normalize_sources(sources: List[Union[str, Task]]):
    return _base_normalizer("src")(sources)


def normalize_pres(pres: List[Union[str, Task]]):
    return _base_normalizer("pre")(pres)


def normalize_posts(posts: List[Union[str, Task]]):
    return _base_normalizer("post")(posts)


def filter_duplicate_ids(tasks: List[Task]):
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


def discover_config():
    raise NotImplementedError
