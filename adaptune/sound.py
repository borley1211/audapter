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
sd.default.never_drop_input = True
sd.default.prime_output_buffers_using_stream_callback = True


class IterableStream(sd.Stream):
    frames: int
    is_running: bool = False

    def __init__(
        self,
        frames,
        *args,
        **kwargs,
    ):
        self.frames = frames
        self.is_running = True
        super(IterableStream, self).__init__(*args, **kwargs)

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
    MONITOR = IterableStream(frames=n, device=dev["monitor"])
    SPEAKER = IterableStream(frames=n, device=dev["main"])
    MICRO = IterableStream(frames=n, device=dev["input"])

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


def pass_thru(n: int = 1024, input_=dev["input"], output_=dev["main"]):
    MICRO = IterableStream(frames=n, device=input_)
    SPEAKER = IterableStream(frames=n, device=output_)

    res = True

    try:
        for recorded in MICRO.read_as_iterable():
            SPEAKER.write(recorded)
    except KeyboardInterrupt:
        res = False

    return res


if __name__ == "__main__":
    pass_thru()
