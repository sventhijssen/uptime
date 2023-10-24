import itertools
import time
from typing import Dict

from networkx import MultiDiGraph

from aux.DataAssignmentStrategy import DataAssignmentStrategy
from aux.RowColumnPermutation import MultiLayerPermutation
from core.crossbars.Topology import Topology
from core.expressions.BooleanExpression import LITERAL
from core.crossbars.MemristorCrossbar import MemristorCrossbar


class DataLayoutReorganization:

    def __init__(self, design: MemristorCrossbar, crossbar: MemristorCrossbar, assignment_strategy: DataAssignmentStrategy = MultiLayerPermutation()):
        """
        For now, we rely on MemristorCrossbarDesign for the crossbar but in the future, we will make an abstraction.
        We will differentiate between a design and a physical crossbar.
        :param design:
        :param crossbar:
        """
        self.design = design
        self.crossbar = crossbar
        self.assignment_strategy = assignment_strategy
        self.compress_time = 0
        self.assignment_time = 0
        self.decompress_time = 0

    def _compress(self) -> MemristorCrossbar:
        start_time = time.time()
        compressed_crossbar = self.crossbar.compress()
        end_time = time.time()

        self.compress_time = end_time - start_time

        return compressed_crossbar

    def _assign(self, design: MemristorCrossbar, compressed_crossbar: MemristorCrossbar) -> Dict:
        start_time = time.time()
        assignment = self.assignment_strategy.assign(design, compressed_crossbar)
        end_time = time.time()

        self.assignment_time = end_time - start_time

        return assignment

    def _equivalent_(self):
        # From the compressed faulty crossbar, apply a greedy assigment
        # to the possible rows and columns in the faulty crossbar
        equivalent_rows_lst = list(filter(lambda x: len(x) != 0, self.crossbar.get_equivalent_rows()))
        equivalent_rows = set([item for elem in equivalent_rows_lst for item in elem])
        equivalent_columns_lst = list(filter(lambda x: len(x) != 0, self.crossbar.get_equivalent_columns()))
        equivalent_columns = set([item for elem in equivalent_columns_lst for item in elem])

        all_rows = set([row for row in range(self.crossbar.rows)])
        all_columns = set([column for column in range(self.crossbar.columns)])

        missing_rows = list(map(lambda r: [r], all_rows - equivalent_rows))
        missing_columns = list(map(lambda c: [c], all_columns - equivalent_columns))

        equivalent_rows_lst.extend(missing_rows)
        equivalent_columns_lst.extend(missing_columns)
        return equivalent_rows_lst, equivalent_columns_lst

    def _decompress(self, assignment: Dict) -> MemristorCrossbar:
        start_time = time.time()

        crossbar_design = self.crossbar.__copy__()

        equivalent_rows_lst, equivalent_columns_lst = self._equivalent_()

        for r in range(self.design.rows):
            for c in range(self.design.columns):
                assigned_row = assignment.get((0, r))
                assigned_column = assignment.get((1, c))

                r_options = equivalent_rows_lst[assigned_row[1]]
                c_options = equivalent_columns_lst[assigned_column[1]]

                # Based on: https://www.geeksforgeeks.org/python-program-to-get-all-unique-combinations-of-two-lists/
                options = list(itertools.product(r_options, c_options))

                for (r_option, c_option) in options:
                    original_literal = self.design.get_memristor(r, c).literal
                    option_literal = self.crossbar.get_memristor(r_option, c_option).literal
                    if original_literal == LITERAL("True", True) and option_literal != LITERAL("False", False):
                        assignment[((0, r), (1, c))] = (r_option, c_option)
                        crossbar_design.set_memristor(r_option, c_option, original_literal)
                        break
                    elif original_literal == LITERAL("False", False) and option_literal != LITERAL("True", True):
                        assignment[((0, r), (1, c))] = (r_option, c_option)
                        crossbar_design.set_memristor(r_option, c_option, original_literal)
                        break
                    elif original_literal != LITERAL("True", True) and original_literal != LITERAL("False", False) and option_literal != LITERAL("True", True) and option_literal != LITERAL("False", False):
                        assignment[((0, r), (1, c))] = (r_option, c_option)
                        crossbar_design.set_memristor(r_option, c_option, original_literal)
                        break

        # Outputs have permuted
        for (output_variable, (layer, row)) in self.design.get_output_nanowires().items():
            crossbar_design.set_output_nanowire(output_variable, equivalent_rows_lst[assignment[(0, row)][1]][0], layer)

        crossbar_design.input_variables = self.design.get_input_variables()

        # Input(s) have permuted
        for (input_function, (layer, row)) in self.design.get_input_nanowires().items():
            crossbar_design.set_input_nanowire(input_function, equivalent_rows_lst[assignment[(0, row)][1]][0], layer)

        for r in range(crossbar_design.rows):
            for c in range(crossbar_design.columns):
                if crossbar_design.get_memristor(r, c).literal == LITERAL("-", True):
                    crossbar_design.set_memristor(r, c, LITERAL("False", False))

        end_time = time.time()

        self.decompress_time = end_time - start_time

        return crossbar_design

    def map(self) -> Topology:
        compressed_crossbar = self._compress()
        assignment = self._assign(self.design, compressed_crossbar)
        crossbar_design = self._decompress(assignment)

        topology_graph = MultiDiGraph()
        topology_graph.add_node(crossbar_design)
        return Topology(topology_graph)
