from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
from typing import Dict, List, Set, Any

from networkx import has_path, connected_components

from core.BooleanFunction import BooleanFunction
from core.crossbars.Crossbar import Crossbar
from core.expressions.BooleanExpression import LITERAL, TRUE, FALSE


class MemristorCrossbar(Crossbar):
    """
    Type of crossbar where selectorlines are assigned to memristors.
    """

    def __init__(self, rows: int, columns: int, layers: int = 1, name: str = None, compressed: bool = False, default_literal: LITERAL = FALSE()):
        """
        Constructs a memristor crossbar of dimensions (number of memristors) x by y.
        The optional dimension layers indicates the number of layers of memristors.
        By default, the number of layers is 1.
        A memristor is defined by a triple (l, r, c) where r is the index of the nanowire below the memristor,
        c is the index of the nanowire above the memristor, and l is the layer of the memristor.
        A nanowire is defined by a tuple (l, i) where i is the index in a series of parallel nanowires at layer l.
        :param rows: The number of memristors along the input and output nanowires.
        :param columns: The number of memristors orthogonal to the input and output nanowires.
        :param layers: The number of layers of memristors.
        :param name: The name of the crossbar.
        :param compressed: Whether the crossbar is compressed or not. Do not use this for now.
        :param default_literal: The default literal to fill the crossbar. Usually False, but can be LITERAL("-", True).
        """
        super(MemristorCrossbar, self).__init__(rows, columns, layers, name, compressed, default_literal)

    def get_input_variables(self) -> Set[str]:
        input_variables = set()
        for l in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    memristor = self.get_memristor(r, c, l)
                    literal = memristor.literal
                    if literal != TRUE() and literal != FALSE():
                        input_variables.add(literal.atom)
        return input_variables

    def get_output_variables(self) -> Set[str]:
        return self.output_nanowires.keys()

    def get_auxiliary_variables(self) -> Set[str]:
        return set()

    def get_log(self) -> Dict[str, Any]:
        graph = self.graph()
        return {
            "type": self.__class__.__name__,
            "rows": self.rows,
            "columns": self.columns,
            "layers": self.layers,
            "input_nanowires": len(self.input_nanowires),
            "output_nanowires": len(self.output_nanowires.items()),
            "bipartite_graph":
                {
                    "nodes": len(list(graph.nodes)),
                    "edges": len(list(graph.edges)),
                    "literals": len(list(filter(lambda e: graph.get_edge_data(e[0], e[1]).get("atom") != "False" and graph.get_edge_data(e[0], e[1]).get("atom") != "True", graph.edges))),
                    "on": len(list(filter(lambda e: graph.get_edge_data(e[0], e[1]).get("atom") == "True" and graph.get_edge_data(e[0], e[1]).get("positive") == True, graph.edges))),
                    "off": len(list(filter(lambda e: graph.get_edge_data(e[0], e[1]).get("atom") == "False" and graph.get_edge_data(e[0], e[1]).get("positive") == False, graph.edges))),
                }
        }

    @staticmethod
    def read(filepath: Path) -> BooleanFunction:
        f = open(str(filepath))
        import json
        crossbar = json.load(f)
        rows = crossbar.get("rows")
        columns = crossbar.get("columns")
        input_nanowires = crossbar.get("input_nanowires")
        output_nanowires = crossbar.get("output_nanowires")
        bipartite_graph = crossbar.get("bipartite_graph")
        edges = bipartite_graph.get("edges")

        xbar = MemristorCrossbar(rows, columns)
        for edge in edges:
            x, y, l = edge
            if "L0" in x:
                r = int(x[3:])
                c = int(y[3:])
            else:
                r = int(y[3:])
                c = int(x[3:])
            if l == "0":
                literal = LITERAL("False", False)
            elif l == "1":
                literal = LITERAL("True", True)
            elif "~" in l:
                literal = LITERAL(l[1:], False)
            else:
                literal = LITERAL(l, True)
            xbar.set_memristor(r, c, literal)

        for (input_function, (layer, index)) in input_nanowires.items():
            xbar.set_input_nanowire(input_function, index, layer)

        for (output_function, (layer, index)) in output_nanowires.items():
            xbar.set_output_nanowire(output_function, index, layer)

        return xbar

    def to_json(self) -> str:
        graph = self.graph()
        content = {
            "type": "crossbar",
            "subtype": "memristor",
            "name": self.get_name(),
            "rows": self.rows,
            "columns": self.columns,
            "layers": self.layers,
            "input_nanowires": self.input_nanowires,
            # A key maps to a set of values. However, JSON cannot encode a set, thus we convert it into a list.
            "output_nanowires": dict(map(lambda item: (item[0], list(item[1])), self.output_nanowires.items())),
            "bipartite_graph":
                {
                    "nodes": list(graph.nodes),
                    "edges": list(map(lambda e: (e[0], e[1], str(LITERAL(graph.get_edge_data(e[0], e[1]).get("atom"), graph.get_edge_data(e[0], e[1]).get("positive")))), graph.edges))
                }
        }
        return content

    def to_string(self) -> str:
        json_content = self.to_json()
        json_string = json.dumps(json_content, indent=6) + "\n"
        return json_string

    def write(self, filepath: Path):
        content = self.to_string()
        with open(filepath, 'w') as f:
            f.write(content)

    def draw(self) -> Set[str]:
        # We draw a separate crossbar matrix for each layer of memristors.
        # Grid after https://graphviz.org/Gallery/undirected/grid.html
        # Node distance after https://newbedev.com/how-to-manage-distance-between-nodes-in-graphviz
        for layer in range(self.get_memristor_layers()):
            content = ''
            content += 'graph {} {{\n'.format(self.name)
            content += '\tgraph [nodesep="0.2", ranksep="0.2"];\n'
            content += '\tcharset="UTF-8";\n'
            content += '\tratio=fill;\n'
            content += '\tsplines=polyline;\n'
            content += '\toverlap=scale;\n'
            content += '\tnode [shape=circle, fixedsize=true, width=0.4, fontsize=8];\n'
            content += '\n'

            content += '\n\t// Memristors\n'
            for c in range(self.columns):
                for r in range(self.rows):
                    if self.get_memristor(r, c, layer).literal.atom == 'False':
                        v = '0'
                        style = 'color="#000000", fillcolor="#eeeeee", style="filled,solid"'
                    elif self.get_memristor(r, c, layer).literal.atom == 'True':
                        v = '1'
                        style = 'color="#000000", fillcolor="#cadfb8", style="filled,solid"'
                    else:
                        if not self.get_memristor(r, c, layer).literal.positive:
                            v = '¬' + self.get_memristor(r, c, layer).literal.atom
                        else:
                            v = self.get_memristor(r, c, layer).literal.atom
                        style = 'color="#000000", fillcolor="#b4c7e7", style="filled,solid"'
                    content += '\tm{}_{} [label="{}" {}]\n'.format(r + 1, c + 1, v, style)

            content += '\n\t// Functions (left y-axis)\n'
            # Functions
            for r in range(self.rows):
                input_rows = list(map(lambda i: i[1], self.get_input_nanowires().values()))
                style = 'color="#ffffff", fillcolor="#ffffff", style="filled,solid"'
                if r not in input_rows:
                    v = ''  # '{}'.format(self.wordlines[r][0])
                    content += '\tm{}_{} [label="{}" {}]\n'.format(r + 1, 0, v, style)
                else:
                    v = ''
                    for (input_function, (layer, row)) in self.get_input_nanowires().items():
                        if r == row:
                            v = 'Vin<SUB>{}</SUB>'.format(input_function)
                    content += '\tm{}_{} [label=<{}> {}]\n'.format(r + 1, 0, v, style)

            content += '\n\t// Outputs (right y-axis)\n'
            # Outputs
            output_variables = dict()
            for (o, (l, r)) in self.output_nanowires.items():
                if (l, r) in output_variables:
                    output_variables[(l, r)].append(o)
                else:
                    output_variables[(l, r)] = [o]
            for ((l, r), os) in output_variables.items():
                if layer == l:
                    for i in range(len(os)):
                        v = os[i]
                        style = 'color="#ffffff", fillcolor="#ffffff", style="filled,solid"'
                        content += '\tm{}_{} [label="{}" {}];\n'.format(r + 1, self.columns + 1, v, style)

            content += '\n\t// Crossbar\n'
            # Important: The description of the grid is transposed when being rendered -> rows and columns are switched
            for r in range(self.rows):
                input_rows = list(map(lambda i: i[1], self.get_input_nanowires().values()))
                content += '\trank=same {\n'
                for c in range(self.columns):
                    if r not in input_rows and c == 0:
                        content += '\t\tm{}_{} -- m{}_{} [style=invis];\n'.format(r + 1, c, r + 1, c + 1)
                    else:
                        content += '\t\tm{}_{} -- m{}_{};\n'.format(r + 1, c, r + 1, c + 1)

                # TODO: Change layer
                if (0, r) in output_variables:
                    content += '\t\tm{}_{} -- m{}_{};\n'.format(r + 1, self.columns, r + 1, self.columns + 1)
                content += '\t}\n'

            for c in range(self.columns):
                content += '\t' + ' -- '.join(["m{}_{}".format(r + 1, c + 1) for r in range(self.rows)]) + '\n'

            content += '}'

            return {content}

    def __copy__(self):
        crossbar = MemristorCrossbar(self.rows, self.columns, self.layers)
        crossbar.matrix = copy.deepcopy(self.matrix)
        # for layer in range(self.layers):
        #     for r in range(self.rows):
        #         for c in range(self.columns):
        #             memristor = self.get_memristor(r, c)
        #             stuck_at_fault = memristor.stuck_at_fault
        #             permanent = memristor.permanent
        #             crossbar.set_memristor(r, c, self.get_memristor(r, c).literal, layer, stuck_at_fault=stuck_at_fault,
        #                                    permanent=permanent)
        crossbar.input_nanowires = self.input_nanowires
        # crossbar.input_variables = self.input_variables.copy()
        crossbar.output_nanowires = self.output_nanowires.copy()
        return crossbar

    def fix(self, atom: str, positive: bool) -> MemristorCrossbar:
        crossbar = copy.deepcopy(self)
        for l in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    memristor = self.get_memristor(r, c, l)
                    literal = memristor.literal
                    crossbar.set_memristor(r, c, literal.fix(atom, positive), l)
        return crossbar

    def find_equivalent_components(self) -> List:
        graph = self.graph()
        o_non_one_edges = [(u, v) for u, v, d in graph.edges(data=True) if
                           not (d['atom'] == 'True' and d['positive'])]
        graph.remove_edges_from(o_non_one_edges)

        equivalent = [list(f) for f in connected_components(graph)]
        return equivalent

    @staticmethod
    def _find_equivalent_row_or_column(equivalent: List, layer: int) -> List[List[int]]:
        """
        The axis 0 denotes one axis, and the axis 1 denotes the perpendicular axis of nanowires.
        :param equivalent:
        :param axis:
        :return:
        """
        f = [list(map(lambda w: int(w[3:]), filter(lambda x: x[1] == str(layer), equivalent_subset))) for equivalent_subset in equivalent]
        return f

    def get_equivalent_rows(self) -> List[List[int]]:
        equivalent = self.find_equivalent_components()
        return self._find_equivalent_row_or_column(equivalent, 0)

    def get_equivalent_columns(self) -> List[List[int]]:
        equivalent = self.find_equivalent_components()
        return self._find_equivalent_row_or_column(equivalent, 1)

    def get_ternary_matrix(self, layer: int = 0) -> np.ndarray:
        """
        TODO: Adapt to handle all layers, currently only handles one layer (layer 0)
        :param layer:
        :return:
        """
        ternary_matrix = np.empty((self.rows, self.columns))
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal == TRUE():
                    ternary_matrix[r, c] = 1
                elif self.get_memristor(r, c).literal == FALSE():
                    ternary_matrix[r, c] = -1
                else:
                    ternary_matrix[r, c] = 0
        return ternary_matrix

    def compress(self) -> MemristorCrossbar:
        ternary_matrix = self.get_ternary_matrix()
        equivalent_rows = self.get_equivalent_rows()
        compressed_rows = self._compress_equivalent_rows(ternary_matrix, equivalent_rows)
        row_compressed_crossbar = MemristorCrossbar.nd_array_to_crossbar(compressed_rows, equivalent_rows)
        equivalent_columns = row_compressed_crossbar.get_equivalent_columns()
        compressed_columns = self._compress_equivalent_columns(compressed_rows, equivalent_columns)
        compressed_crossbar = MemristorCrossbar.nd_array_to_crossbar(compressed_columns, equivalent_columns)
        return compressed_crossbar

    @staticmethod
    def nd_array_to_crossbar(nd_array: np.ndarray, equivalent_dimension: List[List[int]]) -> MemristorCrossbar:
        crossbar = MemristorCrossbar(nd_array.shape[0], nd_array.shape[1])
        for r in range(nd_array.shape[0]):
            for c in range(nd_array.shape[1]):
                if nd_array[r, c] == 1:
                    crossbar.set_memristor(r, c, TRUE())
                elif nd_array[r, c] == -1:
                    crossbar.set_memristor(r, c, FALSE())
                else:
                    # TODO: Fix
                    crossbar.set_memristor(r, c, LITERAL("x", True))
        return crossbar

    @staticmethod
    def _compress_equivalent_rows(ternary_matrix: np.ndarray, equivalent_rows: List) -> np.ndarray:
        rows = []
        for group in equivalent_rows:
            if len(group) > 0:
                a = np.amax(np.array(list(map(lambda x: ternary_matrix[x, :], group))), axis=0)
                rows.append([a])
        if rows:
            n = np.concatenate(rows)
        else:
            n = ternary_matrix
        return n

    @staticmethod
    def _compress_equivalent_columns(ternary_matrix, equivalent_columns: List) -> np.ndarray:
        cols = []
        for group in equivalent_columns:
            if len(group) > 0:
                a = np.amax(np.array(list(map(lambda x: ternary_matrix[:, x], group))), axis=0)
                cols.append([a])
        if cols:
            n = np.concatenate(cols).transpose()
        else:
            n = ternary_matrix
        return n

    def transpose(self) -> MemristorCrossbar:
        crossbar = MemristorCrossbar(self.columns, self.rows)
        for r in range(self.rows):
            for c in range(self.columns):
                crossbar.set_memristor(c, r, self.get_memristor(r, c).literal)

        # crossbar.input_variables = self.input_variables.copy()
        # crossbar.output_nanowires = self.output_nanowires.copy()
        return crossbar

    def instantiate(self, instance: dict) -> MemristorCrossbar:
        for layer in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    memristor = self.get_memristor(r, c, layer)
                    literal = memristor.literal
                    variable_name = literal.atom
                    positive = literal.positive
                    if variable_name != "True" and variable_name != "False":
                        if not memristor.stuck_at_fault:
                            if positive:
                                if instance[variable_name]:
                                    literal = LITERAL('True', True)
                                else:
                                    literal = LITERAL('False', False)
                            else:
                                if instance[variable_name]:
                                    literal = LITERAL('False', False)
                                else:
                                    literal = LITERAL('True', True)
                            self.set_memristor(r, c, literal, layer=layer)
        return self

    def eval(self, instance: Dict[str, bool], input_function: str = "1") -> Dict[str, bool]:
        # For all input nanowires different from a different input function than the given input function,
        # we set the selectorlines False to avoid any loops through these nanowires.
        for (other_input_function, (layer, input_nanowire)) in self.get_input_nanowires().items():
            if input_function != other_input_function:
                for c in range(self.columns):
                    self.set_memristor(input_nanowire, c, FALSE(), layer=layer)

        crossbar_copy = self.__copy__()
        crossbar_instance = crossbar_copy.instantiate(instance)
        graph = crossbar_instance.graph()
        true_edges = [(u, v) for u, v, d in graph.edges(data=True) if
                              not (d['atom'] == 'True' and d['positive'])]
        graph.remove_edges_from(true_edges)

        evaluation = dict()
        for (output_variable, (output_layer, output_nanowire)) in crossbar_instance.get_output_nanowires().items():
            source = "L{}_{}".format(output_layer, output_nanowire)
            input_layer, input_nanowire = crossbar_instance.get_input_nanowire(input_function)
            sink = "L{}_{}".format(input_layer, input_nanowire)
            evaluation[output_variable] = has_path(graph, source, sink)

        return evaluation
