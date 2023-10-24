from pathlib import Path

from aux import config
from cli.Command import Command
from core.crossbars.Crossbar import Crossbar
from depr.CrossbarWriter import CrossbarWriter


class WriteCrossbarCommand(Command):

    def __init__(self, args):
        super().__init__()
        if len(args) < 1:
            raise Exception("Missing file name.")

        self.file_path = Path(args[0])

    def execute(self) -> bool:
        boolean_function_collection = config.context_manager.get_context()
        topology = list(boolean_function_collection.boolean_functions)[0]
        subtopology = list(topology.graph.nodes)[0]
        if isinstance(subtopology, Crossbar):
            crossbar = subtopology
        else:
            crossbar = list(subtopology.graph.nodes)[0]
        cw = CrossbarWriter(crossbar, self.file_path)
        cw.write()
        return False
