from __future__ import annotations

import os
from functools import reduce
from pathlib import Path
from typing import Dict, Set, TYPE_CHECKING

from blifparser.blifparser import BlifParser
from blifparser.keywords.generic import Blif, Model, Inputs, Outputs, Names
from networkx import DiGraph, topological_sort

from aux import config
from core.DrawInterface import DrawInterface

from core.benchmarks.Benchmark import Benchmark
if TYPE_CHECKING:
    from core.benchmarks.PLABenchmark import PLABenchmark
from core.benchmarks.VerilogBenchmark import VerilogBenchmark


class BLIFBenchmark(Benchmark, DrawInterface):
    """
    A class to represent a BLIF benchmark.
    """

    file_extension = "blif"

    def __init__(self, blif: Blif, file_path: Path = None, name: str = None):
        """
        A BLIF benchmark has the BLIF content, and optionally a file path and a name.
        :param blif: The BLIF content.
        :param file_path: Optionally, a file path for the benchmark.
        :param name: Optionally, a name for the benchmark.
        """
        super().__init__(file_path, name)
        self.blif = blif
        self.functions = self._get_functions()

    def get_input_variables(self) -> Set[str]:
        return self.blif.inputs.inputs

    def get_output_variables(self) -> Set[str]:
        return self.blif.outputs.outputs

    def get_auxiliary_variables(self) -> Set[str]:
        output_variables = self.get_output_variables()
        auxiliary_variables = set()
        for bf in self.blif.booleanfunctions:
            if bf.output not in output_variables:
                auxiliary_variables.add(bf.output)
        return auxiliary_variables

    def model_name(self) -> str:
        """
        Returns the name of this BLIF benchmark.
        :return: The name of this BLIF benchmark.
        """
        if self.name:
            return self.name
        return self.blif.model.name

    @staticmethod
    def read(filepath: Path) -> BLIFBenchmark:
        """
        Reads a BLIF benchmark from the file with the given file path.
        :param filepath: The path of the BLIF file.
        :return: A BLIF benchmark.
        """
        parser = BlifParser(str(filepath))
        blif = parser.blif
        name = blif.model.name
        return BLIFBenchmark(blif, filepath, name)

    def to_string(self) -> str:
        content = ""
        content += ".model {}\n".format(self.model_name())
        content += ".inputs {}\n".format(" ".join(self.get_input_variables()))
        content += ".outputs {}\n".format(" ".join(self.get_output_variables()))
        for _, names in self.functions.items():
            content += str(names)
        content += ".end"
        return content

    def _get_functions(self) -> Dict[str, Names]:
        """
        Returns the wordlines of this BLIF benchmark.
        Here, a function is a dictionary with the output as key and the names as value.
        :return: A dictionary mapping the output to the names.
        """

        functions = dict()
        for bf in self.blif.booleanfunctions:
            functions[bf.output] = bf
        return functions

    def write(self, filepath: Path):
        content = self.to_string()

        with open(filepath, 'w') as f:
            f.write(content)

    def draw(self) -> Set[str]:
        raise NotImplementedError()
        # self.write(config.abc_path.joinpath(self.name + ".blif"))

    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        evaluations = dict()
        evaluations.update(instance)

        graph = self.to_data_flow_graph()
        for node in topological_sort(graph):
            # If the node is a primary input variable, then we must not evaluate it.
            if node in self.get_input_variables():
                continue
            else:
                names = self.functions.get(node)
                inputs = names.inputs
                truthtable = names.truthtable

                line_evaluations = []
                for line in truthtable:
                    line_evaluation = []
                    for i in range(len(inputs)):
                        variable = inputs[i]
                        variable_value = evaluations.get(variable)
                        raw_truthtable_value = line[i]

                        if raw_truthtable_value == "~" or raw_truthtable_value == "-":
                            continue
                        elif raw_truthtable_value == "0":
                            truthtable_value = False
                        elif raw_truthtable_value == "1":
                            truthtable_value = True
                        else:
                            raise Exception("Unknown truth value for input variable {}".format(variable))

                        line_evaluation.append(variable_value == truthtable_value)

                    line_evaluations.append(reduce(lambda x, y: x and y, line_evaluation))
                evaluation = reduce(lambda x, y: x or y, line_evaluations)
                evaluations[node] = evaluation

        # We remove the primary input variables and the auxiliary variables from the evaluation
        # such that we only retain the primary output variables.
        for input_variable in self.get_input_variables():
            evaluations.pop(input_variable)
        for auxiliary_variable in self.get_auxiliary_variables():
            evaluations.pop(auxiliary_variable)

        return evaluations

    def to_data_flow_graph(self) -> DiGraph():
        """
        Returns a data flow graph of this BLIF benchmark.
        The leaf nodes are the primary input variables, and the root nodes are the output variables.
        """
        graph = DiGraph()
        for output_variable, names in self.functions.items():
            graph.add_node(output_variable)
            for input_variable in names.inputs:
                graph.add_node(input_variable)
                graph.add_edge(input_variable, output_variable)
        return graph

    def split(self) -> Set[BLIFBenchmark]:
        """
        Splits this multi-output BLIF benchmark into a set of single-output BLIF benchmarks.
        """
        graph = self.to_data_flow_graph()

        subgraph = dict()
        for output_variable in self.get_output_variables():
            subgraph[output_variable] = {"input_variables": [], "wordlines": set(), "auxiliary_variables": []}
            q = [output_variable]
            while len(q) != 0:
                c = q.pop(0)
                if c in self.get_input_variables():
                    if c not in subgraph[output_variable]["input_variables"]:
                        subgraph[output_variable]["input_variables"].append(c)
                if c in self.get_auxiliary_variables() or c in self.get_auxiliary_variables():
                    if c not in subgraph[output_variable]["auxiliary_variables"]:
                        subgraph[output_variable]["auxiliary_variables"].append(c)

                for n, _ in graph.in_edges(c):
                    q.append(n)

        blif_benchmarks = set()
        for output_variable in self.get_auxiliary_variables():
            input_variables = subgraph[output_variable]["input_variables"]
            auxiliary_variables = subgraph[output_variable]["auxiliary_variables"]
            functions = dict()
            for variable, names in self.functions.items():
                if variable in auxiliary_variables:
                    functions[variable] = names

            blif = Blif()
            blif.model = Model(output_variable)
            blif.inputs = Inputs(" ".join(input_variables))
            blif.outputs = Outputs(output_variable)
            for variable, names in functions.items():
                if variable in auxiliary_variables:
                    blif.booleanfunctions.append(names)

            name = self.name + "_" + output_variable
            file_path = self.file_path.parent.joinpath(name + ".blif")

            blif_benchmark = BLIFBenchmark(blif, file_path, name)
            blif_benchmarks.add(blif_benchmark)

        return blif_benchmarks

    def to_blif(self) -> BLIFBenchmark:
        return self

    def to_pla(self) -> PLABenchmark:
        raise NotImplementedError()

    def to_verilog(self) -> VerilogBenchmark:
        self._abc_conversion("x.blif", "x.v", "write_verilog")
        verilog_benchmark = VerilogBenchmark.read(config.abc_path.joinpath("x.v"))
        abc_new_path = config.abc_path.joinpath("x.v")
        os.remove(abc_new_path)
        return verilog_benchmark
