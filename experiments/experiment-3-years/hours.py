import math
import os
import random
from pathlib import Path


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
max_defects = 1000
# p = 1-e^(-λ*T/10^9)
# => T = -ln(p) * 10^9 / λ
lmbda = math.pow(10, 6)

current_path = Path(os.getcwd())
experiment_path = current_path.parent.joinpath("experiment-2-lifetime")

content = ""

for simulation in range(simulations):

    simulation_path = current_path.joinpath("hours").joinpath("simulation_{}".format(simulation))

    if not simulation_path.exists():
        os.mkdir(simulation_path)

    for i in range(max_defects):
        r = random.random()
        if r >= 0.5:
            t = math.log(r) * math.pow(10, 9) / (-lmbda)
            content += "{}\n".format(t)

    hours_filepath = simulation_path.joinpath("hours.csv")
    with open(hours_filepath, 'w') as f:
        f.write(content)
