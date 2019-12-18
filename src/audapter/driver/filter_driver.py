from typing import Tuple

import numpy as np
import padasip as pa
from stft import spectrogram as stft, ispectrogram as istft

from ..helper.load_config import settings
from ..interface.driver.filter_driver import FilterDriverABC
from ..domain.model import FilterModel


class FilterDriver(FilterDriverABC):
    def __init__(
        self, domain=settings.get('FILTER.domain'), filter_cls=FilterModel, frames: int = 1024,
    ):

        self.domain = domain if domain in ["time", "freq"] else None
        if self.domain is None:
            raise
        self.n_filter = frames
        filter_obj = filter_cls(
            settings.FILTER.model, self.n_filter, **settings.FILTER.padasip
        )
        self.filter = filter_obj.adaptive_filter
        self.datas_in: np.ndarray = np.zeros(
            self.n_filter, dtype=np.float16
        )  # 入力を記憶しておくndarray

    def _tune_at_time(
        self, desired: np.ndarray, data_in: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Time-based tuning
        """
        desired, data_in = desired[:], data_in[:]
        return self.filter.run(desired, data_in)

    def _tune_at_freq(
        self, desired: np.ndarray, data_in: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Frequency-based tuning
        """
        D_d = np.abs(stft(desired, n_fft=self.n_filter))
        D_i = np.abs(stft(data_in, n_fft=self.n_filter))
        D_d, D_i = D_d.tolist(), D_i.tolist()
        X_out, Err, W_frq = self.filter.run(D_d, D_i)
        return istft(X_out), istft(Err), W_frq

    def tune(self, desired, data_in):
        self.datas_in[-(data_in.size) :] = data_in
        if self.domain == "time":
            x_out = self._tune_at_time(desired, self.datas_in)
        elif self.domain == "freq":
            x_out = self._tune_at_freq(desired, self.datas_in)
        return x_out

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
