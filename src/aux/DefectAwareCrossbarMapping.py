import itertools
import time
from typing import List, Tuple

import numpy as np
from pulp import LpVariable, CPLEX_CMD, LpInteger, LpMinimize, LpProblem, lpSum, LpStatus, value, LpStatusInfeasible

from aux import config
from exceptions.InfeasibleSolutionException import InfeasibleSolutionException
from core.expressions.BooleanExpression import LITERAL
from core.crossbars.MemristorCrossbar import MemristorCrossbar


class AssignmentError(Exception):
    pass


def _get_memristor_errors(original: MemristorCrossbar, faulty: MemristorCrossbar) -> List:
    original_all = set(itertools.product([r for r in range(original.rows)], [c for c in range(original.columns)]))

    faulty_true = faulty.find(LITERAL('True', True))
    faulty_false = faulty.find(LITERAL('False', False))

    original_true = original.find(LITERAL('True', True))
    original_false = original.find(LITERAL('False', False))
    original_vars = original_all.difference(set(original_true).union(set(original_false)))

    errors_true = []
    for (k, l) in faulty_true:
        for (i, j) in original_vars:
            errors_true.append((i, j, k, l))
        for (i, j) in original_false:
            errors_true.append((i, j, k, l))

    errors_false = []
    for (k, l) in faulty_false:
        for (i, j) in original_vars:
            errors_false.append((i, j, k, l))
        for (i, j) in original_true:
            errors_false.append((i, j, k, l))

    all_errors = errors_true.copy()
    all_errors.extend(errors_false)

    return all_errors


