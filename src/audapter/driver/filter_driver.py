from typing import Tuple

from nptyping import Array
from stft import ispectrogram as istft
from stft import spectrogram as stft

from ..domain.model import FilterModel
from ..helper.load_config import settings
from ..interface.driver.filter_driver import FilterDriverABC


class FilterDriver(FilterDriverABC):
    def __init__(self, shape):

        self.shape = shape
        self.filter = FilterModel(
            settings.get("FILTER.model"),
            self.shape,
            settings.get("FILTER.mu"),
            settings.get("FILTER.w"),
            settings.get("FILTER.lambda_"),
        )

    def tune(self, desired, data_in) -> Array:
        return self.filter.apply(desired, data_in)

    def get_filter_weights(self) -> Array:
        return self.filter.w
