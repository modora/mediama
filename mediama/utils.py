from types import ModuleType
from typing import Generator, Generic, Any, Union, List
from pathlib import Path
import sys
from importlib import import_module

from appdirs import AppDirs  # type: ignore[import]

from .__about__ import __author__

dirs = AppDirs("mediama", __author__)


def get_project_root() -> Path:
    """
    Get the path of the project root directory
    :returns: project root dir
    """
    return Path(__file__).parent.parent


def discover_modules(search_dir: Path) -> Generator[Path, None, None]:
    """
    Return a generator of paths to python modules in the specified directory
    """
    return (
        f
        for f in search_dir.iterdir()
        if (f.is_file() and f.suffix == ".py")
        or (f.is_dir() and "__init__.py" in f.iterdir())
    )


"""
Untested, too hard to write test without hackery
"""


def import_module_from_path(module: Path) -> ModuleType:
    # attempt to import the file/package and raise error if fails
    sys.path.insert(0, str(module.parent))
    try:
        return import_module(module.stem)
    except Exception as e:
        raise e
    finally:
        sys.path.pop(0)  # lets not pollute sys.path!!


"""
Untested, too hard to write test without hackery
"""


def unload_module(module: Union[str, ModuleType]):
    """
    unload the imported module
    :param module: either the module or name of the module
    """
    try:
        name: str
        if isinstance(module, ModuleType):
            name = module.__name__
        else:
            name = module
        del sys.modules[name]
    except KeyError:
        # module was never loaded so dont do anything
        pass


# The "Any" of Generator[Any, None, None] should be the type of cls
def get_subclasses_from_module(
    module: ModuleType, cls: Any
) -> Generator[Any, None, None]:
    """
    Find all subclasses from the specified module name
    """
    for obj_name in dir(module):
        try:
            obj = getattr(module, obj_name)
            # We want strict subclasses. Make sure ignore the imported class
            if issubclass(obj, cls) and obj is not cls:
                yield obj
        except TypeError:
            # obj is not a class-type
            pass


def normalize_ranking(ranking: List, num_rank):
    raise NotImplementedError


def merge_ranking_metadata(names: List[str], metadata: List):
    raise NotImplementedError


def rank_aggregation(ranks, weights):
    raise NotImplementedError
