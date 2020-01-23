import pathlib as _pathlib

from os import getenv

# default values
MODULEPATH = _pathlib.Path(__file__).parent.absolute()

CONFIGFILENAME = "audapter.toml"
DEFAULTS = "audapter.defaults.toml"
DEFAULTSABSPATH = (MODULEPATH / DEFAULTS).absolute()

CONFIGDIR = _pathlib.Path(getenv("XDG_CONFIGDIR", "~/.config") + "/audapter").absolute()

LOGGERNAME = "audapter"
