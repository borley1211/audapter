# -*- coding: utf-8 -*-
from typing import Optional, Union

import numpy as np
import padasip
import sounddevice as sd

from . import core
from ._load_config import default_filter, dev, domain, hw_params


Numeric = Union[int, float]


hw_params["rate"] = sd.default.samplerate
sd.default.dtype = (hw_params["formatname"], hw_params["formatname"])
sd.default.channels = (hw_params["channels"], hw_params["channels"])
sd.default.never_drop_input = True
sd.default.prime_output_buffers_using_stream_callback = True


class TuningStream(object):
    def __init__(self, target: str = dev["target"], field_meter: str = dev["field_meter"], internal_monitor: str = dev["internal_monitor"], domain: str = domain, filter_: padasip.filters.AdaptiveFilter = default_filter, frames: int = 1024, fs: Optional[int] = None):
        if fs:
            sd.default.samplerate = fs
        self.TargetStream = sd.Stream(device=target)
        self.FieldMeter = sd.Stream(device=field_meter)
        self.InternalMonitor = sd.Stream(device=internal_monitor)
        
        self.Tuner = core.AdapTuner(domain, default_filter, frames, sd.default.samplerate)


def _callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata


def pass_thru(repeat: Numeric, duration: Numeric, micro: str = dev["field_meter"], pci: str = dev["target"]):
    global _callback
    
    with sd.Stream(device=(micro, pci), callback=_callback):
        (sd.sleep(int(duration * 1000)) for n in range(repeat))


if __name__ == "__main__":
    pass_thru(repeat=5, duration=1)
