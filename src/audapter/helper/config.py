"""
Configuration module
"""
import pathlib as _path
from os import getenv

import sounddevice as sd
from dynaconf import LazySettings


# default values
MODULEPATH = _path.Path(__file__).parent.parent.absolute()

CONFIGFILENAME = "audapter.toml"
DEFAULTS = "audapter.defaults.toml"
DEFAULTSABSPATH = (MODULEPATH / DEFAULTS).absolute()

CONFIGDIR = _path.Path(getenv("XDG_CONFIGDIR", "~/.config") + "/audapter").absolute()

LOGGERNAME = "audapter"

settings = LazySettings(INCLUDES_FOR_DYNACONF=str(DEFAULTSABSPATH))
settings.set('SOUND.SYSTEM.RATE', sd.default.samplerate)
