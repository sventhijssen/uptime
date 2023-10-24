from aux import config
from aux.BenchmarkReader import BenchmarkReader
from cli.Command import Command


class ReadCommand(Command):

    def __init__(self, args):
        super(ReadCommand).__init__()
        if len(args) < 1:
            raise Exception("No file defined.")
        if "-depr" in args:
            self.deprecated = True
            offset = 1
        else:
            self.deprecated = False
            offset = 0

        self.relative_file_path = args[offset]

    def execute(self):
        benchmark_reader = BenchmarkReader(self.relative_file_path)
        boolean_function_collection = benchmark_reader.read(self.deprecated)
        config.context_manager.add_context("", boolean_function_collection)

        return False
