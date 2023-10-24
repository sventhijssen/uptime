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

simulation = 0
max_defects = 1000

current_path = Path(os.getcwd())
experiment_path = current_path.parent.joinpath("experiment-2-lifetime")

# For each benchmark
for benchmark_name in benchmark_names:

    design_filename = benchmark_name + ".xbar"
    design_filepath = experiment_path.joinpath("designs").joinpath(design_filename)

    crossbar_path = experiment_path.joinpath("crossbars").joinpath("simulation_{}".format(simulation))



    for defect in range(max_defects):
        log_filename = benchmark_name + "_{}.log".format(defect)
        log_filepath = current_path.joinpath(log_filename)

        crossbar_filename = "crossbar_{}.xbar".format(defect)
        crossbar_filepath = crossbar_path.joinpath(crossbar_filename)

        try:
            program = Program()
            Program.execute("new_log {} | read_xbar {} {} | map permutation {}".format(log_filepath, benchmark_name, design_filepath, crossbar_filepath))
        except (InfeasibleSolutionException, AssignmentError):
            break
        except Exception as e:
            print(e)
