import logging as _log
import pathlib as _path
import shutil as _sh
from typing import Optional, Union

import fire

from . import CONFIGFILENAME, DEFAULTSABSPATH
from .helper.config import settings
from .helper.logger import logger


class Cli(object):
    """
    Adaptive Audio Processor
    """
    path: Union[str, _path.Path]
    name: str
    cfgfile: Union[str, _path.Path]

    def __init__(self, loglevel: Optional[str] = 'INFO'):
        logger.setLevel(getattr(_log, str(loglevel.upper())))

    def init(self, name: Optional[str] = None, path: Optional[Union[str, _path.Path]] = "."):
        self.path = _path.Path(path)
        self.name = name or self.path.parent.name
        self.cfgfile = (self.path + "/" + CONFIGFILENAME).absolute()

        if self.cfgfile.exists():
            raise FileExistsError(f'{self.cfgfile} already exists.')

        _sh.copy(DEFAULTSABSPATH, self.path)
        return settings


if __name__ == "__main__":
    fire.Fire(Cli)
