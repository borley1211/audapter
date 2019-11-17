from abc import ABCMeta, abstractmethod
from ...helper import types


class SoundDriverABC(metaclass=ABCMeta):
    @abstractmethod
    def pass_thru(self, repeat : int, duration : types.Numerics, micro : types.DeviceName, pci : types.DeviceName) -> None:
        raise NotImplementedError
