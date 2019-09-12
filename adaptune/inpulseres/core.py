#!/usr/bin/env python3
'''
This is app for Frequency Response Measuring.
'''
import argparse
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy import fftpack

from adaptune.inpulseres import player, tools


def sweptsine(num=2**16, repeat=3, gain=50):
    '''
    make TSP(Swept-Sine-Signal)

    Keyword Arguments:
        num {int} -- signal length of Swept-Sine (default: {2**16})
        repeat {int} -- repeat number (default: {3})
        gain {int or float} -- gain (default: {50})

    Returns:
        (ndarray, ndarray, int, int) -- (Swept-Sine, Invert Swept-Sine(freq), 'num', 'repeat')
    '''
    eff = num // (2**2)
    k = np.arange(0, num)

    ss_omega = np.zeros(num, dtype=np.complex_)
    ss_exp = np.exp(-1j * 4 * np.pi * eff * (k / num)**2)

    ss_omega[:num // 2 + 1] = ss_exp[:num // 2 + 1]
    ss_omega[num // 2 + 1:] = np.conj(ss_exp[1:num // 2][::-1])

    ss_inv_omega = np.conj(ss_omega)

    ss_real = np.real(fftpack.ifft(ss_omega))
    ss_real = gain * np.roll(ss_real, num // 2 - eff)
    ss_real = np.r_[np.tile(ss_real, repeat), np.zeros(num)]

    return ss_real, ss_inv_omega, num, repeat


def averaging(rec, num, repeat):
    '''
    Average REC Data

    Arguments:
        rec {ndarray} -- recorded data
        num {int} -- signal length of Swept-Sine
        repeat {int} -- repeat number

    Returns:
        ndarray -- averaged data
    '''
    rec_ave = np.zeros((num - 1, rec.ndim))
    for n in range(0, num * repeat, num):
        rec_ave += rec[n:n + num - 1]
    return rec_ave / (repeat)


def main():
    plt.figure(figsize=(4, 8))
    X = 5
    Y = 1

    TSP, INV, NUM, REPEAT = sweptsine()

    plt.subplot(X, Y, 1)
    plt.plot(TSP)
    plt.title('Swept-Sine Wave')
    plt.grid()
    plt.pause(1)

    TEMP = tempfile.NamedTemporaryFile(suffix='.wav')
    sf.write(TEMP, TSP, samplerate=NUM, subtype='PCM_24')
    PARSER = argparse.ArgumentParser()
    tools.add_arg_for_player(PARSER)
    PARSER.set_defaults(filename=TEMP.name)
    ARGS = PARSER.parse_args()

    DEV = player.AudioPlayRec(
        filename=ARGS.filename,
        devices=(ARGS.input_device, ARGS.output_device),
        blocksize=ARGS.blocksize,
        bufsize=ARGS.buffersize,
        channels=2
    )

    try:
        REC, F_S = DEV.main()
        REC = averaging(REC, NUM, REPEAT)
        plt.subplot(X, Y, 2)
        plt.plot(REC)
        plt.title('REC Data')
        plt.grid()
        plt.tight_layout()
        plt.pause(1)

        INV = np.tile(INV[:-1], (REC.ndim, 1)).transpose()
        TF = INV * fftpack.fft(REC)
        plt.subplot(X, Y, 3)
        plt.plot(
            np.array(
                [np.linspace(0, F_S, NUM) for _ in range(TF.ndim)]
            ).transpose()[:-1],
            20 * np.log10(np.abs(TF) / np.max(np.abs(TF)))
        )
        plt.xscale('log')
        plt.title('Transfer Function')
        plt.xlabel('Frequency[Hz]')
        plt.grid()
        plt.tight_layout()
        plt.pause(1)

        IR = fftpack.ifft(TF)
        for i in range(IR.ndim):
            plt.subplot(X, Y, 4 + i)
            plt.title('Impulse Response')
            plt.plot(IR[NUM // 2:, i].real, label='Ch {}'.format(i + 1))
            plt.legend()
            plt.grid()
        plt.tight_layout()
        plt.show()

        import os
        if os.path.isdir('./Properties/') is False:
            os.makedirs('./Properties/')
        np.savez(
            './Properties/dev{input}_{output}.npz'.format(
                input=DEV.device[0], output=DEV.device[1]),
            [TF, IR])

    except KeyboardInterrupt:
        TEMP.close()
        exit('\nInterrupted by user')

    finally:
        TEMP.close()


if __name__ == '__main__':

    main()
