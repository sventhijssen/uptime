from cli.DDCommand import DDCommand
from cli.COMPACTCommand import COMPACTCommand
from cli.DrawCommand import DrawCommand
from cli.EnumerationCommand import EnumerationCommand
from cli.EvalCommand import EvalCommand
from cli.ExitCommand import ExitCommand
from cli.MapCommand import MapCommand
from cli.NewLogCommand import NewLogCommand
from cli.PruneCommand import PruneCommand
from cli.ReadCommand import ReadCommand
from cli.WriteCommand import WriteCommand
from cli.WriteCrossbarCommand import WriteCrossbarCommand


class CommandParser:

    @staticmethod
    def parse(raw_command: str):
        """
        Parses the given command. The command is split into tokens by a whitespace.
        The first token is the command name, upon which the correct command is called with the respective arguments.
        :param raw_command: A command in the format of one string.
        :return: Returns the command based on the first token in the given command string.
        """
        command_list = raw_command.strip().split(" ")
        command_name = command_list[0]
        args = command_list[1:]
        if command_name == "exit":
            return ExitCommand()
        elif command_name == "read":
            return ReadCommand(args)
        elif command_name == "bdd":
            return DDCommand("bdd", args)
        elif command_name == "robdd":
            return DDCommand("robdd", args)
        elif command_name == "sbdd":
            return DDCommand("sbdd", args)
        elif command_name == "compact":
            return COMPACTCommand(args)
        elif command_name == "draw":
            return DrawCommand(args)
        elif command_name == "eval":
            return EvalCommand(args)
        elif command_name == "enum":
            return EnumerationCommand(args)
        elif command_name == "new_log":
            return NewLogCommand(args)
        elif command_name == "write":
            return WriteCommand(args)
        elif command_name == "write_xbar":
            return WriteCrossbarCommand(args)
        elif command_name == "prune":
            return PruneCommand()
        elif command_name == "map":
            return MapCommand(args)
        else:
            raise Exception("Unknown command.")
