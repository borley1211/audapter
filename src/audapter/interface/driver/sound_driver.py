from abc import ABCMeta, abstractmethod
from ...helper import types
from ...domain.model import FilterModel


class SoundDriverABC(metaclass=ABCMeta):
    @abstractmethod
    def __init__(
        self, device_dict: dict, domain: str, filter_: FilterModel, frames: int
    ):
        raise NotImplementedError
