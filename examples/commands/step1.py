import os
from pathlib import Path

from cli.Program import Program

benchmark_name = "misex1"
bdd = "sbdd"

current_path = Path(os.getcwd())
designs_path = current_path.joinpath("designs")

log_filename = benchmark_name + ".log"
log_filepath = current_path.joinpath(log_filename)

benchmark_filename = benchmark_name + ".pla"
benchmark_filepath = current_path.joinpath(benchmark_filename)

xbar_filename = benchmark_name + ".xbar"
xbar_filepath = designs_path.joinpath(xbar_filename)

program = Program()
Program.execute("new_log {} | read {} | {} | compact | write_xbar {}".format(log_filepath, benchmark_filepath, bdd, xbar_filepath))
