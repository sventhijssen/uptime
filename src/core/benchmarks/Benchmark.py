from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any

from aux import config
from core.BooleanFunction import BooleanFunction
from core.IOInterface import IOInterface

if TYPE_CHECKING:
    from core.benchmarks.BLIFBenchmark import BLIFBenchmark
    from core.benchmarks.PLABenchmark import PLABenchmark
    from core.benchmarks.VerilogBenchmark import VerilogBenchmark


class Benchmark(BooleanFunction, IOInterface, ABC):
    """
    An abstract class to represent a benchmark. A benchmark is a multi-output Boolean function.
    """

    def __init__(self, file_path: Path = None, name: str = None):
        """
        A benchmark has optionally a file path and a name.
        :param file_path: Optionally, a file path for the benchmark.
        :param name: Optionally, a name for the benchmark.
        """
        super().__init__()
        self.file_path = file_path
        self._set_name(file_path, name)

    def get_log(self) -> Dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "inputs": len(self.get_input_variables()),
            "outputs": len(self.get_output_variables()),
            "wires": len(self.get_auxiliary_variables())
        }

    def _set_name(self, file_path: Path, name: str):
        """
        Sets the name for the benchmark based on the given file path or the given name.
        If no name is provided, then the stem of the file path is used as name for this benchmark.
        Otherwise, the given name is used for this benchmark.
        :param file_path: The file path of the benchmark.
        :param name: The name of the benchmark.
        :return:
        """
        if name is None:
            if file_path is None:
                self.name = ""
            else:
                self.name = file_path.stem
        else:
            self.name = name

    def _abc_conversion(self, original_filename: str, new_filename: str, write_cmd: str):
        import time
        import pexpect

        abc_original_path = config.abc_path.joinpath(original_filename)
        abc_new_path = config.abc_path.joinpath(new_filename)

        self.write(abc_original_path)

        time.sleep(2)

        process = pexpect.spawn(config.abc_cmd, cwd=str(config.abc_path))
        process.sendline('read "{}"; {} "{}";'.format(original_filename, write_cmd, new_filename))

        while not abc_new_path.exists():
            pass

        time.sleep(2)

        benchmark = Benchmark.read(abc_new_path)

        os.remove(abc_original_path)

        return benchmark

    @abstractmethod
    def to_blif(self) -> BLIFBenchmark:
        pass

    @abstractmethod
    def to_pla(self) -> PLABenchmark:
        pass

    @abstractmethod
    def to_verilog(self) -> VerilogBenchmark:
        pass
