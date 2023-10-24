import os
import random
from pathlib import Path

from aux.BivariateGaussianDefectCrossbarGenerator import BivariateGaussianDefectCrossbarGenerator
from depr.CrossbarWriter import CrossbarWriter
from core.expressions.BooleanExpression import LITERAL

simulations = 1  # Set to the desired number for a Monte Carlo simulation
max_defects = 10  # Set to a high number such as 1000

current_path = Path(os.getcwd())
xbar_path = current_path.joinpath("xbars")

for simulation in range(simulations):
    simulation_path = xbar_path.joinpath("simulation_{}".format(simulation))
    os.mkdir(simulation_path)

    generator = BivariateGaussianDefectCrossbarGenerator(128, 128, 0.002, 5)
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
