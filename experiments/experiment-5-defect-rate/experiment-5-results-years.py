import os
from pathlib import Path


current_path = Path(os.getcwd())
defect_filepath = current_path.joinpath("results_defects.csv")
hours_filepath = current_path.joinpath("hours.csv")
collect_filepath = current_path.joinpath("results_years.csv")

best_defects = []
with open(defect_filepath, 'r') as f:
    for line in f.readlines():
        best_defects.append(int(line))

with open(hours_filepath, 'r') as f:
    content = f.read()
    lines = content.splitlines()

content = ""
for best_defect in best_defects:
    t = 0
    for i in range(best_defect):
        t += float(lines[i])  # Hours
    y = t / 8760
    content += "{}\n".format(y)

with open(collect_filepath, 'w') as f:
    f.write(content)
