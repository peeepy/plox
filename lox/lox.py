import sys
import io
from typing import *
from lox.token import Token
from lox.scanner import Scanner
from lox.parser import Parser
from tool.AST.Stmt import Stmt
from lox.ast_printer import AstPrinter
from lox.interpreter import Interpreter
from lox.runtime_error import RuntimeException


class Lox:
    def __init__(self):
        self.had_error: bool = False
        self.had_runtime_error: bool = False
        self.interpreter = Interpreter(self.runtime_error)

    def run(self, source: str, is_repl: bool = False) -> None:
        scanner = Scanner(source, self.error)
        tokens: List[Token] = scanner.scan_tokens()
        parser: Parser = Parser(tokens, self.error)
        statements: List[Stmt] = parser.parse()
        
        # Only exit if not in REPL mode
        if not is_repl:
            if self.had_error:
                sys.exit(65)
            if self.had_runtime_error:
                sys.exit(70)

        if statements is not None:
            self.interpreter.interpret(statements)


    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def runtime_error(self, error: RuntimeException) -> None:
        print(f"{error.message}\n[line {error.token.line}]")
        
        self.had_runtime_error = True

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
        self.had_error = True


    def run_file(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as file:
                source = file.read()
            self.run(source)

            if self.had_error:
                sys.exit(65)
        except FileNotFoundError:
            print(f"Error: Cannot open file '{path}'.", file=sys.stderr)
            sys.exit(66)
        except Exception as e:
            print(
                f"An unexpected error occurred processing file: {e}", file=sys.stderr)
            sys.exit(70)


    def run_prompt(self) -> None:
        try:
            while True:
                line: str = input("> ")
                if line == "":
                    continue
                self.run(line, is_repl=True)
                self.had_error = False
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")


    @staticmethod
    def main(args: List[str]) -> None:
        lox_interpreter = Lox()

        if len(args) > 1:
            print("Usage: pylox [script]", file=sys.stderr)
            sys.exit(64)
        elif len(args) == 1:
            lox_interpreter.run_file(args[0])
        else:
            lox_interpreter.run_prompt()


if __name__ == "__main__":
    Lox.main(sys.argv[1:])
