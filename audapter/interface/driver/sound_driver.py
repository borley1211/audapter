from abc import ABCMeta, abstractmethod


class SoundDriverABC(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, device_dict: dict):
        raise NotImplementedError
