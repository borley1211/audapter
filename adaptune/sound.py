#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Iterator, Optional, Tuple

import numpy as np
import padasip
import sounddevice as sd

import adaptune.core as core
from adaptune._load_config import default_filter, dev, domain, hw_params

sd.default.samplerate = hw_params["rate"]
sd.default.dtype = (hw_params["formatname"], hw_params["formatname"])
sd.default.channels = (hw_params["channels"], hw_params["channels"])
sd.default.prime_output_buffers_using_stream_callback = True


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


class IterableStream(sd.Stream):
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


def run(
    domain: str = domain,
    filter_: padasip.filters.AdaptiveFilter = default_filter,
    n: int = 1024,
    fs: int = hw_params["rate"],
):
    MONITOR = IterableStream(device=dev["monitor"])
    SPEAKER = IterableStream(device=dev["main"])
    MICRO = IterableStream(device=dev["input"])

    res = True

    adfilter = core.AdapTuner(domain=domain, default_filter=filter_, n=n, fs=fs)

    try:
        for desired, recorded in zip(
            MONITOR.read_as_iterable(), MICRO.read_as_iterable()
        ):
            x_out, err, w_c = adfilter.tune(desired, recorded)
            SPEAKER.write(x_out)
    except KeyboardInterrupt:
        res = False

    return res


def pass_thru(input_=dev["input"], output_=dev["main"]):
    MICRO = IterableStream(device=input_)
    SPEAKER = IterableStream(device=output_)

    res = True

    try:
        for recorded in MICRO.read_as_iterable():
            SPEAKER.write(recorded)
    except KeyboardInterrupt:
        res = False

    return res


if __name__ == "__main__":
    pass_thru()
