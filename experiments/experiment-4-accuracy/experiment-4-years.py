import os
from pathlib import Path


max_defects = 600

current_path = Path(os.getcwd())
hours_filepath = current_path.parent.joinpath("experiment-3-years").joinpath("hours").joinpath("simulation_1").joinpath("hours.csv")
collect_filepath = current_path.joinpath("years.csv")

years = []
with open(hours_filepath, 'r') as f:
    for line in f.readlines():
        h = float(line)
        y = h / 8760
        years.append(y)

content = ""
for i in range(1, len(years)):
    years[i] = years[i - 1] + years[i]
    content += "{}\n".format(years[i])

with open(collect_filepath, 'w') as f:
    f.write(content)
