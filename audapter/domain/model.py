from dataclasses import dataclass as _dataclass

from ..helper import config
from . import freq, time


if config.settings.get("DOMAIN") == "freq":
    FilterModel = freq.get_filter()

elif config.settings.get("DOMAIN") == "time":
    FilterModel = time.get_filter()

else:
    raise ValueError
