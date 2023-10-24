from abc import ABC, abstractmethod

from Loggable import Loggable
from core.crossbars.Topology import Topology
from core.decision_diagrams.DD import DD


class SynthesisMethod(Loggable, ABC):

    def __init__(self, dd: DD):
        super().__init__()
        self.dd = dd
        self.topology = None
        self.start_time = None
        self.end_time = None

    @abstractmethod
    def map(self) -> Topology:
        pass
