from typing import List

from aux import config
from aux.BenchmarkReader import BenchmarkReader
from verf.Enumeration import Enumeration
from cli.Command import Command


class EnumerationCommand(Command):

    def __init__(self, args: List[str]):
        super(EnumerationCommand).__init__()
        if len(args) < 1:
            raise Exception("Specification not provided.")
        self.relative_specification_file_path = args[0]

        if "-s" in args:
            idx = args.index("-s")
            self.sampling_size = int(args[idx + 1])
        else:
            self.sampling_size = 0

    def execute(self):
        boolean_function_collection = config.context_manager.get_context()

        benchmark_reader = BenchmarkReader(self.relative_specification_file_path)
        specification = benchmark_reader.read()

        # assert isinstance(specification, VerilogBenchmark)

        enumeration = Enumeration(boolean_function_collection, specification)
        enumeration.is_equivalent(self.sampling_size)

        return False
