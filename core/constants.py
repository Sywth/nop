import pathlib
import sys
from core.language import Function, IdentifierType, Null, ValueType

GRAMMAR_FILEPATH = pathlib.Path("./core/grammar.lark")


class SystemFunction(Function): ...


class Add(SystemFunction):
    def __init__(self):
        self.parameters = [IdentifierType("lhs"), IdentifierType("rhs")]

    def call(self, arguments: list[ValueType]) -> float:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs + rhs

    def __str__(self):
        return f"+(lhs,rhs)"


class Subtract(SystemFunction):
    def __init__(self):
        self.parameters = [IdentifierType("lhs"), IdentifierType("rhs")]

    def call(self, arguments: list[ValueType]) -> float:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs - rhs

    def __str__(self):
        return f"-(lhs,rhs)"


class Multiply(SystemFunction):
    def __init__(self):
        self.parameters = [IdentifierType("lhs"), IdentifierType("rhs")]

    def call(self, arguments: list[ValueType]) -> float:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs * rhs

    def __str__(self):
        return f"*(lhs,rhs)"


class Divide(SystemFunction):
    def __init__(self):
        self.parameters = [IdentifierType("lhs"), IdentifierType("rhs")]

    def call(self, arguments: list[ValueType]) -> float:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs / rhs

    def __str__(self):
        return f"/(lhs,rhs)"


class Print(SystemFunction):
    def __init__(self):
        self.parameters = [IdentifierType("value")]

    def call(
        self, arguments: list[ValueType]
    ) -> object:  # returns Null (cannot type hint this fact)
        for arg in arguments:
            sys.stdout.write(str(arg) + " ")
        sys.stdout.write("\n")
        return Null

    def __str__(self):
        return f"print(value)"


class Input(SystemFunction):
    def __init__(self):
        self.parameters = [IdentifierType("prompt")]

    def call(self, arguments: list[ValueType]) -> str:
        prompt = arguments[0]
        return input(prompt)

    def __str__(self):
        return f"input(prompt)"


math = {"+": Add(), "-": Subtract(), "*": Multiply(), "/": Divide()}
io = {"print": Print(), "input": Input()}
