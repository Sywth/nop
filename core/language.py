import abc
import logging
from typing import Union, TYPE_CHECKING


class Keywords:
    SELF_IDENTIFIER = "self"


class Command(abc.ABC):
    @abc.abstractmethod
    def execute(self, state: dict[str, "ValueType"]) -> "ValueType": ...


class Function(abc.ABC):
    @abc.abstractmethod
    def call(self, arguments: list["ValueType"]) -> "ValueType": ...


class IdentifierType(str): ...


Null = object()
ValueType = Union[float, str, list["ValueType"], bool, Null, "Function"]
ExpressionType = Union[ValueType, IdentifierType]
ArgumentType = Union[Command, ExpressionType]
LineType = Command


def is_value_type(value: ValueType) -> bool:
    return isinstance(value, (float, str, list, bool, LambdaFunction)) or value is Null


def evaluate_argument(argument: ArgumentType, state: dict[str, ValueType]) -> ValueType:
    if isinstance(argument, Command):
        return argument.execute(state)
    elif isinstance(argument, IdentifierType):
        return state[argument]
    elif is_value_type(argument):
        return argument

    assert False, "Invalid value type"


class LambdaFunction(Function):
    def __init__(
        self,
        parameters: list[IdentifierType],
        lines: list[LineType],
        open_variables: set[IdentifierType] = None,
    ):
        self.parameters = parameters
        self.lines = lines
        # variables that need to be meet for the function to having semantic meaning
        self.open_variables = open_variables if open_variables is not None else set()
        self.closure = {}

    def call(self, arguments: list[ValueType]):
        if len(arguments) != len(self.parameters):
            logging.error("Invalid number of arguments")
            return

        local_state = self.closure.copy()
        local_state[Keywords.SELF_IDENTIFIER] = self
        for parameter, argument in zip(self.parameters, arguments):
            local_state[parameter] = argument

        # Run line by line until a return statement is found
        for line in self.lines:
            line.execute(local_state)
            if isinstance(line, ReturnStatement):
                return line.execute(local_state)

        # If no return statement is found, return Null
        return Null

    def overwrite_closure(self, closure: dict[IdentifierType, ValueType]):
        self.closure = {
            k: v for k, v in closure.items() if k in self.open_variables
        }  # TODO we really should be making a deep copy here

        unclosed_variables = self.open_variables - set(self.closure.keys())

        if len(unclosed_variables) > 0:
            error_message = f"Unclosed variables: {unclosed_variables}"
            logging.error(error_message)
            raise NameError(error_message)

    def __str__(self) -> str:
        return f"Function({', '.join(self.parameters)})"


class Assignment(Command):
    def __init__(self, identifier: IdentifierType, rhs: ArgumentType):
        self.identifier = identifier
        self.rhs = rhs

    def execute(self, state):
        value = evaluate_argument(self.rhs, state)
        state[self.identifier] = value
        return value

    def __str__(self) -> str:
        return f"{self.identifier} <- {self.rhs}"


class FunctionCall(Command):
    def __init__(self, identifier: IdentifierType, arguments: list[ArgumentType]):
        self.identifier = identifier
        self.arguments = arguments

    def execute(self, state):
        function: Function = state[self.identifier]
        arguments = [evaluate_argument(argument, state) for argument in self.arguments]

        # lambda functions have access to outer scopes
        # NOTE: this means that the behavior of the function is dependent on state/scope we call it from
        if isinstance(function, LambdaFunction):
            function.overwrite_closure(state)

        return function.call(arguments)


class ReturnStatement(Command):
    def __init__(self, rhs: ArgumentType):
        self.rhs = rhs

    def execute(self, state) -> ValueType:
        return evaluate_argument(self.rhs, state)
