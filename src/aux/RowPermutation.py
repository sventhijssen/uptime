import time
from typing import Set, Dict, Tuple

import numpy as np
from pulp import LpVariable, LpInteger, CPLEX_CMD, LpProblem, LpMinimize, lpSum, LpStatusInfeasible, value, LpStatus

from aux import config
from exceptions.AssignmentError import AssignmentError
from exceptions.InfeasibleSolutionException import InfeasibleSolutionException
from aux.PermutationStrategy import PermutationStrategy
from core.expressions.BooleanExpression import LITERAL
from core.crossbars.MemristorCrossbar import MemristorCrossbar


class RowPermutation(PermutationStrategy):

    def __init__(self):
        super().__init__()

    def _find_assignment_errors(self, design: MemristorCrossbar, crossbar: MemristorCrossbar, offset: int) -> Set[Tuple[int, int]]:
        start_time = time.time()

        errors = set()
        for r in range(design.rows):
            for rr in range(crossbar.rows):
                for c in range(design.columns):
                    crossbar_literal = crossbar.get_memristor(rr, c + offset).literal
                    design_literal = design.get_memristor(r, c).literal
                    if crossbar_literal == LITERAL("x", True):
                        continue
                    elif crossbar_literal != design_literal:
                        errors.add((r, rr))
                        break

        end_time = time.time()

        self.error_time = end_time - start_time

        return errors

    def _find_permutation(self, design: MemristorCrossbar, crossbar: MemristorCrossbar, errors: Set) -> Dict:
        start_time = time.time()

        # Variables
        vars_r = LpVariable.matrix("r", (range(design.rows), range(crossbar.rows)), lowBound=0, upBound=1, cat=LpInteger)
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
            prob += vars_e[error] == 1

        # Map each row in the design to one row in the crossbar
        for i in range(design.rows):
            prob += lpSum(vars_r[i]) == 1

        vars_r_t = np.array(vars_r).T.tolist()

        # Map at most one row from the design to a row in the crossbar
        for i in range(crossbar.rows):
            prob += lpSum(vars_r_t[i]) <= 1

        prob.solve(solver)

        if prob.status == LpStatusInfeasible:
            raise InfeasibleSolutionException("Infeasible solution.")

        # Print the value of the objective
        print("Error = ", value(prob.objective))
        config.log.add("Permutation error: {}\n".format(value(prob.objective)))

        assignment = dict()
        for v in prob.variables():
            if v.name[0] == "r" and int(round(v.varValue)) == 1:
                [_, original_row, faulty_row] = v.name.split("_")
                assignment[int(original_row)] = int(faulty_row)

        print("Status:", LpStatus[prob.status])

        end_time = time.time()

        self.ilp_time = end_time - start_time
        config.log.add("ILP time: {}\n".format(self.ilp_time))

        return assignment

    def assign(self, design: MemristorCrossbar, crossbar: MemristorCrossbar) -> Dict:
        config.log.add("Mapping method: ROW PERMUTATION\n")
        if design.rows > crossbar.rows or design.columns > crossbar.columns:
            raise AssignmentError(
                "Dimension of design ({}, {}) exceed dimensions of crossbar ({}, {})".format(design.rows,
                                                                                             design.columns,
                                                                                             crossbar.rows,
                                                                                             crossbar.columns))
        row_assignment = None
        offset = 0
        for c in range(crossbar.columns - design.columns + 1):
            errors = self._find_assignment_errors(design, crossbar, c)
            try:
                row_assignment = self._find_permutation(design, crossbar, errors)
                offset = c
                break
            except InfeasibleSolutionException:
                pass

        if row_assignment is None:
            config.log.add("Infeasible solution\n")
            raise InfeasibleSolutionException()

        assignment = dict()
        for (r, rr) in row_assignment.items():
            assignment[(0, r)] = (0, rr)
        for c in range(crossbar.columns):
            assignment[(1, c)] = (1, c + offset)

        return assignment
