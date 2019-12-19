from abc import ABCMeta, abstractmethod
from numpy import ndarray
from typing import Tuple

from ...domain.model import FilterModel as _FilterModel


class FilterDriverABC(metaclass=ABCMeta):
    """
    FilterDriverABC is the base-class for using Adaptive Signal Processing
    """

    @abstractmethod
    def __init__(self, domain : str, filter_ : _FilterModel, frames : int) -> None:
        raise NotImplementedError

    @abstractmethod
    def tune(self, desired : ndarray, data_in : ndarray) -> Tuple[ndarray, ndarray, ndarray]:
        """
        Update internal filter.

        Args:
            desired (np.ndarray): A vector including desired data(1-dimension).
            input (np.ndarray): A vector including input data(1-dimension)。

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]:
                A tuple includes...

                * output (np.ndarray): An output vector.

                * error (np.ndarray): An error vector.
                
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

                * weights (np.ndarray): A filter-weight for now(2-dimensions).
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_filter_weights(self) -> ndarray:
        """
        Returns:
            np.ndarray: A filter-weight for now.
        """
        raise NotImplementedError
    
    @abstractmethod
    def save_filter(self, filename : str) -> None:
        """
        Args:
            filename (str): A file name to want to save.
        """
        raise NotImplementedError
