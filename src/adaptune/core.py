import numpy as np
from padasip import padasip as pa

from typing import Union, Tuple

class AdapTuner(object):
    """
    Adaptive filter for signal tuning
    """

    def __init__(
            self,
            domain: str = "time",
            algorithm: str = "nlms",
            f_init: Union[np.ndarray, str] = None) -> None:
        self.filter = pa.filters.AdaptiveFilter(model=algorithm)
        self._initialize(f_init)
        # 入力を記憶しておくndarrayを準備すべき

    def _initialize(self, f_init: Union[np.ndarray, str]) -> None:
        """
        _initialize initialize filter-weights
        
        Args:
            f_init (Union[np.ndarray, str]): initial weights
        
        Raises:
            ValueError: type(f_init) is not suitable
        """
        if f_init is None:
            pass
        elif f_init is np.ndarray:
            self.filter.init_weights(f_init)
        elif f_init is str:
            self.filter.init_weights(np.load(file=f_init))
        else:
            raise ValueError(
                "'f_init' seems unlike filter-weights or true-filename.")

    def _reconfigure(self, algorithm: str) -> None:
        """
        _reconfigure reconfig filter-algorithm
        
        Args:
            algorithm (str): other algorithm
        """
        self.filter = pa.filters.AdaptiveFilter(model=algorithm)

    def tune(self, desired: np.ndarray, input: np.ndarray, other_algo: str = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        
        if other_algo is not None:
            self._reconfigure(other_algo)
        return self.filter.run(desired, input)

    def get_filter_parameters(self) -> np.ndarray:
        """
        get_filter_parameters get current filter-params
        
        Returns:
            np.ndarray: params
        """
        return self.filter.w

    def save(self, filename: str) -> None:
        """
        save save filter-weights for specified file
        
        Args:
            filename (str): filename you want to open and (over)write
        
        Returns:
            None: 
        """
        np.savez(filename, self.get_filter_parameters())
