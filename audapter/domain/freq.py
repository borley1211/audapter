from typing import Dict

from adasigpy.adasigpy import AdaptiveSignalProcesserABC as _ASPABC
from pyroomacoustics import windows as _win
from pyroomacoustics.adaptive import SubbandLMS as _SLMS
from pyroomacoustics.transform import STFT as _STFT

from ..helper.config import settings as _stgs

_window: Dict = {
    "hann": _win.hann,
    "hamming": _win.hamming,
    "gaussian": _win.gaussian,
}

_WINDOW_MODEL: str = _stgs.get("FILTER.WINDOW")
_FILTER_LENGTH: int = _stgs.get("FILTER.LENGTH")
_BLOCK_SIZE = _stgs.get("FILTER.BLOCKSIZE")
_STEP_SIZE = _stgs.get("FILTER.MU")


class FilterModel(_ASPABC):
    stft: _STFT
    blocksize: int
    hop: int
    driver: _SLMS

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


def get_filter():
    return FilterModel
