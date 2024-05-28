import pathlib
import sys
from core.language import (
    ArgumentType,
    Function,
    IdentifierType,
    LambdaFunction,
    Null,
    ValueType,
    evaluate_argument,
)

GRAMMAR_FILEPATH = pathlib.Path("./core/grammar.lark")


class SystemFunction(Function): ...


class Add(SystemFunction):
    def call(self, arguments: list[ValueType]) -> float:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs + rhs

    def __str__(self):
        return f"+(lhs,rhs)"


class Subtract(SystemFunction):
    def call(self, arguments: list[ValueType]) -> float:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs - rhs

    def __str__(self):
        return f"-(lhs,rhs)"


class Multiply(SystemFunction):
    def call(self, arguments: list[ValueType]) -> float:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs * rhs

    def __str__(self):
        return f"*(lhs,rhs)"


class Divide(SystemFunction):
    def call(self, arguments: list[ValueType]) -> float:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs / rhs

    def __str__(self):
        return f"/(lhs,rhs)"


class Print(SystemFunction):
    def call(
        self, arguments: list[ValueType]
    ) -> object:  # returns Null (cannot type hint this fact)
        print()
        for arg in arguments:
            sys.stdout.write(str(arg) + " ")
        sys.stdout.write("\n")
        print()

        return Null

    def __str__(self):
        return f"print(value)"


class Input(SystemFunction):
    def call(self, arguments: list[ValueType]) -> str:
        prompt = arguments[0]
        return input(prompt)

    def __str__(self):
        return f"input(prompt)"


class If(LambdaFunction):
    @staticmethod
    def get_validated_arguments(
        arguments: list[ArgumentType],
    ) -> tuple[bool, LambdaFunction, LambdaFunction]:
        if len(arguments) != 3:
            assert False, "If statement must have 3 arguments"

        antecedent = arguments[0]
        antecedent = evaluate_argument(antecedent, {})
        if not isinstance(antecedent, bool):
            assert False, "Antecedent must be a boolean"

        consequent = arguments[1]
        alternative = arguments[2]
        if not (
            isinstance(consequent, LambdaFunction)
            and isinstance(alternative, LambdaFunction)
        ):
            assert False, "Consequent and alternative must be functions"

        if not (len(consequent.parameters) == 0 and len(alternative.parameters) == 0):
            assert False, "Arity of consequent and alternative must be 0"

        return antecedent, consequent, alternative

    def call(self, arguments: list[ArgumentType]) -> str:
        antecedent, consequent, alternative = self.get_validated_arguments(arguments)

        if evaluate_argument(antecedent, self.closure) == True:
            consequent.overwrite_closure(self.closure)
            return consequent.call([])

        if evaluate_argument(antecedent, self.closure) == False:
            alternative.overwrite_closure(self.closure)
            return alternative.call([])

        assert False, "Antecedent must be a boolean"

    def __str__(self):
        return f"if(antecedent, consequent, alternative)"


class Equivalence(SystemFunction):
    def call(self, arguments: list[ValueType]) -> bool:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs == rhs

    def __str__(self):
        return f"=(lhs,rhs)"


class LessThan(SystemFunction):
    def call(self, arguments: list[ValueType]) -> bool:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs < rhs

    def __str__(self):
        return f">(lhs,rhs)"


class GreaterThan(SystemFunction):
    def call(self, arguments: list[ValueType]) -> bool:
        lhs = arguments[0]
        rhs = arguments[1]
        return lhs > rhs

    def __str__(self):
        return f">(lhs,rhs)"


math = {
    "+": Add(),
    "-": Subtract(),
    "*": Multiply(),
    "/": Divide(),
    "<": LessThan(),
    ">": GreaterThan(),
}
io = {"print": Print(), "input": Input()}
logic = {
    "=": Equivalence(),
    "if": If(
        [
            IdentifierType("antecedent"),
            IdentifierType("consequent"),
            IdentifierType("alternative"),
        ],
        [],
    ),
}
