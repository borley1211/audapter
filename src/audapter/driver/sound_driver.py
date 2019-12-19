# -*- coding: utf-8 -*-
from typing import Optional

import numpy as np
import sounddevice as sd

from ..domain.model import FilterModel
from ..driver import filter_driver
from ..helper import types
from ..helper.load_config import settings
from ..interface.driver.sound_driver import SoundDriverABC

sd.default.dtype = settings.get("SOUND.system.data_format")
sd.default.channels = (
    settings.get("SOUND.system.channels.input"),
    settings.get("SOUND.system.channels.output"),
)
sd.default.never_drop_input = settings.get("SOUND.sounddevice.never_drop_input")
sd.default.prime_output_buffers_using_stream_callback = settings.get(
    "SOUND.sounddevice.prime_output_buffers_using_stream_callback"
)


class SoundDriver(SoundDriverABC):
    def __init__(
        self,
        device_dict=settings.get("SOUND.target"),
        domain=settings.get("FILTER.domain"),
        filter_cls=FilterModel,
        frames=1024,
    ):
        self.TargetStream = sd.Stream(device=device_dict["target"])
        self.FieldMeter = sd.Stream(device=device_dict["field_meter"])
        self.InternalMonitor = sd.Stream(device=device_dict["internal_monitor"])

        self.Tuner = filter_driver.FilterDriver(
            domain, filter_cls, frames, sd.default.samplerate
        )


def _callback(indata, outdata, frames, time, status):
    print(status) if status else print(f"PASSED in {time}")
    outdata[:] = indata


def pass_thru(
    repeat,
    duration,
    micro=settings.get("SOUND.target.field_meter"),
    pci=settings.get("SOUND.target.target"),
):
    global _callback

    with sd.Stream(device=(micro, pci), callback=_callback):
        (sd.sleep(int(duration * 1000)) for n in range(repeat))

    return None


if __name__ == "__main__":
    pass_thru(repeat=5, duration=1)
