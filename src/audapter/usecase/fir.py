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

        # Generate FIR-Filter object
        self._init_filter(self.D.T.shape)

    def _init_filter(self, shape) -> NoReturn:
        self.filter = FilterDriver(shape)

    def run(self, desired: Array, input_: Array, output_: Array) -> Array:
        self.apply_fft(desired, input_, output_)
        self.W = self.filter.tune(self.D, self.X, self.Y)
        X_dash = self.W * self.X
        x_dash = ifft(X_dash)
        return x_dash[: self.rate * self.period // 1000]
