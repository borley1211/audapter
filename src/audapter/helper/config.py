import pathlib as _path
from os import getenv

import sounddevice as sd
from dynaconf import settings


def _set_samplerate():
    settings.load_file()
    settings.set('SOUND.SYSTEM.RATE', sd.default.samplerate)


# default values
MODULEPATH = _path.Path(__file__).parent.absolute()

CONFIGFILENAME = "audapter.toml"
DEFAULTS = "audapter.defaults.toml"
DEFAULTSABSPATH = (MODULEPATH / DEFAULTS).absolute()

CONFIGDIR = _path.Path(getenv("XDG_CONFIGDIR", "~/.config") + "/audapter").absolute()

LOGGERNAME = "audapter"
