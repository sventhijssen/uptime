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

    benchmark_path = current_path.joinpath(benchmark_name)

    ilp_time = 0
    for filename in os.listdir(benchmark_path):
        with open(benchmark_path.joinpath(filename), 'r') as f:
            for line in f.readlines():
                if "ILP time" in line:
                    [_, raw_value] = line.split(":")
                    ilp_time += float(raw_value)

    content += "{}\n".format(ilp_time)

with open(collect_filepath, 'w') as f:
    f.write(content)
