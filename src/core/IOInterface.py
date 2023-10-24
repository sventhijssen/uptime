from abc import ABC, abstractmethod
from pathlib import Path

from core.BooleanFunction import BooleanFunction


class IOInterface(ABC):

    @staticmethod
    @abstractmethod
    def read(filepath: Path) -> BooleanFunction:
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def write(self, filepath: Path = None):
        pass
