'''
This is app for Frequency Response Measuring.
'''
import numpy as np

__all__ = ["sweptsine", "take_a_mean"]


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

    ss_real = np.real(np.fft.ifft(ss_omega))
    ss_real = gain * np.roll(ss_real, num // 2 - eff)
    ss_real = np.r_[np.tile(ss_real, repeat), np.zeros(num)]

    return ss_real, ss_inv_omega, num, repeat


def take_a_mean(rec, num, repeat):
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
