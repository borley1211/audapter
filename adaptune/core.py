from typing import Tuple

import numpy as np
from librosa.core import istft, stft
from padasip import padasip as pa

from adaptune import params

domain = 'time'

base_filter = pa.filters.FilterNLMS
filter_params = {
    "mu": 0.01,
    "w_init": 'zeros'
}


class AdapTuner:
    """
    音響信号処理に利用可能な適応フィルタの基本クラスです。
    """
    global filter_params, base_filter, domain

    def __init__(
            self,
            domain: str = domain,
            base_filter: 'pa.filters.FilterXX' = base_filter,
            fs: int = params["rate"]) -> None:

        self.domain = domain if domain == 'time' or domain == 'freq' else None
        if self.domain is None:
            raise
        self.period_size = params["period_size"]
        self.n_filter = self.period_size * 2
        self.rate = fs
        self.filter = base_filter(self.n_filter, **filter_params)
        self.datas_in = np.zeros(self.n_filter)  # 入力を記憶しておくndarray

    def tune_at_time(
        self, desired: np.ndarray,
        input: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        適応フィルタを更新します。

        Args:
            desired (np.ndarray): 目標値が格納されたベクトル(1次元配列)。
            input (np.ndarray): 入力値が格納されたベクトル(1次元配列)。

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]:
                以下の要素をもつタプル。

                * output (np.ndarray): 出力値のベクトル。

                * error (np.ndarray): 全サンプルにおける誤差のベクトル。

                    :math: `(error) = (desired) - (filter)\cdot(input)`

                * weights (np.ndarray): 現在までのフィルタ係数(の履歴)。2次元配列。

        """
        self.filter.predict(input)
        return self.filter.run(desired, input)

    def tune_at_freq(
        self, desired: np.ndarray,
        input: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        D_d = np.abs(stft(desired, n_fft=self.n_filter))
        D_i = np.abs(stft(input, n_fft=self.n_filter))
        self.filter.predict(D_i)
        X_out, Err, W_frq = self.filter.run(D_d, D_i)
        return istft(X_out), istft(Err), W_frq

    def tune(
        self, desired: np.ndarray,
        input: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.domain == 'time':
            x_out = self.tune_at_time(desired, input)
        elif self.domain == 'freq':
            x_out = self.tune_at_freq(desired, input)
        return x_out

    def get_filter_weights(self) -> np.ndarray:
        """
        現在までの適応フィルタの係数(の履歴)を取得します。

        Returns:
            np.ndarray: 現在までのフィルタ係数行列。
        """
        return self.filter.w

    def save_filter(self, filename: str) -> None:
        """
        指定したファイルに現在のフィルタ係数を保存します。
        これは主に、構成した適応フィルタを再び利用したいときに有効です。

        Args:
            filename (str): 係数を保存(新規作成 or 上書き)したいファイル名。
        """
        np.savez(filename, self.get_filter_weights())
