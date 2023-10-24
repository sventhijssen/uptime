from aux import config
from core.BooleanFunctionCollection import BooleanFunctionCollection
from exceptions.AssignmentError import AssignmentError
from aux.ColumnPermutation import ColumnPermutation
from aux.CrossbarReader import CrossbarReader
from aux.DataLayoutReorganization import DataLayoutReorganization
from exceptions.InfeasibleSolutionException import InfeasibleSolutionException
from aux.NaiveDataLayoutOrganization import NaiveDataLayoutOrganization
from aux.RowColumnPermutation import MultiLayerPermutation
from aux.RowPermutation import RowPermutation
from cli.Command import Command


class MapCommand(Command):

    def __init__(self, args):
        super(MapCommand).__init__()

        if len(args) < 1:
            raise Exception("No approach defined.")

        if len(args) < 2:
            raise Exception("No crossbar filename defined.")

        self.approach = args[0]

        self.dimensions = []
        if "-l" in args:
            idx = args.index("-l")
            for i in range(idx + 1, len(args)):
                try:
                    self.dimensions.append(int(args[i]))
                except ValueError:
                    break

        self.crossbar_filename = args[-1]

    def execute(self) -> bool:
        ctx = config.context_manager.get_context()

        cr = CrossbarReader(self.crossbar_filename)
        crossbar = cr.read()

        print("Mapping started.")

        new_boolean_functions = set()
        for boolean_function in ctx.boolean_functions:
            design = boolean_function

            if self.approach == "permutation":
                if len(self.dimensions) > 0:
                    # We will try a permutation for each dimension sequentially.
                    # If the mapping fails for the last dimension in the list, then it fails overall.
                    # Otherwise, it is inconclusive, and we must try the next dimension.
                    for i in range(len(self.dimensions)):
                        dimension = self.dimensions[i]
                        if dimension == 0:
                            strategy = RowPermutation()
                        else:
                            strategy = ColumnPermutation()

                        approach = DataLayoutReorganization(design, crossbar, strategy)
                        try:
                            crossbar_design = approach.map()
                            new_boolean_functions.add(crossbar_design)
                            break
                        except (InfeasibleSolutionException, AssignmentError):
                            if i == len(self.dimensions) - 1:
                                raise InfeasibleSolutionException
                else:
                    strategy = MultiLayerPermutation()
                    approach = DataLayoutReorganization(design, crossbar, strategy)
                    crossbar_design = approach.map()
                    new_boolean_functions.add(crossbar_design)
            elif self.approach == "naive":
                approach = NaiveDataLayoutOrganization(design, crossbar)
                crossbar_design = approach.map()
                new_boolean_functions.add(crossbar_design)
            else:
                raise Exception("Unknown mapping approach.")

        new_boolean_function_collection = BooleanFunctionCollection(new_boolean_functions)
        config.context_manager.add_context("", new_boolean_function_collection)

        print("Mapping completed.")

        return False
