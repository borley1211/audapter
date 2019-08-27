#!/usr/dev python3
# -*- coding: utf-8 -*-
"""
現在使用しているサウンドシステムの出力をモニタリングするツールです。
matplotlibライブラリを使用して、スペクトルアナライザを表示します。
"""
from time import time

import librosa as rosa
import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt
from . import passalsa
from .config import params, dev

m_params = params.copy()
# m_params["channels"] = 1


def monitor(device=dev["monitor"], run_time: int = None) -> None:

    PCMDEV = passalsa.ALSA_Source(device=device, params=m_params)

    fftlength = 2 * PCMDEV.p_size * PCMDEV.ch
    vol_scale = 2 ** 21

    x_t = np.zeros(fftlength, dtype=np.float32)
    omega = rosa.core.fft_frequencies(PCMDEV.rate, fftlength)

    FIG, AX = plt.subplots()
    LIN, = AX.plot([], [])
    AX.set_xticks(np.linspace(1, PCMDEV.rate // 2 + 1, 8))
    AX.set_ylim(0, 1.0)
    AX.set_title("Monitor[{}]".format(PCMDEV.devname))
    AX.set_xlabel("frequency[Hz]")
    AX.set_ylabel("Volume[%]")
    AX.grid()

    def _init():
        LIN.set_data(omega, np.zeros_like(omega, dtype=float))
        return LIN,

    def _update_spec(x, x_t, p_size):
        x_t = np.roll(x_t, -p_size)
        x_t[-p_size:] = x
        D = rosa.core.stft(x_t, fftlength)
        LIN.set_data(omega, np.abs(D[:, 0]) / vol_scale)
        return LIN,

    def _frames():
        yield from PCMDEV.read_data()

    _anim = animation.FuncAnimation(
        FIG,
        func=_update_spec,
        init_func=_init,
        fargs=(x_t, PCMDEV.p_size * PCMDEV.ch),
        interval=10,
        frames=_frames,
        blit=True)

    plt.show(block=False)
    if run_time is not None:
        t = time()
        while int(time() - t) >= run_time:
            t = time()
        input("Enter to close!")
    plt.close()
