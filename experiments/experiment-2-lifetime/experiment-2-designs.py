import os
from pathlib import Path

from cli.Program import Program


benchmark_names = [
    "5xp1",
    "clip",
    "cm163a",
    "cordic",
    "frg1",
    "misex1",
]

bdd = "sbdd"

current_path = Path(os.getcwd())

for benchmark_name in benchmark_names:
    log_filename = benchmark_name + ".log"
    log_filepath = current_path.joinpath("designs").joinpath(log_filename)

    benchmark_filename = benchmark_name + ".pla"
    benchmark_filepath = current_path.joinpath("benchmarks").joinpath(benchmark_filename)

    xbar_filename = benchmark_name + ".xbar"
    xbar_filepath = current_path.joinpath("designs").joinpath(xbar_filename)

    try:
        program = Program()
        Program.execute("new_log {} | read {} | {} -all -m | compact -vh | write_xbar {}".format(log_filepath, benchmark_filepath, bdd, xbar_filepath))
    except Exception as e:
        print(e)
