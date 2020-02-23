from typing import Dict

from adasigpy.adasigpy import AdaptiveSignalProcesserABC as _ASPABC
from nptyping import Array
from pyroomacoustics import windows as _win
from pyroomacoustics.adaptive import SubbandLMS as _SLMS
from pyroomacoustics.adaptive import hermitian as _hermitian
from pyroomacoustics.transform import STFT as _STFT

from ..helper.config import load_settings

settings = load_settings()

_window: Dict = {
    "hann": _win.hann,
    "hamming": _win.hamming,
    "gaussian": _win.gaussian,
}

_WINDOW_MODEL: str = settings.get("FILTER.WINDOW")
_FILTER_LENGTH: int = settings.get("FILTER.LENGTH")
_BLOCK_SIZE = settings.get("FILTER.BLOCKSIZE")
_STEP_SIZE = settings.get("FILTER.MU")


class FilterModel(_ASPABC):
    stft: _STFT
    blocksize: int
    hop: int
    driver: _SLMS
    w: Array

    def __init__(
        self,
        window=_WINDOW_MODEL,
        blocksize=_BLOCK_SIZE,
        mu=_STEP_SIZE,
        w_init="unit",
        domain="freq",
        w_len=_FILTER_LENGTH,
    ):
        self.blocksize = blocksize
        self.hop = self.blocksize // 2 + 1
        self.stft = _STFT(self.blocksize, self.hop, analysis_window=_window[window])
        self.driver = _SLMS(w_len, self.hop, mu=mu)
        self.w = _hermitian(self.driver.W)[::-1]

    def adopt(self, d, x):
        self.stft.analysis(d)
        D = self.stft.X[:]
        self.stft.analysis(x)
        X = self.stft.X[:]
        self.driver.update(X_n=X, D_n=D)
        self.w = _hermitian(self.driver.W)[::-1]

    def update(self, d, x):
        self.adopt(d, x)
        return self.w[:]


def get_filter():
    return FilterModel
