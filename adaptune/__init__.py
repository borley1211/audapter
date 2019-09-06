__version__ = '0.1.0'

from . import core, passalsa
from ._monitor import monitor
import alsaaudio as alsa
from padasip import padasip as pa
import os
import commentjson


with open(
    os.path.join(os.path.dirname(__file__), "params.json"), 'r', encoding='UTF-8'
) as file:
    config = commentjson.load(file)

params = config["params"]
params["formatname"] = eval("alsa." + params["formatname"])

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
    'default_filter']
