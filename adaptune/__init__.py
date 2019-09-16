__version__ = '0.1.0'

import os

import alsaaudio as alsa
import commentjson
import numpy as np
from padasip import padasip as pa

from . import core, passalsa, preferences
from ._monitor import monitor

with open(
    os.path.join(os.path.dirname(__file__), "config.json"),
        'r', encoding='UTF-8') as file:
    config = commentjson.load(file)

params = config["params"]
if "PCM" in params["formatname"]:  # for alsaaudio
    params["formatname"] = eval("alsa." + params["formatname"])
else:  # for sounddevice
    params["formatname"] = eval("np." + params["formatname"])

filter_params = config["filter_params"]

domain = config["filter_domain"]

default_filter = eval("pa.filters." + config["filter_algo"])

dev = config["devices"]


__all__ = [
    'core',
    'passalsa',
    'monitor',
    'dev',
    'params',
    'filter_params',
    'domain',
    'default_filter',
    'preferences']
