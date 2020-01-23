import pathlib as _pathlib

from os import getenv

# default values
MODULEPATH = _pathlib.Path(__file__).parent.absolute()

CONFIGFILENAME = "audapter.toml"
DEFAULTS = "audapter.defaults.toml"

CONFIGDIR = getenv("XDG_CONFIGDIR", "~/.config") / "audapter"

LOGGERNAME = "audapter"
