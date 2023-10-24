from networkx import MultiDiGraph

from aux import config
from core.BooleanFunctionCollection import BooleanFunctionCollection
from core.crossbars.Topology import Topology
from core.decision_diagrams.BDD import BDD
from synth.COMPACT import COMPACT
from cli.Command import Command


class COMPACTCommand(Command):

    def __init__(self, args: list):
        """
        Command to apply the COMPACT algorithm to a graph.

        :param args: A list of required and optional arguments.

        compact [-gamma|-g VALUE] [-l VALUE] [-vh] [-io] [-r VALUE] [-c VALUE] [-t VALUE]

        Optional arguments:

        -gamma VALUE    Gamma value [0,1].

        -g VALUE        Shorthand for -gamma.

        -l VALUE        The number of layers.

        -t VALUE        Time limit in seconds.

        """

        super(COMPACTCommand).__init__()

        if "-gamma" in args:
            idx = args.index("-gamma")
            config.gamma = float(args[idx + 1])
        else:
            config.gamma = 1

        if "-g" in args:
            idx = args.index("-g")
            config.gamma = float(args[idx + 1])
        else:
            config.gamma = 1

        self.layers = 1

        if "-io" in args:
            config.io_constraints = False
        else:
            config.io_constraints = True

        if "-t" in args:
            idx = args.index("-t")
            config.time_limit = int(args[idx + 1])
        else:
            config.time_limit = None

        if "-keep" in args:
            config.keep_files = True
        else:
            config.keep_files = False

    def execute(self):
        """
        Executes the COMPACT algorithm on a graph.
        The graph is obtained from the current context.
        :return:
        """

        boolean_function_collection = config.context_manager.get_context()

        graph = MultiDiGraph()
        for boolean_function in boolean_function_collection.boolean_functions:
            assert isinstance(boolean_function, BDD)
            compact = COMPACT(boolean_function, self.layers)
            memristor_crossbar = compact.map()
            graph.add_node(memristor_crossbar)

        topology = Topology(graph)
        config.context_manager.add_context("topology", BooleanFunctionCollection({topology}))
        return False
