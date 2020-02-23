from abc import ABCMeta, abstractmethod
from typing import Tuple, Union

from nptyping import Array


class FilterDriverABC(metaclass=ABCMeta):
    """
    FilterDriverABC is the base-class for using Adaptive Signal Processing
    """

    @abstractmethod
    def __init__(self, shape: Union[int, Tuple[int]]):
        raise NotImplementedError

    @abstractmethod
    def run(self, desired: Array, data_in: Array) -> (Array, Array, Array):
        """
        Update internal filter.

        Args:
            desired (Array): A vector including desired data(1-dimension).
            data_in (Array): A vector including input data(1-dimension)。

        Returns:
            Tuple[Array, Array, Array]:
                A tuple includes...

                * output (Array): An output vector.

                * error (Array): An error vector.

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

                * weights (Array): A filter-weight for now(2-dimensions).
        """
        raise NotImplementedError

    @abstractmethod
    def get_filter_weights(self) -> Array:
        """
        Returns:
            Array: A filter-weight for now.
        """
        raise NotImplementedError
