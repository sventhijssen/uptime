from pathlib import Path

from aux import config
from depr.CrossbarReader import CrossbarReader
from core.BooleanFunctionCollection import BooleanFunctionCollection
from core.benchmarks.BLIFBenchmark import BLIFBenchmark
from core.benchmarks.PLABenchmark import PLABenchmark
from core.benchmarks.VerilogBenchmark import VerilogBenchmark
from core.crossbars.Crossbar import Crossbar
from core.decision_diagrams.BDDCollection import BDDCollection


class BenchmarkReader:
    """
    A class to read a benchmark from a file. This class disambiguates the file readers based on the file extension.
    """

    def __init__(self, relative_file_path: str):
        """

        :param relative_file_path:
        """
        self.file_path = Path(relative_file_path)

    def read(self, deprecated: bool = False) -> BooleanFunctionCollection:
        """
        Reads the benchmark
        :return:
        """
        file_name = self.file_path.name
        [benchmark_name, file_extension] = file_name.split('.')

        print("Started reading benchmark \"{}\"".format(benchmark_name))

        if file_extension == "pla":
            benchmark = PLABenchmark.read(config.root.joinpath(self.file_path))
            return BooleanFunctionCollection({benchmark})
        elif file_extension == "blif":
            benchmark = BLIFBenchmark.read(config.root.joinpath(self.file_path))
            return BooleanFunctionCollection({benchmark})
        elif file_extension == "v":
            benchmark = VerilogBenchmark.read(config.root.joinpath(self.file_path))
            config.log.add_json(benchmark.get_log())
            return BooleanFunctionCollection({benchmark})
        elif file_extension == "bdd":
            bdd_collection = BDDCollection.read(config.root.joinpath(self.file_path))
            return bdd_collection
        elif file_extension == "xbar":
            if deprecated:
                crossbar_reader = CrossbarReader(str(config.root.joinpath(self.file_path)))
                benchmark = crossbar_reader.read()
                config.log.add_json(benchmark.get_log())
            else:
                benchmark = Crossbar.read(config.root.joinpath(self.file_path))
            return BooleanFunctionCollection({benchmark})
        else:
            raise Exception("Unsupported file type.")

        print("Stopped reading benchmark")
        print()

        return benchmark
