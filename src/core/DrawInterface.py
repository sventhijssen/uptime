from abc import ABC, abstractmethod
from typing import Set


class DrawInterface(ABC):

    @abstractmethod
    def draw(self) -> Set[str]:
        pass
