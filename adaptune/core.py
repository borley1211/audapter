from typing import Tuple

import numpy as np
import padasip as pa
from librosa.core import istft, stft

from ._load_config import default_filter, domain, filter_params, hw_params


class AdapTuner(object):
    """
    音響信号処理に利用可能な適応フィルタの基本クラスです。
    """

    def __init__(
        self,
        domain: str = domain,
        default_filter: pa.filters.AdaptiveFilter = default_filter,
        n: int = 1024,
        fs: int = hw_params["rate"],
    ) -> None:

        self.domain = domain if domain in ["time", "freq"] else None
        if self.domain is None:
            raise
        self.n_filter = n
        self.rate = fs
        self.filter: pa.filters.AdaptiveFilter = default_filter(
            self.n_filter, **filter_params
        )
        self.datas_in: np.ndarray = np.zeros(
            self.n_filter, dtype=np.float16
        )  # 入力を記憶しておくndarray

    def _tune_at_time(
        self, desired: np.ndarray, data_in: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Time-based tuning
        """
        desired, data_in = desired.tolist(), data_in.tolist()
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

    def tune(
        self, desired: np.ndarray, data_in: np.ndarray
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
                
                .. math::
                    :nowrap:

                    \[
                    \left\{
                        \\begin{array}{rcl}
                            e & : & \\text{error} \\\\
                            d & : & \\text{desired} \\\\
                            x & : & \\text{input} \\\\
                            \\boldsymbol{\omega} & : & \\text{filter weight}
                        \\end{array}
                    \\right. \\\\
                    \\, \\\\
                    e = d - \\boldsymbol{\omega} \cdot x
                    \]

                * weights (np.ndarray): 現在までのフィルタ係数(の履歴)。2次元配列。

        """
        self.datas_in[-(data_in.size) :] = data_in
        if self.domain == "time":
            x_out = self._tune_at_time(desired, self.datas_in)
        elif self.domain == "freq":
            x_out = self._tune_at_freq(desired, self.datas_in)
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
