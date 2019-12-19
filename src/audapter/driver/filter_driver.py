from typing import Tuple

import numpy as np
from stft import ispectrogram as istft
from stft import spectrogram as stft

from ..domain.model import FilterModel
from ..helper.load_config import settings
from ..interface.driver.filter_driver import FilterDriverABC


class FilterDriver(FilterDriverABC):
    def __init__(
        self, domain=settings.get("FILTER.domain"), frames: int = 1024,
    ):

        self.domain = domain
        self.n = settings.get("FILTER.n")
        self.filter = FilterModel(**dict(settings.get("FILTER")))
        self.datas_in: np.ndarray = np.zeros(
            self.n, dtype=np.float16
        )  # 入力を記憶しておくndarray

    def tune(self, desired, data_in) -> np.ndarray:
        return self.filter.apply(desired, data_in)

    def get_filter_weights(self) -> np.ndarray:
        return self.filter.w

    def save_filter(self, filename: str) -> None:
        """
        指定したファイルに現在のフィルタ係数を保存します。
        これは主に、構成した適応フィルタを再び利用したいときに有効です。

        Args:
            filename (str): 係数を保存(新規作成 or 上書き)したいファイル名。
        """
        np.savez(filename, self.get_filter_weights())
