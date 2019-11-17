# -*- coding: utf-8 -*-
from typing import Optional

import numpy as np
import padasip
import sounddevice as sd

from . import filter_driver
from ..helper import config, types


config.SOUND.system.rate = sd.default.samplerate
sd.default.dtype = config.SOUND.system.data_format
sd.default.channels = (config.SOUND.system.channels.input, config.SOUND.system.channels.output)
sd.default.never_drop_input = config.SOUND.sounddevice.never_drop_input
sd.default.prime_output_buffers_using_stream_callback = config.SOUND.sounddevice.prime_output_buffers_using_stream_callback


class TuningStream(object):
    def __init__(self, target: str = config.SOUND.target["main"], field_meter: str = config.SOUND.target["field_meter"], internal_monitor: str = config.SOUND.target["internal_monitor"], domain: str = domain, filter_: padasip.filters.AdaptiveFilter = default_filter, frames: int = 1024, fs: Optional[int] = None):
        if fs:
            sd.default.samplerate = fs
        self.TargetStream = sd.Stream(device=target)
        self.FieldMeter = sd.Stream(device=field_meter)
        self.InternalMonitor = sd.Stream(device=internal_monitor)
        
        self.Tuner = filter.AdapTuner(domain, default_filter, frames, sd.default.samplerate)


def _callback(indata, outdata, frames, time, status):
    print(status) if status else print(f"PASSED in {time}")
    outdata[:] = indata


def pass_thru(repeat, duration, micro=config.SOUND.target["field_meter"], pci=config.SOUND.target["target"]):
    global _callback
    
    with sd.Stream(device=(micro, pci), callback=_callback):
        (sd.sleep(int(duration * 1000)) for n in range(repeat))
    
    return None


if __name__ == "__main__":
    pass_thru(repeat=5, duration=1)
