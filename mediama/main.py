from .config import NormalizedConfig

from logging import getLogger

logger = getLogger(__name__)


def main(filelist: list, cfg: NormalizedConfig):
    """
    Init, run premanager, run sourcesManager, run postManager
    """
    raise NotImplementedError


def init():
    """
    Setup root logger, setup varpool
    """
    raise NotImplementedError
