from abc import abstractmethod
from typing import Dict

from core.crossbars.MemristorCrossbar import MemristorCrossbar


class DataAssignmentStrategy:

    @abstractmethod
    def assign(self, design: MemristorCrossbar, crossbar: MemristorCrossbar) -> Dict:
        pass
