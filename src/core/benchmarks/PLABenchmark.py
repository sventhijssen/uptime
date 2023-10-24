from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Set, TYPE_CHECKING

from aux import config
from aux.PLAParser import PLA, PLAParser
from core.benchmarks.Benchmark import Benchmark

if TYPE_CHECKING:
    from core.benchmarks.BLIFBenchmark import BLIFBenchmark
from core.benchmarks.VerilogBenchmark import VerilogBenchmark


class PLABenchmark(Benchmark):
    """
    A class to represent a PLA benchmark.
    """

    file_extension = "pla"

    def __init__(self, pla: PLA, file_path: Path = None, name: str = None):
        """
        A PLA benchmark has the PLA content, and optionally a file path and auxiliary variables.
        :param pla: The PLA content.
        :param file_path: Optionally, a file path for the benchmark.
        :param name: Optionally, a name for the benchmark.
        """
        self.pla = pla
        super().__init__(file_path, name)

    def get_input_variables(self) -> Set[str]:
        return set(self.pla.inputs)

    def get_output_variables(self) -> Set[str]:
        return set(self.pla.outputs)

    def get_auxiliary_variables(self) -> Set[str]:
        return set()

    @staticmethod
    def read(filepath: Path) -> PLABenchmark:
        pla_parser = PLAParser(filepath)
        pla = pla_parser.pla
        return PLABenchmark(pla, file_path=filepath)

    def to_string(self) -> str:
        content = ""
        content += ".i {}\n".format(len(self.get_input_variables()))
        content += ".o {}\n".format(len(self.get_output_variables()))
        content += ".ilb {}\n".format(" ".join(self.pla.inputs))
        content += ".ob {}\n".format(" ".join(self.pla.outputs))
        content += ".p {}\n".format(len(self.pla.truthtable))
        for (input_vector, output_vector) in self.pla.truthtable:
            content += "{} {}\n".format("".join(input_vector), "".join(output_vector))
        content += ".e"

        return content

    def write(self, file_path: Path):
        content = self.to_string()
        with open(file_path, 'w') as f:
            f.write(content)

    def _satisfies(self, input_vector: List[str], instance: Dict[str, bool]) -> bool:
        """
        Auxiliary function for the evaluation of a PLA benchmark.
        Returns true if and only if the given input vector satisfies the given instance.
        An input vector satisfies the given instance when there is no conflict among the truth values.
        A conflict arises when we have a pair of (True, False) or (False, True) for the input vector and the instance,
        i.e. when input_variable_value != truth_table_value.
        :param input_vector: The input vector of the truth table of this PLA benchmark.
        :param instance: The given input vector.
        :return:
        """

        # We iterate over each input variable
        for i in range(len(self.pla.inputs)):
            input_variable = self.pla.inputs[i]

            # We get the truth value from the instance
            input_variable_value = instance.get(input_variable)
            # We get the truth value from the truth table of this PLA benchmark
            raw_truthtable_value = input_vector[i]

            if raw_truthtable_value == "~" or raw_truthtable_value == "-":
                continue
            elif raw_truthtable_value == "0":
                truth_table_value = False
            elif raw_truthtable_value == "1":
                truth_table_value = True
            else:
                raise Exception("Unknown truth value for input variable {}".format(input_variable))

            if input_variable_value != truth_table_value:
                return False

        return True

    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        evaluations = dict()

        # Initially, every output variable is False
        for output_variable in self.get_output_variables():
            evaluations[output_variable] = False

        # We iterate over the lines in the truth table
        for line in self.pla.truthtable:
            input_vector, output_vector = line

            # When the input vector of the line satisfies the given instance,
            # then we will determine the evaluation of the output variables
            # based on the corresponding output vector.
            if self._satisfies(input_vector, instance):

                # We iterate over the output variables in the line
                for i in range(len(self.pla.outputs)):
                    output_variable = self.pla.outputs[i]
                    raw_truthtable_value = output_vector[i]

                    # When we find that an output variable evaluates to true, we use it for the evaluation.
                    # An output variable evaluating to True cannot be undone, i.e. when the entry is False,
                    # we leave the evaluation untouched.
                    if raw_truthtable_value == "~" or raw_truthtable_value == "-":
                        continue
                    elif raw_truthtable_value == "0":
                        continue
                    elif raw_truthtable_value == "1":
                        evaluations[output_variable] = True
                    else:
                        raise Exception("Unknown truth value for input variable {}".format(output_variable))

        return evaluations

    def to_blif(self) -> BLIFBenchmark:
        raise NotImplementedError()

    def to_pla(self) -> PLABenchmark:
        return self

    def to_verilog(self) -> VerilogBenchmark:
        self._abc_conversion("x.pla", "x.v", "write_verilog")
        verilog_benchmark = VerilogBenchmark.read(config.abc_path.joinpath("x.v"))
        abc_new_path = config.abc_path.joinpath("x.v")
        os.remove(abc_new_path)
        return verilog_benchmark
