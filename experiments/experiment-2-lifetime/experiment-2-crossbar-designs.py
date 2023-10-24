import os
from pathlib import Path

from exceptions.AssignmentError import AssignmentError
from exceptions.InfeasibleSolutionException import InfeasibleSolutionException
from cli.Program import Program


benchmark_names = [
    "5xp1",
    "clip",
    "cm163a",
    "cordic",
    "frg1",
    "misex1",
]

approaches = {
    "row": "-l 0",
    "row-column": "-l 0 1",
    "both": ""
}

simulations = 10
max_defects = 1000

current_path = Path(os.getcwd())

# For each approach
for approach, arguments in approaches.items():

    # For each benchmark
    for benchmark_name in benchmark_names:

        benchmark_path = current_path.joinpath("crossbar-designs").joinpath(approach).joinpath(benchmark_name)

        if not benchmark_path.exists():
            os.mkdir(benchmark_path)

        design_filename = benchmark_name + ".xbar"
        design_filepath = current_path.joinpath("designs").joinpath(design_filename)

        # For each simulation
        for simulation in range(simulations):
            crossbar_path = current_path.joinpath("crossbars").joinpath("simulation_{}".format(simulation))

            if not crossbar_path.exists():
                os.mkdir(crossbar_path)

            crossbar_design_path = benchmark_path.joinpath("simulation_{}".format(simulation))

            if not crossbar_design_path.exists():
                os.mkdir(crossbar_design_path)

            # Binary search based on:
            # https://www.geeksforgeeks.org/binary-search/
            stop_simulation = False
            low = 0
            high = max_defects
            while low <= high:
                mid = low + (high - low) // 2
                defect = mid

                log_filename = benchmark_name + "_{}.log".format(defect)
                log_filepath = crossbar_design_path.joinpath(log_filename)

                crossbar_filename = "crossbar_{}.xbar".format(defect)
                crossbar_filepath = crossbar_path.joinpath(crossbar_filename)

                crossbar_design_filename = "crossbar_{}.xbar".format(defect)
                crossbar_design_filepath = crossbar_design_path.joinpath(crossbar_filename)

                try:
                    program = Program()
                    Program.execute("new_log {} | read_xbar {} {} | map permutation {} {} | write_xbar {}".format(log_filepath, benchmark_name, design_filepath, crossbar_filepath, arguments, crossbar_design_filepath))

                    # Go up
                    low = mid + 1
                except (InfeasibleSolutionException, AssignmentError):
                    # Go down
                    high = mid - 1
                except Exception as e:
                    print(e)
