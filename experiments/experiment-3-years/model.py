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
experiment_path = current_path.parent.joinpath("experiment-2-lifetime")
collect_filepath = current_path.joinpath("results.csv")

content = ""

for benchmark_name in benchmark_names:

    for approach in approaches:

        benchmark_path = experiment_path.joinpath("crossbar-designs").joinpath(approach).joinpath(benchmark_name)

        years = []
        for simulation in range(simulations):

            crossbar_design_path = benchmark_path.joinpath("simulation_{}".format(simulation))
            simulation_path = current_path.joinpath("hours").joinpath("simulation_{}".format(simulation))

            best_defects = 0
            for file in os.listdir(crossbar_design_path):

                [filename, extension] = os.path.splitext(file)

                if extension == ".xbar":
                    [_, raw_defects] = filename.split("_")
                    defects = int(raw_defects)
                    if defects > best_defects:
                        best_defects = defects

            hours_filepath = simulation_path.joinpath("hours.csv")
            with open(hours_filepath, 'r') as f:
                t = 0
                i = 0
                for line in f.readlines():
                    if i == best_defects:
                        break
                    t += float(line)  # Hours
                    i += 1
                y = t / 8760
                years.append(y)

        min_hours = min(years)
        mean_hours = mean(years)
        max_hours = max(years)

        content += "{}\t{}\t{}\t".format(min_hours, mean_hours, max_hours)
    content += "\n"

with open(collect_filepath, 'w') as f:
    f.write(content)
