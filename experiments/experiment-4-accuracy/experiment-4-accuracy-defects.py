import os
from pathlib import Path


benchmark_name = "misex1"

approaches = ["row", "row-column", "both"]

simulations = 10
max_defects = 600

current_path = Path(os.getcwd())
collect_filepath = current_path.joinpath("results.csv")

results = []
# For each approach
for approach in approaches:

    benchmark_path = current_path.parent.joinpath("experiment-2-lifetime").joinpath("crossbar-designs").joinpath(approach).joinpath(benchmark_name)

    design_filename = benchmark_name + ".xbar"
    design_filepath = current_path.joinpath("designs").joinpath(design_filename)

    successes = [0 for _ in range(max_defects)]

    # For each simulation
    for simulation in range(simulations):
        crossbar_design_path = benchmark_path.joinpath("simulation_{}".format(simulation))

        best_defects = 0
        for file in os.listdir(crossbar_design_path):

            [filename, extension] = os.path.splitext(file)

            if extension == ".xbar":
                [_, raw_defects] = filename.split("_")
                defects = int(raw_defects)
                if defects > best_defects:
                    best_defects = defects

        for i in range(best_defects):
            successes[i] += 1

    results.append(successes)

# Based on: https://stackoverflow.com/questions/53250821/in-python-how-do-i-rotate-a-matrix-90-degrees-counterclockwise
rotated_results = [[results[j][i] for j in range(len(results))] for i in range(len(results[0]))]

content = ""
for i in range(len(rotated_results)):
    content += "{}\t{}\t{}\n".format(rotated_results[i][0]/simulations, rotated_results[i][1]/simulations, rotated_results[i][2]/simulations)

with open(collect_filepath, 'w') as f:
    f.write(content)
