#!/usr/dev python3
# -*- coding: utf-8 -*-
from time import time
from typing import Optional, Union, Iterator

import alsaaudio as alsa
import numpy as np

from adaptune import core, params, dev


class ALSA_Source(object):
    """
    Linuxの基本サウンドシステム(ALSA)にアクセスし、音声入力を検出するクラスです。
    """

    def __init__(self, device=dev["monitor"], mode=alsa.PCM_NONBLOCK, params=params):
        self.pcm = alsa.PCM(type=alsa.PCM_CAPTURE, mode=mode, device=device)
        self.config(**params)
        self.devname = device

    def config(
            self,
            rate: int,
            formatname: 'alsa.PCM_TYPE',
            period_size: int,
            channels: int):
        self.pcm.setchannels(channels)
        self.pcm.setrate(rate)
        self.pcm.setperiodsize(period_size)
        self.pcm.setformat(formatname)
        self.rate = rate
        self.fmt = formatname
        self.p_size = period_size
        self.ch = channels
        
    def _read_once(self) -> np.ndarray:
        length, data = self.pcm.read()
        if length <= 0:
            x = np.zeros(self.p_size)
        else:
            x = np.frombuffer(
                data,
                dtype=np.int16)
            if (self.p_size - x.size) // self.ch > 0:
                np.pad(
                    x,
                    (0, (self.p_size - x.size) // self.ch),
                    mode='constant')
        return x

    def read_data(self) -> Iterator:
        while True:
            x = self._read_once()
            yield x


class ALSA_Sink(object):
    """
    Linuxの基本サウンドシステム(ALSA)にアクセスし、音声を出力するクラスです。
    """

    def __init__(self, device=dev["main"], mode=alsa.PCM_NORMAL):
        self.pcm = alsa.PCM(type=alsa.PCM_PLAYBACK, mode=mode, device=device)
        self.config(**params)

    def config(
            self,
            rate: int,
            formatname: 'alsa.PCM_TYPE',
            period_size: int,
            channels: int):
        self.pcm.setchannels(channels)
        self.pcm.setrate(rate)
        self.pcm.setperiodsize(period_size)
        self.pcm.setformat(formatname)
        self.rate = rate
        self.fmt = formatname
        self.p_size = period_size
        self.ch = channels

    def write_data(self, data_out: np.ndarray) -> None:
        bdata = bytearray(data_out)
        fragments = [
            bdata[i:i + self.p_size - 1] for i in range(
                0, len(bdata), self.p_size)]
        for frg in fragments:
            self.pcm.write(frg)


def run(
    domain: str = 'time',
    run_time: Optional[int] = None
) -> Union[bool, None]:
    PCM_MONITOR = ALSA_Source(device=dev["monitor"])
    PCM_SINK = ALSA_Sink(device=dev["main"])
    PCM_MIC = ALSA_Source(device=dev["input"])

    filt = core.AdapTuner()

    ret = None

    for desired, data_in in zip(
        PCM_MONITOR.read_data(),
        PCM_MIC.read_data()
    ):
        t_start = time()
        x_out, err, w_c = filt.tune(desired, data_in)
        PCM_SINK.write_data(x_out)
        if run_time is not None:
            ret = True if int(time() - t_start) >= run_time else False
            if ret:
                break
        else:
            continue

    return ret
