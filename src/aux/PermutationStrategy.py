from abc import abstractmethod
from typing import Set, Dict

from aux.DataAssignmentStrategy import DataAssignmentStrategy
from core.crossbars.MemristorCrossbar import MemristorCrossbar


class PermutationStrategy(DataAssignmentStrategy):

    def __init__(self):
        super().__init__()
        self.error_time = 0
        self.ilp_time = 0

    @abstractmethod
    def _find_permutation(self, design: MemristorCrossbar, crossbar: MemristorCrossbar, errors: Set) -> Dict:
        pass

    @abstractmethod
    def assign(self, design: MemristorCrossbar, crossbar: MemristorCrossbar) -> Dict:
        pass
