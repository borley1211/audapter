import numpy as np
from nptyping import Array
from scipy.fftpack import fft, ifft
from typing_extensions import NoReturn

from ..driver.filter_driver import FilterDriver


class FIR_Tuner:
    D: Array
    X: Array
    Y: Array
    W: Array

    def __init__(self, samplerate: int, period_ms: float):
        """
        Adaptive Tuner as FIR-Filter

        Args:
            samplerate (int): Sample rate of data.
            period_ms (float): Length of period to update filter(as 'msec').
        """
        self.rate = samplerate
        self.period = period_ms

    def apply_fft(self, desired: Array, input_: Array, output_: Array) -> NoReturn:
        self.D = np.abs(fft(desired, self.rate))
        self.X = np.abs(fft(input_, self.rate))
        self.Y = np.abs(fft(output_, self.rate))

        self._init_filter(self.D.T.shape)  # Generate FIR-Filter object

    def _init_filter(self, shape) -> NoReturn:
        self.filter = FilterDriver(shape)

    def run(self):
        pass

    def invert_fft(self):
        pass


# fs = 48000
# T_sec = 0.1

# x_arr = np.sin(np.linspace(0, T_sec, fs * T_sec) * np.pi / 2)
# d_arr = x_arr
# x_arr.shape

# y_arr = np.random.normal(-0.2, 0.2, x_arr.shape) + x_arr
# y_arr.shape

# D, X = np.abs(fft(d_arr, fs)), np.abs(fft(x_arr, fs))
# D /= np.max(D)
# X /= np.max(X)
# D, X

# D.shape

# Y = np.abs(fft(y_arr, fs))
# Y /= np.max(Y)
# Y

# driver = filter_driver.FilterDriver(shape=X.shape)

# W = np.zeros_like(X).T
# W = driver.tune(D, Y)
# W

# w = np.abs(ifft(W, int(fs * T_sec)))
# w *= np.max(w)
# w.shape

# xdash_arr = np.dot(w, x_arr)
# xdash_arr
