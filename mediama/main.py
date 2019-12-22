from .config import NormalizedConfig, discover_config, load_config

import logging.config
from logging import getLogger

logger = getLogger(__name__)

def init():
    """
    Setup root logger, setup varpool, discover plugins
    """
    raise NotImplementedError

def configure_logger(cfg: NormalizedConfig):
    logging.config.dictConfig(cfg['log'])

def main(filelist: list, cfg: NormalizedConfig):
    """
    Init, run premanager, run sourcesManager, run postManager
    """
    cfg_path = discover_config()
    cfg = load_config(cfg_path)

    configure_logger(cfg)
    logger.debug(f"Config path loaded: {cfg_path}")
    logger.debug(f"Config settings: {cfg}")

    raise NotImplementedError
