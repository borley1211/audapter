#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import time
from typing import Optional

import alsaaudio as alsa
import numpy as np

from adaptune import core, params

device = 'default'


class ALSA_Source(object):
    """
    Linuxの基本サウンドシステム(ALSA)にアクセスし、音声入力を検出するクラスです。
    """

    def __init__(self, mode=alsa.PCM_NORMAL, device=device):
        self.pcm = alsa.PCM(alsa.PCM_CAPTURE, mode=mode, device=device)
        self.config(**params)
        self.devname = device

    def config(
            self,
            rate: int,
            format: 'alsa.PCM_TYPE',
            period_size: int,
            channels: int):
        self.pcm.setchannels(channels)
        self.pcm.setrate(rate)
        self.pcm.setperiodsize(period_size)
        self.pcm.setformat(format)
        self.rate = rate
        self.format = format
        self.period_size = period_size
        self.channels = channels

    def read_data(
        self, dtype: Optional[np.dtype] = np.int16
    ) -> np.ndarray:
        while True:
            _length, data = self.pcm.read()
            x = np.frombuffer(data, dtype=dtype)
            np.pad(x, ((0, self.period_size - len(x)),), 'constant')
            yield x


class ALSA_Sink(object):
    """
    Linuxの基本サウンドシステム(ALSA)にアクセスし、音声を出力するクラスです。
    """

    def __init__(self, mode=alsa.PCM_NORMAL, device=device):
        self.pcm = alsa.PCM(alsa.PCM_PLAYBACK, mode=mode, device=device)
        self.config(**params)

    def config(
            self,
            rate: int,
            format: 'alsa.PCM_TYPE',
            period_size: int,
            channels: int):
        self.pcm.setchannels(channels)
        self.pcm.setrate(rate)
        self.pcm.setperiodsize(period_size)
        self.pcm.setformat(format)
        self.rate = rate
        self.format = format
        self.period_size = period_size
        self.channels = channels

    def write_data(self, data_out: np.ndarray) -> None:
        bdata = data_out.tobytes()
        fragments = [bdata[i:i + self.period_size]
                     for i in range(0, len(bdata), self.period_size)]
        for frg in fragments:
            self.pcm.write(frg)


def main(
    domain: str = 'time',
    run_time: Optional[int] = None
):
    PCM_MONITOR = ALSA_Source()
    PCM_SINK = ALSA_Sink()
    PCM_MIC = ALSA_Source()

    filter = core.AdapTuner()

    for desired, input in zip(
        PCM_MONITOR.read_data(),
        PCM_MIC.read_data()
    ):
        t_start = time()
        x_out, err, w_c = filter.tune(desired, input)
        PCM_SINK.write_data(x_out)
        if run_time is not None:
            if int(time() - t_start) >= run_time:
                return True
            else:
                return False
