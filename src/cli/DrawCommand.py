from pathlib import Path

from aux import config
from cli.Command import Command
from core.DrawInterface import DrawInterface


class DrawCommand(Command):

    def __init__(self, args):
        super().__init__()
        if len(args) < 1:
            raise Exception("Missing file name.")

        self.file_path = Path(args[0])

    def execute(self) -> bool:
        context = config.context_manager.get_context()

        i = 0
        for boolean_function in context.get_boolean_functions():
            assert isinstance(boolean_function, DrawInterface)

            file_path = self.file_path.stem + "_" + str(i) + self.file_path.suffix
            content = boolean_function.draw()
            for sub_content in content:
                with open(file_path, 'w') as f:
                    f.write(sub_content)
            i += 1
        return False
