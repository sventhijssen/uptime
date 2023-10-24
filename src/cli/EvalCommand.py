from pathlib import Path

from aux import config
from aux.InstanceFileReader import InstanceFileReader
from cli.Command import Command


class EvalCommand(Command):

    def __init__(self, args):
        super(EvalCommand).__init__()
        if len(args) < 1:
            raise Exception("Unknown instance file.")

        self.instance_file = args[0]

        # Output file is specified in command following argument "-f"
        if "-f" in args:
            idx = args.index("-f")
            self.output_file = args[idx + 1]
        else:
            self.output_file = None

        if "-v" in args:
            self.verify = True
        else:
            self.verify = False

    def execute(self) -> bool:
        context = config.context_manager.get_context()

        instance_file_reader = InstanceFileReader(self.instance_file)
        instance = instance_file_reader.parse()

        evaluation = context.eval(instance)

        # content = ''
        # evaluation = context.crossbar.eval(instance, "1")
        # print(evaluation)
        # for formula in context.benchmark.formulas.values():
        #     evaluation = "{} = {}\n".format(formula.output_variable, formula.eval(instance))
        #     content += evaluation

        if self.verify:
            for output_variable, value in evaluation.items():
                if output_variable in instance:
                    if value != instance.get(output_variable):
                        print("Not equivalent.")
            print("Equivalent.")
        else:
            print(evaluation)
        # if self.output_file is not None:
        #     with open(self.output_file, 'w') as f:
        #         f.write(content)
        return False
