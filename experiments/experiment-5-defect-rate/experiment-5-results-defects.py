import os
from pathlib import Path


benchmark_name = "frg1"

max_defects = 800
defect_rates = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]

current_path = Path(os.getcwd())
defect_filepath = current_path.joinpath("results_hours.csv")
collect_filepath = current_path.joinpath("results_defects.csv")

content = ""
for defect_rate in defect_rates:

    crossbar_design_path = current_path.joinpath("crossbar-designs").joinpath("defect_rate_{}".format(defect_rate))

    best_defects = 0
    for file in os.listdir(crossbar_design_path):

        [filename, extension] = os.path.splitext(file)

        if extension == ".xbar":
            [_, raw_defects] = filename.split("_")
            defects = int(raw_defects)
            if defects > best_defects:
                best_defects = defects

    content += "{}\n".format(best_defects)

with open(collect_filepath, 'w') as f:
    f.write(content)

