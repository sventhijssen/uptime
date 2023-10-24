import math
import random

from core.expressions.BooleanExpression import LITERAL
from core.crossbars.MemristorCrossbar import MemristorCrossbar


class BivariateGaussianDefectCrossbarGenerator:
    """
    This crossbar generator will create a spatial distribution for defects according to the techniques described in
    "Simulation of Spatial Fault Distributions for Integrated Circuit Yield Estimations" by C.H. Stapper.
    The methodology was used in ""Fault-Tolerant Training with On-Line Fault Detection for RRAM-based
    Neural Computing Systems" by L. Xia et al.
    """

    def __init__(self, rows: int, columns: int, fabrication_defect_rate: float = 0.10, open_close_ratio: int = 5):
        if rows != columns:
            raise NotImplementedError("Crossbar must be square.")
        self.rows = rows
        self.columns = columns
        self.fabrication_defect_rate = fabrication_defect_rate
        self.open_close_ratio = open_close_ratio
        self.c = 0.2
        self.sigma = 0.3
        self.z = [[0 for c in range(self.columns)] for r in range(self.rows)]

    def generate(self, nr_crossbars: int = 1, seed: int = 7583):
        # random.seed(seed)

        for i in range(nr_crossbars):
            crossbar = MemristorCrossbar(self.rows, self.columns, default_literal=LITERAL("-", True))
            fault_locations = set()

            # While we do not meet the percentage of stuck-at-faults, we add a new fault center.
            while len(fault_locations) < int(round(self.fabrication_defect_rate * self.rows * self.columns)):
                # We define the center of the crossbar at (x2, y2)
                x2 = int(round(self.columns / 2))
                y2 = int(round(self.rows / 2))

                # We translate the center with distance dx and dy
                dx = random.randint(-x2, x2)
                dy = random.randint(-y2, y2)

                # New center
                # print((x2+dx, y2+dy))

                for r in range(self.rows):
                    for c in range(self.columns):

                        if c < x2:
                            x = (c - x2)/x2
                        else:
                            x = (c - x2 + 1)/x2
                        if r < y2:
                            y = (r - y2)/y2
                        else:
                            y = (r - y2 + 1)/y2
                        # p = (1/(self.sigma*math.sqrt((2*math.pi)))) * math.pow(math.e, -(math.pow(x, 2) + math.pow(y, 2)) / (2*math.pow(self.sigma, 2)))
                        p = self.c * math.pow(math.e, -(math.pow(x, 2) + math.pow(y, 2)) / (2 * math.pow(self.sigma, 2)))

                        if random.random() < p:
                            if 0 <= r+dy <= self.rows - 1 and 0 <= c + dx <= self.columns - 1:
                                fault_locations.add((r+dy, c+dx))

            # When the number of faults is greater than the stuck-at-fault rate*R*C, then we must remove faults
            if len(fault_locations) > int(round(self.fabrication_defect_rate * self.rows * self.columns)):
                d = len(fault_locations) - int(round(self.fabrication_defect_rate * self.rows * self.columns))

                elements = random.sample(fault_locations, d)
                for element in elements:
                    fault_locations.remove(element)

            # We define the number of stuck-off faults based on the open-close-ratio
            nr_stuck_off = int(round(len(fault_locations) / (self.open_close_ratio + 1) * self.open_close_ratio))
            stuck_off_locations = random.sample(fault_locations, k=nr_stuck_off)
            stuck_on_locations = fault_locations.difference(stuck_off_locations)

            s = 0
            for (r, c) in stuck_on_locations:
                crossbar.set_memristor(r, c, LITERAL("True", True))
                crossbar.get_memristor(r, c).stuck_at_fault = True
                crossbar.get_memristor(r, c).permanent = True
                s += 1

            for (r, c) in stuck_off_locations:
                crossbar.set_memristor(r, c, LITERAL("False", False))
                crossbar.get_memristor(r, c).stuck_at_fault = True
                crossbar.get_memristor(r, c).permanent = True
                s += 1

            # print(s)
            # print(s/(self.rows*self.rows))

            yield crossbar
