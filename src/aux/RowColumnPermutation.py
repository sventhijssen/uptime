import itertools
import time
from typing import Set, Dict, Tuple

import numpy as np
from pulp import LpVariable, LpInteger, CPLEX_CMD, LpProblem, LpMinimize, lpSum, LpStatusInfeasible, value, LpStatus

from aux import config
from exceptions.AssignmentError import AssignmentError
from exceptions.InfeasibleSolutionException import InfeasibleSolutionException
from aux.PermutationStrategy import PermutationStrategy
from core.expressions.BooleanExpression import LITERAL
from core.crossbars.Crossbar import Crossbar


class MultiLayerPermutation(PermutationStrategy):

    def _find_assignment_errors(self, design: Crossbar, crossbar: Crossbar) -> Set[Tuple[Tuple[int, int, int], Tuple[int, int, int]]]:
        start_time = time.time()

        design_all = set(itertools.product([l for l in range(design.layers)], [r for r in range(design.rows)],
                                           [c for c in range(design.columns)]))

        crossbar_on = crossbar.find(LITERAL('True', True))
        crossbar_off = crossbar.find(LITERAL('False', False))

        design_on = design.find(LITERAL('True', True))
        design_off = design.find(LITERAL('False', False))
        design_vars = design_all.difference(set(design_on).union(set(design_off)))

        errors_on = set()
        for crossbar_nanowire in crossbar_on:
            for design_nanowire in design_vars:
                errors_on.add((design_nanowire, crossbar_nanowire))
            for design_nanowire in design_off:
                errors_on.add((design_nanowire, crossbar_nanowire))

        errors_off = set()
        for crossbar_nanowire in crossbar_off:
            for design_nanowire in design_vars:
                errors_off.add((design_nanowire, crossbar_nanowire))
            for design_nanowire in design_on:
                errors_off.add((design_nanowire, crossbar_nanowire))

        errors = set()
        errors.update(errors_on)
        errors.update(errors_off)

        end_time = time.time()

        self.error_time = end_time - start_time
        config.log.add("Error time: {}\n".format(self.error_time))

        return errors

    def _find_permutation(self, design: Crossbar, crossbar: Crossbar, errors: Set) -> Dict:
        start_time = time.time()

        # Variables
        vars_r = LpVariable.matrix("r", (range(design.rows), range(crossbar.rows)), lowBound=0, upBound=1, cat=LpInteger)
        vars_c = LpVariable.matrix("c", (range(design.columns), range(crossbar.columns)), lowBound=0, upBound=1, cat=LpInteger)
        vars_e = LpVariable.dicts("e", errors, lowBound=0, upBound=0, cat=LpInteger)

        # Minimization problem
        solver = CPLEX_CMD(path=config.cplex_path, msg=False)
        prob = LpProblem("permutation", LpMinimize)

        # Objective function
        prob += lpSum(vars_e)

        # We only allow a solution such that all errors are masked. Hence, the sum of errors must be zero.
        prob += lpSum(vars_e) == 0

        # Errors
        # https://benalexkeen.com/linear-programming-with-python-and-pulp-part-6/
        for error in errors:
            design_nanowire, crossbar_nanowire = error
            _, i, j = design_nanowire
            _, k, l = crossbar_nanowire
            prob += vars_e[error] >= vars_r[i][k] + vars_c[j][l] - 1
            prob += vars_e[error] <= vars_r[i][k]
            prob += vars_e[error] <= vars_c[j][l]

        # Map each row/column in original
        for i in range(design.rows):
            prob += lpSum(vars_r[i]) == 1
        for j in range(design.columns):
            prob += lpSum(vars_c[j]) == 1

        vars_r_t = np.array(vars_r).T.tolist()
        vars_c_t = np.array(vars_c).T.tolist()

        # Map maximum 1 row/col from the design to each row/col in the crossbar
        for i in range(crossbar.rows):
            prob += lpSum(vars_r_t[i]) <= 1
        for i in range(crossbar.columns):
            prob += lpSum(vars_c_t[i]) <= 1

        prob.solve(solver)

        if prob.status == LpStatusInfeasible:
            config.log.add("Infeasible solution\n")
            raise InfeasibleSolutionException("Infeasible solution.")

        # Print the value of the objective
        print("Error = ", value(prob.objective))
        config.log.add("Permutation error: {}\n".format(value(prob.objective)))

        # TODO: Fix hardwired layers (1/0) for row and column
        assignment = dict()
        for v in prob.variables():
            if v.name[0] == "r" and int(round(v.varValue)) == 1:
                [_, design_row, crossbar_row] = v.name.split("_")
                assignment[(0, int(design_row))] = (0, int(crossbar_row))
            if v.name[0] == "c" and int(round(v.varValue)) == 1:
                [_, design_column, crossbar_column] = v.name.split("_")
                assignment[(1, int(design_column))] = (1, int(crossbar_column))

        print("Status:", LpStatus[prob.status])

        end_time = time.time()

        self.ilp_time = end_time - start_time
        config.log.add("ILP time: {}\n".format(self.ilp_time))

        return assignment

    def assign(self, design: Crossbar, crossbar: Crossbar) -> Dict:
        config.log.add("Mapping method: ROW AND COLUMN PERMUTATION\n")
        if design.rows > crossbar.rows or design.columns > crossbar.columns:
            raise AssignmentError("Dimension of design ({}, {}) exceed dimensions of crossbar ({}, {})".format(design.rows, design.columns, crossbar.rows, crossbar.columns))

        errors = self._find_assignment_errors(design, crossbar)
        assignment = self._find_permutation(design, crossbar, errors)

        return assignment
