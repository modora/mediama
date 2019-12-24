import logging.config
from logging import getLogger
from pathlib import Path

import gevent
import requests_cache

from .utils import dirs
from .config import NormalizedConfig, discover_config, load_config
from .metadata import VariablePool, Metadata
from .managers import PreProcessManager, SourceManager, PostProcessManager


logger = getLogger(__name__)


def configure_logger(cfg: NormalizedConfig):
    logging.config.dictConfig(cfg["log"])


def configure_requests_cache(cfg: NormalizedConfig):
    # Check if caching is enabled
    config = cfg["cache"]
    if not cfg["cache"]:
        return

    path = Path(config["path"])
    if not path.is_absolute():
        path = Path(dirs.user_data_dir) / (path or "cache")

    requests_cache.install_cache(path)


def execute_process(
    mgr, task, name: str = "main", set_metadata: bool = True
) -> Metadata:
    try:
        logger.debug(f"Loading {task.name} with id: {task.id}")
        t = mgr.load_task(task)
    except Exception as e:
        logger.error(f"Error while loading {task.name}: {e}")
        raise e

    try:
        logger.debug(f"Executing {task.id} with {task.kwargs}")
        id_ = task.id if set_metadata else None
        return mgr.execute_task(t, id_=id_, name=name, **task.kwargs)
    except Exception as e:
        logger.error(f"Error while executing {task.id}: {e}")
        raise e


def execute_disambiguator(mgr, ranking, name, cfg):
    try:
        func = getattr(mgr, name)
        idx = func(ranking)
    except Exception as e:
        logger.debug("Automatic disambiguation failed")
        if not cfg["prompt"]:
            raise e
        idx = int(input())
    return ranking[idx].name


def main(filepaths: list, cfg: NormalizedConfig):
    # Note that the logger is not yet loaded since it depends on the cfg
    # Import the config if not given
    if not cfg:
        cfg_path = discover_config()
        cfg = load_config(cfg_path)

    # Configure the logger
    configure_logger(cfg)
    # Log missed functions
    logger.debug(f"Config path loaded: {cfg_path}")
    logger.debug(f"Config settings: {cfg}")
    logger.debug(f"File args: {[str(file) for file in filepaths]}")

    # Setup requests cache
    configure_requests_cache(cfg)

    # Setup the varpool
    logger.debug("Setting up variable pool")
    varpool = VariablePool(cfg, id_="mediama")
    varpool["filepaths"] = filepaths

    # Initialize the managers
    logger.debug("Setting up managers")
    try:
        pre_mgr = PreProcessManager(cfg, metadata=varpool)
        src_mgr = SourceManager(cfg, metadata=varpool)
        post_mgr = PreProcessManager(cfg, metadata=varpool)
    except Exception as e:
        logger.critical(f"Failed to setup managers: {e}")
        raise e

    # Discover the tasks early to catch errors early
    logger.debug("Discovering tasks")
    try:
        pre_mgr.discover_tasks()
        src_mgr.discover_tasks()
        post_mgr.discover_tasks()
    except Exception as e:
        logger.critical(f"Failed to discover tasks: {e}")
        raise e

    # Begin execution
    # Preprocess
    logger.debug("Executing preprocess tasks")
    for task in cfg["pres"]:
        try:
            execute_process(pre_mgr, task)
        except Exception:
            # The errors are captured in execute_process
            continue

    # Source
    # Fetch series metadata
    logger.debug("Fetching series metadata")
    src_ids = [task.id for task in cfg["sources"]]
    src_wts = [1 for task in cfg["sources"]]  # TODO: RESERVED FOR FUTURE
    tasks = [
        gevent.spawn(execute_process, src_mgr, task, name="fetch_series")
        for task in cfg["sources"]
    ]
    gevent.joinall(tasks, cfg["timeout"])
    # Collect results
    rankings = zip(src_ids, [task.value for task in tasks])
    # Aggregate series metadata
    logger.debug("Aggregating series metadata")
    ranking = src_mgr.aggregate(zip(*rankings, src_wts))
    # Disambiguate
    logger.debug("Disambiguating series")
    try:
        name = execute_disambiguator(src_mgr, ranking, "disambiguate_series", cfg)
    except Exception as e:
        # Logging occurs in the executor
        raise e
    for id_, ranking in rankings:
        data = tuple(filter(lambda result: result["name"] == name, ranking))[0]
        varpool.set_(data, id_)

    # Fetch episode metadata
    logger.debug("Fetching episode metadata")
    tasks = [
        gevent.spawn(execute_process, src_mgr, task, name="fetch_episodes")
        for task in cfg["sources"]
    ]
    gevent.joinall(tasks, cfg["timeout"])
    # Aggregate episode metadata
    logger.debug("Aggregating episode metadata")
    ranking = src_mgr.aggregate(
        [
            task.value if isinstance(tasks.value, list) else [task.value]
            for task in tasks
        ]
    )

    # Disambiguate
    logger.debug("Disambiguating episodes")
    try:
        data = execute_disambiguator(src_mgr, ranking, "disambiguate_episodes", cfg)
    except Exception as e:
        # Logging occurs in the executor
        raise e
    logger.debug(f"Episode metadata: {data}")

    # Postprocess
    logger.debug("Executing postprocess tasks")
    for task in cfg["pres"]:
        try:
            execute_process(post_mgr, task)
        except Exception:
            # The errors are captured in execute_process
            continue
