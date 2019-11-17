from abc import ABCMeta, abstractmethod
from numpy import ndarray
from typing import Tuple


class FilterDriverABC(metaclass=ABCMeta):
    @abstractmethod
    def tune(self, desired : ndarray, data_in : ndarray) -> Tuple[ndarray, ndarray, ndarray]:
        raise NotImplementedError
    
    @abstractmethod
    def get_filter_weight(self) -> ndarray:
        raise NotImplementedError
    
    @abstractmethod
    def save_filter(self, filename : str) -> None:
        raise NotImplementedError
