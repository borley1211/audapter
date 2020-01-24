import pathlib as _path
import shutil as _sh
from typing import Optional, Union

import fire

from .helper.config import CONFIGFILENAME, DEFAULTSABSPATH, settings


class Cli(object):
    """
    Adaptive Audio Processor
    """
    path: Union[str, _path.Path]
    name: str
    cfgfile: Union[str, _path.Path]

    def init(self, name: Optional[str] = None, path: Optional[Union[str, _path.Path]] = "."):
        self.path = _path.Path(path)
        self.name = name or self.path.parent.name
        self.cfgfile = (self.path + "/" + CONFIGFILENAME).absolute()

        if self.cfgfile.exists():
            raise FileExistsError(f'{self.cfgfile} already exists.')

        _sh.copy(DEFAULTSABSPATH, self.path)
        return settings

    @staticmethod
    def run(method: Optional[str] = "nlms"):
        return method


def main():
    fire.Fire(Cli)


if __name__ == "__main__":
    main()
