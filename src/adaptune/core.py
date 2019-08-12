from typing import Optional, Tuple, Union

import numpy as np
from librosa.core import istft, stft
from padasip import padasip as pa


class AdapTuner(object):
    """
    音響信号処理に利用可能な適応フィルタの基本クラスです。
    """

    def __init__(
            self,
            domain: str = "time",
            algorithm: str = "nlms",
            f_init: Union[np.ndarray, str] = None) -> None:

        self.filter = pa.filters.AdaptiveFilter(model=algorithm)  # Filter本体
        self._init_weights(f_init)  # Filter係数を初期化
        # 入力を記憶しておくndarrayを準備すべき

    def _init_weights(self, f_init: Union[np.ndarray, str]) -> None:
        """
        フィルタ係数を初期化します。

        Args:
            f_init (Union[np.ndarray, str]): フィルタ係数の初期値。

        Raises:
            ValueError: 'type(f_init)'が上記の型で与えられていません。
        """
        if f_init is None:
            pass  # 指定がなければ(default: None)何もしない
        elif f_init is np.ndarray:
            self.filter.init_weights(f_init)  # 係数をそのまま設定
        elif f_init is str:
            # 係数データを格納したファイルを開いてこの値を設定
            self.filter.init_weights(np.load(file=f_init))
        else:
            raise ValueError(
                "'f_init' seems unlike filter-weights or true-filename.")

    def _reconf_algo(self, algorithm: Optional[str]) -> None:
        """
        フィルタ更新アルゴリズムを変更します。

        Args:
            algorithm (Optional[str]): 新たに使用したいアルゴリズム名。
        """
        if algorithm is not None:
            self.filter = pa.filters.AdaptiveFilter(model=algorithm)

    def tune(
        self, desired: np.ndarray,
        input: np.ndarray,
        other_algo: str = None
        ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        適応フィルタを更新します。

        Args:
            desired (np.ndarray): 目標値が格納されたベクトル(1次元配列)。
            input (np.ndarray): 入力値が格納されたベクトル(1次元配列)。
            other_algo (Optional[str]): 今回新たに使用したいアルゴリズムの名称(必要に応じて)。

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: 
                以下の要素をもつタプル。

                * output (np.ndarray): 出力値のベクトル。

                * error (np.ndarray): 全サンプルにおける誤差のベクトル。

                :math:`(error) = (desired) - (filter)\cdot(input)`

                * weights (np.ndarray): 現在までのフィルタ係数(の履歴)。2次元配列。

        """

        self._reconf_algo(other_algo)
        return self.filter.run(desired, input)

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
