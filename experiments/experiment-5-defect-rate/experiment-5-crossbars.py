import os
import random
from pathlib import Path

from aux.BivariateGaussianDefectCrossbarGenerator import BivariateGaussianDefectCrossbarGenerator
from depr.CrossbarWriter import CrossbarWriter
from core.expressions.BooleanExpression import LITERAL

max_defects = 800
defect_rates = [0] # [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10] # [0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.010]

current_path = Path(os.getcwd())

for defect_rate in defect_rates:
    simulation_path = current_path.joinpath("crossbars").joinpath("defect_rate_{}".format(defect_rate))
    os.mkdir(simulation_path)

    generator = BivariateGaussianDefectCrossbarGenerator(128, 128, defect_rate, 5)
    crossbar = list(generator.generate(1))[0]

    i = 0
    crossbar_filename = "crossbar_{}.xbar".format(i)
    crossbar_filepath = simulation_path.joinpath(crossbar_filename)

    cw = CrossbarWriter(crossbar, str(crossbar_filepath))
    cw.write()

    available = set()
    for r in range(crossbar.rows):
        for c in range(crossbar.columns):
            literal = crossbar.get_memristor(r, c).literal
            if literal != LITERAL("True", True) and literal != LITERAL("False", False):
                available.add((r, c))

    while i < max_defects:
        r, c = available.pop()
        if random.random() >= 0.5:
            literal = LITERAL("True", True)
        else:
            literal = LITERAL("False", False)
        crossbar.set_memristor(r, c, literal)

        crossbar_filename = "crossbar_{}.xbar".format(i)
        crossbar_filepath = simulation_path.joinpath(crossbar_filename)

        cw = CrossbarWriter(crossbar, str(crossbar_filepath))
        cw.write()

        i += 1
