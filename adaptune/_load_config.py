import os
from collections import OrderedDict
from typing import OrderedDict as OrderedDictType

import alsaaudio
import commentjson
import numpy
from padasip import filters
from sounddevice import default

__all__ = ["hw_params", "filter_params", "domain", "default_filter", "dev"]

config: OrderedDict = OrderedDict()

with open(
    os.path.join(os.path.dirname(__file__), "data/config.json"), "r", encoding="UTF-8"
) as file:
    config = commentjson.load(file)

_params = config["hw_params"]
_params["frames"] = 1024

_fmtname: str = str(_params["formatname"])
if _fmtname.startswith("PCM"):  # for alsaaudio
    _params["formatname"] = getattr(alsaaudio, _params["formatname"])
else:  # for sounddevice
    _params["formatname"] = getattr(numpy, _params["formatname"])

_params["rate"] = int(_params["rate"]) if _params["rate"] else default.samplerate
_params["channels"] = int(_params["channels"])

hw_params: OrderedDictType = OrderedDict(_params)

filter_params: OrderedDictType = config["filter_params"]

domain: str = str(config["filter_domain"])

default_filter: filters.AdaptiveFilter = getattr(filters, config["filter_algo"])

dev: OrderedDictType[str, str] = config["devices"]
