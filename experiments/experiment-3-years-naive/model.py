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

simulations = 10

current_path = Path(os.getcwd())
collect_filepath = current_path.joinpath("results.csv")

content = ""

for benchmark_name in benchmark_names:

    years = []
    for simulation in range(simulations):

        simulation_path = current_path.joinpath("hours").joinpath(benchmark_name).joinpath("simulation_{}".format(simulation))

        best_defects = 1
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

    content += "{}\t{}\t{}\n".format(min_hours, mean_hours, max_hours)

with open(collect_filepath, 'w') as f:
    f.write(content)
