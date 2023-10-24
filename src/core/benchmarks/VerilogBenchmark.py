from __future__ import annotations

from pathlib import Path
from typing import Dict, TYPE_CHECKING, Set

from networkx import DiGraph, topological_sort
from z3 import Bool

from aux.VerilogParser import VerilogModule, VerilogParser, VerilogFormula
from core.benchmarks.Benchmark import Benchmark
from core.benchmarks.Formula import Formula
from core.expressions.BooleanExpression import OR, LITERAL

if TYPE_CHECKING:
    from core.benchmarks.BLIFBenchmark import BLIFBenchmark
    from core.benchmarks.PLABenchmark import PLABenchmark


class VerilogBenchmark(Benchmark):
    """
    A class to represent a Verilog benchmark.
    """

    file_extension = "v"

    def __init__(self, verilog: VerilogModule, file_path: Path = None, name: str = None):
        """
        A Verilog benchmark has the Verilog content, and optionally a file path and name.
        :param verilog: The Verilog content.
        :param file_path: Optionally, a file path for the benchmark.
        :param name: Optionally, a name for the benchmark.
        """
        super().__init__(file_path, name)
        self.verilog = verilog

    def __copy__(self):
        return VerilogBenchmark(self.verilog.copy(), self.file_path, self.name)

    def get_input_variables(self) -> Set[str]:
        return self.verilog.inputs

    def get_output_variables(self) -> Set[str]:
        return self.verilog.outputs

    def get_auxiliary_variables(self) -> Set[str]:
        return self.verilog.wires

    # TODO: Fix ;)
    def fix(self, atom: str, positive: bool) -> VerilogBenchmark:
        for output_variable, formula in self.verilog.functions.items():
            print(output_variable)

    def negate(self) -> VerilogBenchmark:
        """
        Returns the negation of this benchmark.
        """

        negated_functions = dict()
        for variable, formula in self.verilog.functions.items():
            if variable in self.get_output_variables():
                negated_formula = formula.negate()
                negated_functions[variable] = negated_formula
            else:
                negated_functions[variable] = formula

        name = self.name + "_neg"
        input_variables = self.get_input_variables()
        output_variables = self.get_output_variables()
        auxiliary_variables = self.get_auxiliary_variables()
        file_path = self.file_path

        verilog = VerilogModule()
        verilog.module_name = name
        verilog.inputs = input_variables
        verilog.wires = auxiliary_variables
        verilog.outputs = output_variables
        verilog.functions = negated_functions

        return VerilogBenchmark(verilog, file_path, name)

    @staticmethod
    def read(filepath: Path) -> VerilogBenchmark:
        verilog_parser = VerilogParser(filepath)
        verilog = verilog_parser.verilog_module
        return VerilogBenchmark(verilog, filepath, verilog.module_name)

    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        evaluations = dict()
        evaluations.update(instance)

        graph = self._to_data_flow_graph()
        for node in topological_sort(graph):
            # If the node is a primary input variable, then we must not evaluate it.
            if node in self.get_input_variables():
                continue
            else:
                formula = self.verilog.functions.get(node)
                evaluations[node] = formula.eval(evaluations).get(node)

        # We remove the primary input variables and the auxiliary variables from the evaluation
        # such that we only retain the primary output variables.
        for input_variable in self.get_input_variables():
            evaluations.pop(input_variable)
        for auxiliary_variable in self.get_auxiliary_variables():
            evaluations.pop(auxiliary_variable)

        return evaluations

    def _to_data_flow_graph(self) -> DiGraph():
        """
        Returns a data flow graph of this Verilog benchmark.
        The leaf nodes are the primary input variables, and the root nodes are the output variables.
        """
        graph = DiGraph()
        for output_variable, formula in self.verilog.functions.items():
            graph.add_node(output_variable)
            for input_variable in formula.get_input_variables():
                graph.add_node(input_variable)
                graph.add_edge(input_variable, output_variable)
        return graph

    def to_string(self) -> str:
        input_variables = ", ".join(sorted(self.get_input_variables()))
        output_variables = ", ".join(sorted(self.get_output_variables()))

        content = "module {} (".format(self.verilog.module_name)
        content += "\n"
        content += "\t{}, {});".format(input_variables, output_variables)
        content += "\n"
        content += "\tinput {};".format(input_variables)
        content += "\n"
        content += "\toutput {};".format(output_variables)
        content += "\n"
        if len(self.get_auxiliary_variables()) > 0:
            auxiliary_variables = ", ".join(sorted(self.get_auxiliary_variables()))
            content += "\twire {};".format(auxiliary_variables)
            content += "\n"
        for function_name, formula in self.verilog.functions.items():
            content += "\tassign {};".format(formula)
            content += "\n"
        content += "endmodule"
        return content

    def write(self, file_path: Path):
        content = self.to_string()

        with open(file_path, 'w') as f:
            f.write(content)

    def collapse(self) -> VerilogBenchmark:
        data_flow_graph = self._to_data_flow_graph()  # From primary input variable to output variable
        node_to_expression = dict()
        for node in topological_sort(data_flow_graph):
            if len(data_flow_graph.in_edges(node)) == 0:
                node_to_expression[node] = LITERAL(node, True)
            else:
                formula = self.verilog.functions.get(node)
                boolean_expression = formula.verilog.boolean_expression
                # print("Node: {}".format(node))
                # print(boolean_expression)
                for (child_node, _) in data_flow_graph.in_edges(node):
                    child_expression = node_to_expression.get(child_node)
                    # print("\t{} -> \t{}".format(child_node, child_expression))
                    boolean_expression = boolean_expression.substitute(LITERAL(child_node, True), child_expression)
                node_to_expression[node] = boolean_expression

        functions = dict()
        for output_variable in self.get_output_variables():
            verilog = VerilogFormula()
            verilog.output = output_variable
            verilog.boolean_expression = node_to_expression.get(output_variable)
            formula = Formula(verilog)
            functions[output_variable] = formula

        verilog_module = VerilogModule()
        verilog_module.module_name = self.verilog.module_name
        verilog_module.inputs = self.verilog.inputs
        verilog_module.outputs = self.verilog.outputs
        verilog_module.wires = set()
        verilog_module.functions = functions

        return VerilogBenchmark(verilog_module)

    def to_z3(self) -> Dict[str, Bool]:
        verilog_benchmark = self.collapse()
        functions = dict()
        for output_variable, formula in verilog_benchmark.verilog.functions.items():
            functions[output_variable] = formula.verilog.boolean_expression.to_z3()
        return functions

    def to_blif(self, collapse: bool = True) -> BLIFBenchmark:
        verilog_filename = self.name + "." + VerilogBenchmark.file_extension
        blif_filename = self.name + "." + BLIFBenchmark.file_extension
        return self._abc_conversion(verilog_filename, blif_filename, "write_verilog")

    def to_pla(self) -> PLABenchmark:
        verilog_filename = self.name + "." + VerilogBenchmark.file_extension
        pla_filename = self.name + "." + PLABenchmark.file_extension
        return self._abc_conversion(verilog_filename, pla_filename, "write_pla")

    def to_verilog(self) -> VerilogBenchmark:
        return self
