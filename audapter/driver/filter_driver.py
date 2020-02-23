from typing import Optional

import numpy as np
from nptyping import Array
from pyroomacoustics.transform import STFT

from ..domain.model import FilterModel
from ..helper.config import load_settings
from ..interface.driver.filter_driver import FilterDriverABC

settings = load_settings()


class FilterDriver(FilterDriverABC):
    def __init__(self, shape):
        self.shape = shape
        self.filter_ = FilterModel(
            settings.get("FILTER.model"),
            self.shape,
            settings.get("FILTER.mu"),
            settings.get("FILTER.w"),
            settings.get("FILTER.lambda_"),
        )

    def run(self, desired, data_in) -> Array:
        return self.filter_.update(desired, data_in)

    def get_filter_weights(self) -> Array:
        return self.filter_.w


def apply_filter(
    w: Array, x: Array, domain: str, stftobj: Optional[STFT] = None
) -> Array:
    if domain == "time":
        return np.dot(w, x.T[::-1])
    elif domain == "freq":
        if not stftobj:
            raise ValueError("In FREQ domain, you HAVE TO SET 'stftobj'")
        stftobj.analysis(x)
        X = stftobj.X[:]
        return stftobj.synthesis(np.diag(np.dot(w, X)))
