from core.crossbars.Crossbar import Crossbar
from core.expressions.BooleanExpression import LITERAL


class CrossbarWriter:

    def __init__(self, crossbar: Crossbar, file_name):
        self.crossbar = crossbar
        self.file_name = file_name

    @staticmethod
    def _literal_representation(literal: LITERAL):
        if literal == LITERAL("True", True):
            return 1
        elif literal == LITERAL("False", False):
            return 0
        else:
            return literal

    def write(self):
        with open(self.file_name, 'w') as f:
            f.write(".model {}\n".format(self.file_name))
            f.write(".inputs {}\n".format(' '.join(self.crossbar.get_input_variables())))
            f.write(".outputs {}\n".format(' '.join(self.crossbar.get_output_variables())))
            f.write(".rows {}\n".format(self.crossbar.rows))
            f.write(".columns {}\n".format(self.crossbar.columns))
            for (input_variable, (layer, nanowire)) in self.crossbar.get_input_nanowires().items():
                if layer == 0:
                    f.write(".i {} {}\n".format(input_variable, nanowire))
                else:
                    f.write(".i {} {} {}\n".format(input_variable, layer, nanowire))
            for (output_variable, (layer, nanowire)) in self.crossbar.get_output_nanowires().items():
                if layer == 0:
                    f.write(".o {} {}\n".format(output_variable, nanowire))
                else:
                    f.write(".o {} {} {}\n".format(output_variable, layer, nanowire))
            f.write(".xbar\n")
            for r in range(self.crossbar.rows):
                for c in range(self.crossbar.columns):
                    literal = self._literal_representation(self.crossbar.get_memristor(r, c).literal)
                    if c < self.crossbar.columns - 1:
                        f.write("{}\t".format(literal))
                    else:
                        f.write("{}\r\n".format(literal))
            f.write(".end\n")
