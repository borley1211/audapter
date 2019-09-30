#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from . import core
from ._load_config import hw_params, dev
import sounddevice as sd


sd.default.samplerate = hw_params["rate"]
sd.default.dtype = (hw_params["formatname"], hw_params["formatname"])
sd.default.channels = (hw_params["channels"], hw_params["channels"])


class Source(sd.InputStream):
    frames: int
    
    def __init__(self, frames=hw_params["frames"], samplerate=None, blocksize=None, device=None, channels=None, dtype=None, latency=None, extra_settings=None, callback=None, finished_callback=None, clip_off=None, dither_off=None, never_drop_input=None, prime_output_buffers_using_stream_callback=None):
        self.frames = frames
        super().__init__(samplerate=samplerate, blocksize=blocksize, device=device, channels=channels, dtype=dtype, latency=latency, extra_settings=extra_settings, callback=callback, finished_callback=finished_callback, clip_off=clip_off, dither_off=dither_off, never_drop_input=never_drop_input, prime_output_buffers_using_stream_callback=prime_output_buffers_using_stream_callback)
