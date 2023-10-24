import os
from pathlib import Path

from cli.Program import Program


benchmark_name = "misex1"

# Possible data layout reorganization approaches:
# - naive
# - permutation -l 0 (row-wise)
# - permutation -l 1  (column-wise)
# - permutation (simultaneous rows and columns)

strategies = ["naive", "permutation -l 0", "permutation -l 0 1", "permutation"]

simulations = 1  # Set to same value as in step 2
max_defects = 10  # Set to a high number such as 1000

current_path = Path(os.getcwd())
xbar_path = current_path.joinpath("xbars")
design_path = current_path.joinpath("designs")
mapped_path = current_path.joinpath("mapped")
log_path = current_path.joinpath("logs")

design_filename = benchmark_name + ".xbar"
design_filepath = design_path.joinpath(design_filename)

# For each simulation
for strategy in strategies:
    mapped_strategy_path = mapped_path.joinpath(strategy.replace(" ", ""))
    log_strategy_path = log_path.joinpath(strategy.replace(" ", ""))

    if not mapped_strategy_path.exists():
        os.mkdir(mapped_strategy_path)

    if not log_strategy_path.exists():
        os.mkdir(log_strategy_path)

    for simulation in range(simulations):
        simulation_path = xbar_path.joinpath("simulation_{}".format(simulation))
        mapped_simulation_path = mapped_strategy_path.joinpath("simulation_{}".format(simulation))
        log_simulation_path = log_strategy_path.joinpath("simulation_{}".format(simulation))

        if not mapped_simulation_path.exists():
            os.mkdir(mapped_simulation_path)
        if not log_simulation_path.exists():
            os.mkdir(log_simulation_path)

        for defect in range(max_defects):
            crossbar_filepath = simulation_path.joinpath("crossbar_{}.xbar".format(defect))
            mapped_filepath = mapped_simulation_path.joinpath("crossbar_{}.xbar".format(defect))
            log_filename = benchmark_name + "_{}.log".format(defect)
            log_filepath = log_simulation_path.joinpath(log_filename)

            Program.execute("new_log {} | read -depr {} | map {} {} | write_xbar {}".format(log_filepath, design_filepath, strategy, crossbar_filepath, mapped_filepath))
