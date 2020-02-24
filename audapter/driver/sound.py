# -*- coding: utf-8 -*-

import sounddevice as sd

from ..domain.model import FilterModel
from ..driver import filter_driver
from ..helper.config import load_settings

settings = load_settings()


def setup_sounddevice(settings):
    sd.default.dtype = settings.get("SOUND.system.data_format")
    sd.default.channels = (
        settings.get("SOUND.system.channels.input"),
        settings.get("SOUND.system.channels.output"),
    )
    sd.default.never_drop_input = settings.get("SOUND.sounddevice.never_drop_input")
    sd.default.prime_output_buffers_using_stream_callback = settings.get(
        "SOUND.sounddevice.prime_output_buffers_using_stream_callback"
    )


def callback_for_test(indata, outdata, frames, time, status):
    print(status) if status else print(f"PASSED in {time}")
    outdata[:] = indata


def pass_thru(
    repeat,
    duration,
    system=settings.get("SOUND.target.system"),
    target=settings.get("SOUND.target.main"),
):
    global callback_for_test, settings
    
    setup_sounddevice(settings)

    with sd.Stream(device=(system, target), callback=callback_for_test):
        (sd.sleep(int(duration * 1000)) for n in range(repeat))

    return None


if __name__ == "__main__":
    pass_thru(repeat=5, duration=1)
