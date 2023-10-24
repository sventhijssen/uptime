from abc import ABC

from core.BooleanFunctionInterface import BooleanFunctionInterface


class BooleanFunction(BooleanFunctionInterface, ABC):
    """
    An abstract class to represent a Boolean function.
    """
    def __init__(self, name: str = None):
        """
        A multi-output Boolean function has input variables, output variables, and optionally auxiliary variables.
        """
        self.name = name

    def get_name(self) -> str:
        """
        Returns the name of this Boolean function.
        :return:
        """
        if self.name is None:
            return str(id(self))
        return self.name