class DefectAwareCrossbarMapping:

    def __init__(self, design: MemristorCrossbar, crossbar: MemristorCrossbar):
        self.design = design
        self.crossbar = crossbar
        self.compressed_crossbar = self.crossbar.compress()
        self.crossbar_design = self.crossbar.__copy__()
        self.row_assignment = dict()
        self.column_assignment = dict()
        self.error = -1

        self.start_time_total = None
        self.end_time_total = None

        self.start_time_compression = None
        self.end_time_compression = None

        self.start_time_errors = None
        self.end_time_errors = None

        self.start_time_ilp = None
        self.end_time_ilp = None

    def map(self):
        self.start_time_total = time.time()

        # TODO: Permute all input nanowires
        self.start_time_compression = time.time()
        self.compressed_crossbar = self.crossbar.compress()
        self.end_time_compression = time.time()

        # From the compressed faulty crossbar, apply a greedy assigment
        # to the possible rows and columns in the faulty crossbar
        equivalent_rows_lst = list(filter(lambda x: len(x) != 0, self.crossbar.get_equivalent_rows()))
        equivalent_rows = set([item for elem in equivalent_rows_lst for item in elem])
        equivalent_columns_lst = list(filter(lambda x: len(x) != 0, self.crossbar.get_equivalent_columns()))
        equivalent_columns = set([item for elem in equivalent_columns_lst for item in elem])
        all_rows = set([row for row in range(self.crossbar.rows)])
        all_columns = set([column for column in range(self.crossbar.columns)])
        missing_rows = list(map(lambda r: [r], all_rows - equivalent_rows))
        missing_columns = list(map(lambda c: [c], all_columns - equivalent_columns))
        equivalent_rows_lst.extend(missing_rows)
        equivalent_columns_lst.extend(missing_columns)

        try:
            self._assign(self.design, self.compressed_crossbar, equivalent_rows_lst)
        except AssignmentError as e:
            raise e
        assignments = dict()

        for r in range(self.design.rows):
            for c in range(self.design.columns):
                # Get the assignment of the row and column in the original crossbar
                # to the row and column in the compressed faulty crossbar
                assigned_row = self.row_assignment[r]
                assigned_column = self.column_assignment[c]

                r_options = equivalent_rows_lst[assigned_row]
                c_options = equivalent_columns_lst[assigned_column]

                # Based on: https://www.geeksforgeeks.org/python-program-to-get-all-unique-combinations-of-two-lists/
                options = list(itertools.product(r_options, c_options))

                for (r_option, c_option) in options:
                    original_literal = self.design.get_memristor(r, c).literal
                    option_literal = self.crossbar.get_memristor(r_option, c_option).literal
                    if original_literal == LITERAL("True", True) and option_literal != LITERAL("False", False):
                        assignments[(r, c)] = (r_option, c_option)
                        self.crossbar_design.set_memristor(r_option, c_option, original_literal)
                        break
                    elif original_literal == LITERAL("False", False) and option_literal != LITERAL("True", True):
                        assignments[(r, c)] = (r_option, c_option)
                        self.crossbar_design.set_memristor(r_option, c_option, original_literal)
                        break
                    elif original_literal != LITERAL("True", True) and original_literal != LITERAL("False", False) and option_literal != LITERAL("True", True) and option_literal != LITERAL("False", False):
                        assignments[(r, c)] = (r_option, c_option)
                        self.crossbar_design.set_memristor(r_option, c_option, original_literal)
                        break

        # print(self.row_assignment)
        # print(self.column_assignment)
        # print(assignments)

        # Outputs have permuted
        for (output_variable, (layer, row)) in self.design.get_output_nanowires().items():
            self.crossbar_design.set_output_nanowire(output_variable, equivalent_rows_lst[self.row_assignment[row]][0], layer)
            # self.crossbar_design.output_nanowires[output_variable] = equivalent_rows_lst[self.row_assignment[row]][0]
        self.crossbar_design.input_variables = self.design.input_variables

        # Input(s) have permuted
        for (input_function, (layer, row)) in self.design.get_input_nanowires().items():
            self.crossbar_design.set_input_nanowire(input_function, equivalent_rows_lst[self.row_assignment[row]][0], layer)
            # self.crossbar_design.input_nanowires[input_function] = equivalent_rows_lst[self.row_assignment[nanowire]][0]

        for r in range(self.crossbar_design.rows):
            for c in range(self.crossbar_design.columns):
                if self.crossbar_design.get_memristor(r, c).literal == LITERAL("-", True):
                    self.crossbar_design.set_memristor(r, c, LITERAL("False", False))
        self.end_time_total = time.time()

        return self.crossbar_design

    def _assign(self, design: MemristorCrossbar, crossbar: MemristorCrossbar, equivalent_rows: List) -> Tuple[dict, dict]:
        if design.rows > crossbar.rows or design.columns > crossbar.columns:
            raise AssignmentError("Dimension of design ({}, {}) exceed dimensions of crossbar ({}, {})".format(design.rows, design.columns, crossbar.rows, crossbar.columns))

        self.start_time_errors = time.time()
        memristor_errors = _get_memristor_errors(design, crossbar)
        self.end_time_errors = time.time()

        self.start_time_ilp = time.time()
        # Variables
        vars_r = LpVariable.matrix("r", (range(design.rows), range(crossbar.rows)), lowBound=0, upBound=1, cat=LpInteger)
        vars_c = LpVariable.matrix("c", (range(design.columns), range(crossbar.columns)), lowBound=0, upBound=1, cat=LpInteger)
        vars_e = LpVariable.dicts("e", memristor_errors, lowBound=0, upBound=1, cat=LpInteger)
        # Minimization problem
        solver = CPLEX_CMD(path=config.cplex_path, msg=False)
        prob = LpProblem("VC", LpMinimize)

        # Objective function
        prob += lpSum(vars_e)

        prob += lpSum(vars_e) == 0

        # Errors
        # https://benalexkeen.com/linear-programming-with-python-and-pulp-part-6/
        for e in range(len(memristor_errors)):
            (i, j, k, l) = memristor_errors[e]
            prob += vars_e[memristor_errors[e]] >= vars_r[i][k] + vars_c[j][l] - 1
            prob += vars_e[memristor_errors[e]] <= vars_r[i][k]
            prob += vars_e[memristor_errors[e]] <= vars_c[j][l]

        # equivalent_last_row_set = [[faulty.rows - 1]]
        # for equivalent_row_set in equivalent_rows:
        #     if faulty.rows - 1 in equivalent_row_set:
        #         equivalent_last_row_set = equivalent_row_set
        #         break

        # No other but last row to bottom-most nanowire
        # for i in range(original.rows - 1):
        # for j in equivalent_last_row_set:
        # prob += vars_r[original.input_nanowire - 1][equivalent_last_row_set[0]] == 0

        # Map each row/column in original
        for i in range(design.rows):
            prob += lpSum(vars_r[i]) == 1
        for j in range(design.columns):
            prob += lpSum(vars_c[j]) == 1

        vars_r_t = np.array(vars_r).T.tolist()
        vars_c_t = np.array(vars_c).T.tolist()

        # Map maximum 1 row/col to each row/col in faulty
        for i in range(crossbar.rows):
            prob += lpSum(vars_r_t[i]) <= 1
        for i in range(crossbar.columns):
            prob += lpSum(vars_c_t[i]) <= 1

        prob.solve(solver)
        # prob.writeLP("test.lp")

        if prob.status == LpStatusInfeasible:
            raise InfeasibleSolutionException("Infeasible solution.")

        for v in prob.variables():
            # print(v.name[0])
            # print(v.varValue)
            if v.name[0] == "r" and int(round(v.varValue)) == 1:
                [_, original_row, faulty_row] = v.name.split("_")
                self.row_assignment[int(original_row)] = int(faulty_row)
            if v.name[0] == "c" and int(round(v.varValue)) == 1:
                [_, original_column, faulty_column] = v.name.split("_")
                self.column_assignment[int(original_column)] = int(faulty_column)

        print("Status:", LpStatus[prob.status])

        # Print the value of the variables at the optimum
        # for v in prob.variables():
        #     print(v.name, "=", v.varValue)

        # Print the value of the objective
        print("Error = ", value(prob.objective))
        self.error = value(prob.objective)
        self.end_time_ilp = time.time()

        return self.row_assignment, self.column_assignment
