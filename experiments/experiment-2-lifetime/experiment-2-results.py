import os
from pathlib import Path
from statistics import mean

benchmark_names = [
    "5xp1",
    "clip",
    "cm163a",
    "cordic",
    "frg1",
    "misex1",
]

approaches = ["row", "row-column", "both"]

simulations = 10

current_path = Path(os.getcwd())
collect_filepath = current_path.joinpath("results.csv")

content = ""

for benchmark_name in benchmark_names:

    for approach in approaches:

        benchmark_path = current_path.joinpath("crossbar-designs").joinpath(approach).joinpath(benchmark_name)

        simulation_defects = []
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

            simulation_defects.append(best_defects)

        min_defects = min(simulation_defects)
        mean_defects = mean(simulation_defects)
        max_defects = max(simulation_defects)

        content += "{}\t{}\t{}\t".format(min_defects, mean_defects, max_defects)
    content += "\n"

with open(collect_filepath, 'w') as f:
    f.write(content)
