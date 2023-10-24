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

approach = "naive"

simulations = 10
defect = 0

current_path = Path(os.getcwd())
design_path = current_path.parent.joinpath("experiment-2-lifetime")

# For each benchmark
for benchmark_name in benchmark_names:

    benchmark_path = current_path.joinpath("crossbar-designs").joinpath(benchmark_name)

    if not benchmark_path.exists():
        os.mkdir(benchmark_path)

    design_filename = benchmark_name + ".xbar"
    design_filepath = design_path.joinpath("designs").joinpath(design_filename)

    # For each simulation
    for simulation in range(simulations):
        crossbar_path = design_path.joinpath("crossbars").joinpath("simulation_{}".format(simulation))

        if not crossbar_path.exists():
            os.mkdir(crossbar_path)

        crossbar_design_path = benchmark_path.joinpath("simulation_{}".format(simulation))

        if not crossbar_design_path.exists():
            os.mkdir(crossbar_design_path)

        log_filename = benchmark_name + "_{}.log".format(defect)
        log_filepath = crossbar_design_path.joinpath(log_filename)

        crossbar_filename = "crossbar_{}.xbar".format(defect)
        crossbar_filepath = crossbar_path.joinpath(crossbar_filename)

        crossbar_design_filename = "crossbar_{}.xbar".format(defect)
        crossbar_design_filepath = crossbar_design_path.joinpath(crossbar_filename)

        try:
            program = Program()
            Program.execute("new_log {} | read_xbar {} {} | map naive {} | write_xbar {}".format(log_filepath, benchmark_name, design_filepath, crossbar_filepath, crossbar_design_filepath))
        except Exception as e:
            print(e)
