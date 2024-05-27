import logging
import sys
import core.constants as constants
import pathlib
import lark

from core.language import (
    Assignment,
    LambdaFunction,
    FunctionCall,
    IdentifierType,
    Null,
    ReturnStatement,
)

# TODO next time, implement if statements using functions with 3 arguments
# TODO next time, implement loops etc


class NopTransformer(lark.Transformer):
    def line(self, items: list[lark.tree.Tree]):
        return items[0]

    def assignment(self, items: list[lark.tree.Tree]):
        return Assignment(items[0], items[1])

    def identifier(self, items: list[lark.tree.Tree]):
        return IdentifierType(items[0])

    def numeric(self, items: list[lark.tree.Tree]):
        return float(items[0])

    def string(self, items: list[lark.tree.Tree]):
        return str(items[0])

    def true(self, items: list[lark.tree.Tree]):
        return True

    def false(self, items: list[lark.tree.Tree]):
        return False

    def null(self, items: list[lark.tree.Tree]):
        return Null

    def function(self, items: list[lark.tree.Tree]):
        parameters = items[0].children
        if len(parameters) == 1 and parameters[0] is None:
            parameters = []
        lines = items[1].children
        if len(lines) == 1 and lines[0] is None:
            lines = []
        f = LambdaFunction(parameters, lines)
        return f

    def function_call(self, items: list[lark.tree.Tree]):
        identifier = items[0]
        # for some reason if no arguments are passed it looks like [identifier, None]
        arguments = items[1:]
        if items[1] is None:
            arguments = []
        return FunctionCall(identifier, arguments)

    def return_statement(self, items: list[lark.tree.Tree]):
        return ReturnStatement(items[0])


def get_parser() -> lark.Lark:
    grammar = ""
    with open(constants.GRAMMAR_FILEPATH) as f:
        grammar += f.read()

    return lark.Lark(grammar)


def get_transformer() -> lark.Transformer:
    return NopTransformer()


def inject_library(state: dict, library: dict) -> None:
    for key, value in library.items():
        state[key] = value


def get_runner(parser: lark.Lark, transformer: lark.Transformer, global_sate):
    inject_library(global_sate, constants.math)
    inject_library(global_sate, constants.io)

    def run(line: str):
        try:
            obj: lark.ParseTree = parser.parse(line)
        except lark.exceptions.LarkError as e:
            logging.error(f"Parser Error: {e}")
            return
        logging.log(logging.DEBUG, f"parser tree = {obj.pretty()}")

        try:
            obj: lark.Token = transformer.transform(obj)
        except Exception as e:
            logging.error(f"Transformer Error: {e}")
            return
        logging.log(logging.DEBUG, f"transformed = {obj}")

        try:
            result = obj.execute(global_sate)
        except Exception as e:
            logging.error(f"Execution Error: {e}")
            return
        logging.log(logging.DEBUG, f"executing = {result}")

    return run


def run_repl():
    run = get_runner(parser=get_parser(), transformer=get_transformer(), global_sate={})
    while True:
        line = input(">>>")
        run(line)


def run_file(filepath: pathlib.Path):
    run = get_runner(parser=get_parser(), transformer=get_transformer(), global_sate={})
    with open(filepath) as f:
        for i, line in enumerate(f):
            run(line)


def main():
    logging.info("===***NOP v0.1***===")

    args = sys.argv
    if len(args) > 2:
        logging.error("Invalid use of NOP")
        return

    if len(args) == 2:
        filepath = pathlib.Path(args[1])
        logging.info(f"Running on file {filepath}")
        run_file(filepath)
        return

    if len(args) == 1:
        logging.info(f"Running REPL")
        run_repl()
        return

    assert False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
