from __future__ import annotations

from abc import abstractmethod, ABC
from pathlib import Path
from typing import Dict, Tuple, Set

import numpy as np
from networkx import Graph, set_node_attributes

from core.BooleanFunction import BooleanFunction
from core.DrawInterface import DrawInterface
from core.IOInterface import IOInterface
from core.crossbars.Memristor import Memristor
from core.expressions.BooleanExpression import LITERAL, FALSE, TRUE


class Crossbar(BooleanFunction, IOInterface, DrawInterface, ABC):
    """
    An abstract class to represent a crossbar.
    """

    def __init__(self, rows: int, columns: int, layers: int = 1, name: str = None, compressed: bool = False, default_literal: LITERAL = FALSE()):
        """
        Constructs a crossbar with the given dimensions x, y, and optionally z.
        :param rows: The number of memristors along the input and output nanowires.
        :param columns: The number of memristors orthogonal to the input and output nanowires.
        :param layers: The number of layers of memristors. The number of layers of nanowires is equal to the number
        of layers of memristors plus one. By default, the number of layers = 1.
        :param name: The name of the crossbar.
        :param compressed: Whether the crossbar is compressed or not. Do not use this for now.
        :param default_literal: The default literal to fill the crossbar. Usually False, but can be LITERAL("-", True).
        """
        super().__init__(name)
        self.rows = rows
        self.columns = columns
        self.layers = layers
        self.input_nanowires = dict()
        self.output_nanowires = dict()
        self.compressed = compressed
        self.default_literal = default_literal
        if self.compressed:
            self.matrix = None
        else:
            self.matrix = [[[Memristor(r, c, self.default_literal, l) for c in range(self.columns)] for r in range(self.rows)] for l in range(self.layers)]

    @staticmethod
    def read(filepath: Path) -> BooleanFunction:
        from core.crossbars.MemristorCrossbar import MemristorCrossbar
        return MemristorCrossbar.read(filepath)

    @abstractmethod
    def instantiate(self, instance: Dict) -> Crossbar:
        pass

    @abstractmethod
    def fix(self, atom: str, positive: bool) -> Crossbar:
        pass

    def get_input_nanowire(self, input_function: str) -> Tuple[int, int]:
        return self.input_nanowires[input_function]

    def get_input_nanowires(self) -> Dict[str, Tuple[int, int]]:
        """
        Returns a dictionary mapping the input of this crossbar to the input nanowires.
        An input nanowire is defined by a tuple of its layer and index.
        :return: A dictionary mapping an input (str) to a tuple of a layer (int) and an index (int).
        """
        return self.input_nanowires

    def get_output_nanowire(self, output_variable: str) -> Tuple[int, int]:
        """
        Returns the output nanowire of the given output variable.
        :param output_variable: The given output variable.
        :return: A tuple of the layer and the index.
        """
        return self.output_nanowires[output_variable]

    def get_output_nanowires(self) -> Dict[str, Tuple[int, int]]:
        """
        Returns a dictionary mapping the output variables of this crossbar to the output nanowire.
        An output nanowire is defined by a tuple of its layer and index.
        :return: A dictionary mapping an output variable (str) to a tuple of a layer (int) and an index (int).
        """
        return self.output_nanowires

    def set_input_nanowire(self, input_function: str, nanowire: int, layer: int = 0):
        self.input_nanowires[input_function] = (layer, nanowire)

    def set_output_nanowire(self, output_function: str, nanowire: int, layer: int = 0):
        self.output_nanowires[output_function] = (layer, nanowire)

    def graph(self, boolean_expression_representation: bool = False) -> Graph:
        """
        Returns a bipartite_graph representation based on the following analogy: nanowires in the crossbar correspond to nodes in the bipartite_graph, and memristors in the crossbar correspond to edges in the bipartite_graph.
        The resulting bipartite_graph is a multi-layered bipartite_graph. More specifically, the bipartite_graph is k-layered and bipartite.
        :param boolean_expression_representation: If true, the edge will be represented as a Boolean expression.
        Otherwise, as an atom and a truth value.
        :return: A k-layered bipartite bipartite_graph.
        """
        graph = Graph()
        for layer in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    memristor = self.get_memristor(r, c, layer=layer)
                    if layer % 2 == 0:
                        if boolean_expression_representation:
                            graph.add_edge("L{}_{}".format(layer, r), "L{}_{}".format(layer + 1, c),
                                           boolean_expression=memristor.literal)
                        else:
                            graph.add_edge("L{}_{}".format(layer, r), "L{}_{}".format(layer + 1, c),
                                           atom=memristor.literal.atom,
                                           positive=memristor.literal.positive)
                    else:
                        if boolean_expression_representation:
                            graph.add_edge("L{}_{}".format(layer, c), "L{}_{}".format(layer + 1, r),
                                           boolean_expression=memristor.literal)
                        else:
                            graph.add_edge("L{}_{}".format(layer, c), "L{}_{}".format(layer + 1, r),
                                           atom=memristor.literal.atom,
                                           positive=memristor.literal.positive)

        attributes = dict()
        for input_function, (layer, index) in self.get_input_nanowires().items():
            if "L{}_{}".format(layer, index) not in attributes:
                attributes["L{}_{}".format(layer, index)] = dict()
            attributes["L{}_{}".format(layer, index)]["input_function"] = input_function
        for output_function, (layer, index) in self.get_output_nanowires().items():
            if "L{}_{}".format(layer, index) not in attributes:
                attributes["L{}_{}".format(layer, index)] = dict()
            if "output_functions" not in attributes["L{}_{}".format(layer, index)]:
                attributes["L{}_{}".format(layer, index)]["output_functions"] = set()
            attributes["L{}_{}".format(layer, index)]["output_functions"].add(output_function)

        set_node_attributes(graph, attributes)

        return graph

    def find(self, literal: LITERAL) -> Set[Tuple[int, int, int]]:
        """
        Returns the positions of the given selectorlines occurring in this crossbar.
        :param literal: The given literal to find in this crossbar.
        :return: A list of positions (tuples) at which the literal occurs.
        """
        positions = set()
        for l in range(self.layers):
            for r in range(self.rows):
                for c in range(self.columns):
                    if self.get_memristor(r, c, layer=l).literal == literal:
                        positions.add((l, r, c))
        return positions

    def get_rows(self) -> int:
        """
        Returns the number of rows of this crossbar.
        :return: The number of rows of this crossbar.
        """
        return self.rows

    def get_columns(self) -> int:
        """
        Returns the number of columns of this crossbar.
        :return: The number of columns of this crossbar.
        """
        return self.columns

    def get_nanowire_layers(self) -> int:
        """
        Returns the number of layers (nanowires) of this crossbar.
        :return: The number of layers of nanowires in this crossbar.
        """
        return self.layers + 1

    def get_memristor_layers(self) -> int:
        """
        Returns the number of layers (memristors) of this crossbar.
        :return: The number of layers of memristors in this crossbar.
        """
        return self.layers

    def get_semiperimeter(self):
        """
        Returns the semiperimeter (number of wordlines + number of bitlines)
        of this crossbar.
        :return: The semiperimeter of this crossbar.
        """
        return self.get_rows() + self.get_columns()

    def get_area(self):
        """
        Returns the area (number of wordlines * number of bitlines) of this crossbar.
        :return: The area of this crossbar.
        """
        return self.get_rows() * self.get_columns()

    def get_volume(self):
        """
        Returns the volume (area * number of layers of memristors) of this crossbar.
        :return: The number of layers of this crossbar.
        """
        return self.get_area() * self.get_memristor_layers()

    def get_memristor(self, row: int, column: int, layer: int = 0) -> Memristor:
        """
        Returns the memristor at the given row and column.
        :param row: The given row in this crossbar.
        :param column: The given column in this crossbar.
        :param layer: The given layer in this crossbar.
        :return: The memristor at the given row and column.
        """
        return self.matrix[layer][row][column]

    def set_memristor(self, row: int, column: int, literal: LITERAL, layer: int = 0, stuck_at_fault: bool = False):
        """
        Assigns the given literal to the memristor at the given row and column.
        :param row: The given row in this crossbar.
        :param column: The given column in this crossbar.
        :param literal: The given literal to be assigned.
        :param layer: The given layer in this crossbar.
        :param stuck_at_fault:
        :return:
        """
        if self.compressed:
            return
        memristor = Memristor(row, column, literal, layer)
        self.matrix[layer][row][column] = memristor

    def flip_horizontal(self, layer: int = 0):
        """
        Flips the nanowire over its axis parallel to the nanowires in its layer (i.e. mirrors).
        :return:
        """
        self.matrix.reverse()

        for r in range(self.rows):
            for c in range(self.columns):
                memristor = self.get_memristor(r, c, layer=layer)
                self.set_memristor(r, c, memristor.literal, layer)

        outputs = dict()
        for (output_variable, (layer, row)) in self.get_output_nanowires().items():
            outputs[output_variable] = self.rows - 1 - row
        self.output_nanowires = outputs

    def flip_vertical(self):
        """
        Flips the nanowire of its axis parallel to the nanowires in its layer (i.e. mirrors).
        :param layer:
        :return:
        """
        for layer in range(self.layers):
            for r in range(self.rows):
                old_row = self.matrix[layer][r]
                new_row = old_row[::-1]
                for c in range(self.columns):
                    literal = new_row[c].literal
                    new_row[c] = Memristor(r, c, literal, layer)
                self.matrix[layer][r] = new_row

    def get_binary_matrix(self, layer: int = 0) -> np.ndarray:
        """
        TODO: Adapt to handle all layers, currently only handles one layer (layer 0)
        :param layer:
        :return:
        """
        binary_matrix = np.empty((self.rows, self.columns))
        for r in range(self.rows):
            for c in range(self.columns):
                if self.get_memristor(r, c).literal == TRUE():
                    binary_matrix[r, c] = 1
                elif self.get_memristor(r, c).literal == FALSE():
                    binary_matrix[r, c] = 0
                else:
                    raise Exception()
        return binary_matrix
