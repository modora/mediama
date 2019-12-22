import logging.config
from logging import getLogger

import gevent

from .config import NormalizedConfig, discover_config, load_config
from .metadata import VariablePool
from .managers import PreProcessManager, SourceManager, PostProcessManager


logger = getLogger(__name__)


def configure_logger(cfg: NormalizedConfig):
    logging.config.dictConfig(cfg["log"])


def execute_process(mgr, task, name: str = "main"):
    try:
        logger.debug(f"Loading {task.name} with id: {task.id}")
        t = mgr.load_task(task)
    except Exception as e:
        logger.error(f"Error while loading {task.name}: {e}")
        raise e

    try:
        logger.debug(f"Executing {task.id} with {task.kwargs}")
        func = getattr(t, name)
        return func(task.kwargs)
    except Exception as e:
        logger.error(f"Error while executing {task.id}: {e}")
        raise e

def execute_disambiguator(mgr, ranking, name, cfg):
    try:
        func = getattr(mgr, name)
        idx = func(ranking)
    except Exception as e:
        logger.debug("Automatic disambiguation failed")
        if not cfg['prompt']:
            raise e
        idx = int(input())
    return ranking[idx]

def main(filepaths: list, cfg: NormalizedConfig):
    # Import the config
    # Note that the logger is not yet loaded since it depends on the cfg
    cfg_path = discover_config()
    cfg = load_config(cfg_path)

    # Configure the logger
    configure_logger(cfg)
    # Log missed functions
    logger.debug(f"Config path loaded: {cfg_path}")
    logger.debug(f"Config settings: {cfg}")
    logger.debug(f"File args: {[str(file) for file in filepaths]}")

    # Setup the varpool
    logger.debug("Setting up variable pool")
    varpool = VariablePool(cfg, id_="mediama")
    varpool['filepaths'] = filepaths

    # Initialize the managers
    logger.debug("Setting up managers")
    try:
        search_dirs = cfg.get("search_dirs", None)
        pre_mgr = PreProcessManager(metadata=varpool, search_dirs=search_dirs)
        src_mgr = SourceManager(metadata=varpool, search_dirs=search_dirs)
        post_mgr = PreProcessManager(metadata=varpool, search_dirs=search_dirs)
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
    tasks = [
        gevent.spawn(execute_process, src_mgr, task, name="fetch_series")
        for task in cfg["sources"]
    ]
    gevent.joinall(tasks, cfg["timeout"])
    # Aggregate series metadata
    logger.debug("Aggregating series metadata")
    ranking = src_mgr.aggregate(
        [task.value for task in tasks if isinstance(tasks.value, list)]
    )
    # Disambiguate
    logger.debug("Disambiguating series")
    try:
        data = execute_disambiguator(src_mgr, ranking, 'disambiguate_series', cfg)
    except Exception as e:
        # Logging occurs in the executor
        raise e
    logger.debug(f"Series metadata: {data}")
    # Fetch series metadata
    logger.debug("Fetching episode metadata")
    tasks = [
        gevent.spawn(execute_process, src_mgr, task, name="fetch_episodes")
        for task in cfg["sources"]
    ]
    gevent.joinall(tasks, cfg["timeout"])
    # Aggregate episode metadata
    logger.debug("Aggregating episode metadata")
    ranking = src_mgr.aggregate(
        [task.value for task in tasks if isinstance(tasks.value, list)]
    )
    # Disambiguate
    logger.debug("Disambiguating episodes")
    try:
        data = execute_disambiguator(src_mgr, ranking, 'disambiguate_episodes', cfg)
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
