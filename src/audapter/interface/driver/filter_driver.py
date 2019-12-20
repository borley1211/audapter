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
    def tune(self, desired: Array, data_in: Array) -> Tuple[Array, Array, Array]:
        """
        Update internal filter.

        Args:
            desired (np.Array): A vector including desired data(1-dimension).
            input (np.Array): A vector including input data(1-dimension)。

        Returns:
            Tuple[np.Array, np.Array, np.Array]:
                A tuple includes...

                * output (np.Array): An output vector.

                * error (np.Array): An error vector.

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

                * weights (np.Array): A filter-weight for now(2-dimensions).
        """
        raise NotImplementedError

    @abstractmethod
    def get_filter_weights(self) -> Array:
        """
        Returns:
            np.Array: A filter-weight for now.
        """
        raise NotImplementedError
