import pathlib as _path
import shutil as _sh
from typing import Optional, Union

from fire import Fire

from . import CONFIGFILENAME, DEFAULTSABSPATH
from .helper.logger import logger, _log


class CommandLineInterface:
    """
    Adaptive Audio Processor
    """
    path: Union[str, _path.Path]
    name: str
    cfgfile: Union[str, _path.Path]

    def __init__(self, loglevel: Optional[str] = 'INFO'):
        logger.setLevel(getattr(_log, loglevel.upper()))

    def init(self, name: Optional[str] = None, path: Optional[str, _path.Path] = "."):
        self.path = _path.Path(path)
        self.name = name or self.path.parent.name
        self.cfgfile = (self.path / CONFIGFILENAME).absolute()

        if self.cfgfile.exists():
            raise FileExistsError(f'{self.cfgfile} already exists.')

        _sh.copy(DEFAULTSABSPATH, self.path)


if __name__ == "__main__":
    Fire(CommandLineInterface)
