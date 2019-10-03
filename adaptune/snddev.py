#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Tuple, Iterator
import numpy as np
import padasip
from . import core
from ._load_config import hw_params, dev, domain, default_filter
import sounddevice as sd


sd.default.samplerate = hw_params["rate"]
sd.default.dtype = (hw_params["formatname"], hw_params["formatname"])
sd.default.channels = (hw_params["channels"], hw_params["channels"])


class Source(sd.InputStream):
    frames: int
    is_running: bool = False

    def __init__(
        self,
        frames=hw_params["frames"],
        samplerate=None,
        blocksize=None,
        device=None,
        channels=None,
        dtype=None,
        latency=None,
        extra_settings=None,
        callback=None,
        finished_callback=None,
        clip_off=None,
        dither_off=None,
        never_drop_input=None,
        prime_output_buffers_using_stream_callback=None,
    ):
        self.frames = frames
        self.is_running = True
        super().__init__(
            samplerate=samplerate,
            blocksize=blocksize,
            device=device,
            channels=channels,
            dtype=dtype,
            latency=latency,
            extra_settings=extra_settings,
            callback=callback,
            finished_callback=finished_callback,
            clip_off=clip_off,
            dither_off=dither_off,
            never_drop_input=never_drop_input,
            prime_output_buffers_using_stream_callback=prime_output_buffers_using_stream_callback,
        )

    def read_as_iterable(
        self, frames: Optional[int] = None
    ) -> Iterator[Tuple[np.ndarray, bool]]:
        if frames:
            pass
        else:
            frames = self.frames
        while self.is_running:
            _readed = self.read(frames)
            yield _readed

    def stop_iteration(self):
        self.is_running = False
        self.stop()


class Sink(sd.OutputStream):

    def __init__(
        self,
        samplerate=None,
        blocksize=None,
        device=None,
        channels=None,
        dtype=None,
        latency=None,
        extra_settings=None,
        callback=None,
        finished_callback=None,
        clip_off=None,
        dither_off=None,
        never_drop_input=None,
        prime_output_buffers_using_stream_callback=None,
    ):
        super().__init__(
            samplerate=samplerate,
            blocksize=blocksize,
            device=device,
            channels=channels,
            dtype=dtype,
            latency=latency,
            extra_settings=extra_settings,
            callback=callback,
            finished_callback=finished_callback,
            clip_off=clip_off,
            dither_off=dither_off,
            never_drop_input=never_drop_input,
            prime_output_buffers_using_stream_callback=prime_output_buffers_using_stream_callback,
        )


def run(domain: str = domain, filter_: padasip.filters.AdaptiveFilter = default_filter, n: int = 1024, fs: int = hw_params["rate"]):
    MONITOR = Source(device=dev["monitor"])
    SPEAKER = Sink(device=dev["main"])
    MICRO = Source(device=dev["input"])
    
    adfilter = core.AdapTuner(domain=domain, default_filter=filter_, n=n, fs=fs)
