import os
from pathlib import Path

from exceptions.AssignmentError import AssignmentError
from exceptions.InfeasibleSolutionException import InfeasibleSolutionException
from cli.Program import Program


benchmark_name = "frg1"

max_defects = 800
defect_rates = [0] # [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]

current_path = Path(os.getcwd())

for defect_rate in defect_rates:

    benchmark_path = current_path.joinpath("crossbar-designs")

    design_filename = benchmark_name + ".xbar"
    design_filepath = current_path.parent.joinpath("experiment-2-lifetime").joinpath("designs").joinpath(design_filename)

    crossbar_path = current_path.joinpath("crossbars").joinpath("defect_rate_{}".format(defect_rate))

    crossbar_design_path = benchmark_path.joinpath("defect_rate_{}".format(defect_rate))

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
            Program.execute("new_log {} | read_xbar {} {} | map permutation {} | write_xbar {}".format(log_filepath, benchmark_name, design_filepath, crossbar_filepath, crossbar_design_filepath))

            # Go up
            low = mid + 1
        except (InfeasibleSolutionException, AssignmentError):
            # Go down
            high = mid - 1
        except Exception as e:
            print(e)
