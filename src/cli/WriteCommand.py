from pathlib import Path

from aux import config
from cli.Command import Command


class WriteCommand(Command):

    def __init__(self, args):
        super().__init__()
        if len(args) < 1:
            raise Exception("Missing file name.")

        self.file_path = Path(args[0])

    def execute(self) -> bool:
        boolean_function_collection = config.context_manager.get_context()
        boolean_function_collection.write(self.file_path)
        return False
