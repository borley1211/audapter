#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
現在使用しているサウンドシステムの出力をモニタリングするツールです。
matplotlibライブラリを使用して、スペクトルアナライザを表示します。
"""
import librosa as rosa
import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt
from adaptune import passalsa, params

PCMDEV = passalsa.ALSA_Source()

fftlength = 2 * params["period_size"]
vol_scale = 2 ** 21

x_t = np.zeros(fftlength, dtype=np.float16)
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
    global LIN
    LIN.set_data(omega, np.zeros_like(omega, dtype=float))
    return LIN,


def _update_spec(x):
    global x_t, omega, vol_scale, PCMDEV, fftlength, LIN
    x_t = np.roll(x_t, -PCMDEV.period_size)
    x_t[-PCMDEV.period_size:] = x
    D = rosa.core.stft(x_t, fftlength)
    LIN.set_data(omega, np.abs(D[:, 0]) / vol_scale)
    return LIN,


def _frames():
    global PCMDEV
    while True:
        yield PCMDEV.read_data()


if __name__ == '__main__':
    
    anim = animation.FuncAnimation(
        FIG,
        _update_spec,
        init_func=_init,
        interval=10,
        frames=_frames,
        blit=True)

    plt.show()
