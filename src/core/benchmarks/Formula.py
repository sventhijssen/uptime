from __future__ import annotations
import re
from typing import Dict, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from aux.VerilogParser import VerilogFormula
from core.BooleanFunction import BooleanFunction


class Formula(BooleanFunction):

    def __init__(self, verilog: VerilogFormula):
        super().__init__()
        self.verilog = verilog

    def get_input_variables(self) -> Set[str]:
        return self.verilog.boolean_expression.get_input_variables()

    def get_output_variables(self) -> Set[str]:
        return set(self.verilog.output)

    def get_auxiliary_variables(self) -> Set[str]:
        return set()

    def negate(self) -> Formula:
        """
        Returns the negation of this formula.
        """
        return self.__neg__()

    def __str__(self):
        return str(self.verilog.output) + ' = ' + str(self.verilog.boolean_expression)

    def __repr__(self):
        return str(self.verilog.output) + ' = ' + str(self.verilog.boolean_expression)

    def __neg__(self):
        neg_verilog = self.verilog
        neg_verilog = re.sub(r"(.+)", r"~(\1)", neg_verilog)
        neg_verilog = neg_verilog.replace("~(1'b1)", "1'b0")
        neg_verilog = neg_verilog.replace("~(1'b0)", "1'b1")
        return Formula(neg_verilog)

    def eval(self, instance: Dict[str, bool]) -> Dict[str, bool]:
        return {self.verilog.output: self.verilog.boolean_expression.eval(instance)}
