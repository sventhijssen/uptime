from networkx import MultiDiGraph

from core.crossbars.Topology import Topology
from core.expressions.BooleanExpression import LITERAL
from core.crossbars.MemristorCrossbar import MemristorCrossbar
from exceptions.AssignmentError import AssignmentError


class NaiveDataLayoutOrganization:

    def __init__(self, design: MemristorCrossbar, crossbar: MemristorCrossbar):
        self.design = design
        self.crossbar = crossbar

    def map(self) -> Topology:

        crossbar_design = MemristorCrossbar(self.crossbar.rows, self.crossbar.columns)

        for r in range(self.design.rows):
            for c in range(self.design.columns):
                crossbar_memristor = self.crossbar.get_memristor(r, c)
                crossbar_literal = crossbar_memristor.literal
                design_memristor = self.design.get_memristor(r, c)
                design_literal = design_memristor.literal
                if crossbar_literal == LITERAL("True", True) or crossbar_literal == LITERAL("False", False):
                    if crossbar_literal != design_literal:
                        raise AssignmentError()
                crossbar_design.set_memristor(r, c, design_literal)

        for (output_variable, (layer, row)) in self.design.get_output_nanowires().items():
            crossbar_design.set_output_nanowire(output_variable, row, layer)

        for (input_function, (layer, row)) in self.design.get_input_nanowires().items():
            crossbar_design.set_input_nanowire(input_function, row, layer)

        topology_graph = MultiDiGraph()
        topology_graph.add_node(crossbar_design)
        return Topology(topology_graph)
