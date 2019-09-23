import os
from collections import OrderedDict

import alsaaudio
import commentjson
import numpy
from padasip import filters

__all__ = ["hw_params", "filter_params", "domain", "default_filter", "dev"]

config: OrderedDict = OrderedDict()

with open(
    os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="UTF-8"
) as file:
    config = commentjson.load(file)

_params = config["hw_params"]

_fmtname: str = str(_params["formatname"])
if _fmtname.startswith("PCM"):  # for alsaaudio
    _params["formatname"] = getattr(alsaaudio, _params["formatname"])
else:  # for sounddevice
    _params["formatname"] = getattr(numpy, _params["formatname"])

hw_params: OrderedDict = OrderedDict(_params)

filter_params = config["filter_params"]

domain = config["filter_domain"]

default_filter = getattr(filters, config["filter_algo"])

dev = config["devices"]
