import os
from pathlib import Path


benchmark_names = [
    "5xp1",
    "clip",
    "cm163a",
    "cordic",
    "frg1",
    "misex1",
]

settings = ["positive", "positive-negative"]

current_path = Path(os.getcwd())
collect_filepath = current_path.joinpath("results.csv")

content = ""
for benchmark_name in benchmark_names:

    for setting in settings:

        log_filename = benchmark_name + ".log"
        log_filepath = current_path.joinpath(setting + "-results").joinpath(log_filename)

        with open(log_filepath, 'r') as f:
            for line in f.readlines():
                if line.startswith("Rows"):
                    [_, raw_value] = line.split(":")
                    rows = int(raw_value)

                if line.startswith("Columns"):
                    [_, raw_value] = line.split(":")
                    columns = int(raw_value)

                if line.startswith("Edges"):
                    [_, raw_value] = line.split(":")
                    edges = int(raw_value)

            content += "{}\t{}\t{}".format(rows, columns, edges)
        content += "\t"
    content += "\n"

with open(collect_filepath, 'w') as f:
    f.write(content)
