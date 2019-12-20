from typing import List, Union, Dict, Any, TypedDict
from pathlib import Path

class Task(TypedDict):
    name: str
    kwargs: dict
    id: str

class Config(TypedDict):
    name: str
    pre: List[Union[str, Task]]
    sources: List[Union[str, Task]]
    post: List[Union[str, Task]]
    key_sources: Dict[str, List[str]]
    alias: Dict[str, List[str]]
    limit: int

def normalize_config(cfg: Config):
    cfg.setdefault("name", "unnamed profile")
    cfg.setdefault("sources", [])
    cfg.setdefault("key_sources", {})
    cfg.setdefault("alias", {})
    cfg.setdefault("limit", 5)
    cfg.setdefault("pre", [])
    cfg.setdefault("post", [])

    normalize_pres(cfg["pres"])
    normalize_sources(cfg["sources"])
    normalize_posts(cfg["posts"])



def _base_normalizer(task: str):
    def normalize_tasks(tasks: List[Union[str,Task]]):
        for i, task_ in enumerate(tasks):
            if isinstance(task_, str):
                task_ = {"name": task_}

            tasks[i] = {
                "name": task_["name"],
                "id": task_.get("id", f"{task}_{i}"),
                "kwargs": task_.get("kwargs", {}),
            }
    
    return normalize_tasks


def normalize_sources(sources: List[Union[str, Task]]):
    _base_normalizer('src')(sources)

def normalize_pres(pres: List[Union[str, Task]]):
    _base_normalizer('pre')(pres)

def normalize_posts(posts: List[Union[str, Task]]):
    _base_normalizer('post')(posts)

def load_config(path: Path) -> dict:
    raise NotImplementedError

def discover_config():
    raise NotImplementedError
