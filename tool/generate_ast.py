import sys
from typing import List, Any
from pathlib import Path
import os

class GenerateAst:

    @staticmethod
    def main(args: List[str]):
        if len(args) != 1:
            print("Usage: generate_ast <output directory>")
            sys.exit(64)

        output_dir = Path(args[0])

        expr_types = [
            "Assign   : Token name, Expr value",
            "Binary   : Expr left, Token operator, Expr right",
            "Call     : Expr callee, Token paren, List[Expr] arguments",
            "Grouping : Expr expression",
            "Literal  : Object value",
            "Logical  : Expr left, Token operator, Expr right",
            "Unary    : Token operator, Expr right",
            "Variable : Token name",
        ]
        GenerateAst.define_ast(output_dir, "Expr", expr_types)

        GenerateAst.define_ast(output_dir, "Stmt", ["Block      : List[Stmt] statements", 
                                                    "Expression : Expr expression",
                                                    "Function   : Token name, List[Token] params," +
                                                    " List[Stmt] body",
                                                    "If         : Expr condition, Stmt thenBranch," +
                                                    " Stmt elseBranch",
                                                    "Print      : Expr expression",
                                                    "Return     : Token keyword, Expr value",
                                                    "Var        : Token name, Expr initializer",
                                                    "While      : Expr condition, Stmt body"])

    @staticmethod
    def define_ast(output_dir: Path, base_name: str, types: List[str]) -> None:
        path = output_dir / f"{base_name}.py"

        try:
            if os.path.exists(path):
                os.unlink(path)
                
            with open(path, mode='a', encoding='utf-8') as writer:
                writer.write("from __future__ import annotations\n")
                writer.write("from abc import ABC, abstractmethod\n")
                writer.write("from typing import *\n")
                writer.write("from lox.token import Token\n\n")

                GenerateAst.define_visitor(writer, base_name, types)
                writer.write("\n")

                writer.write(f"class {base_name}(ABC):\n")
                writer.write("    @abstractmethod\n")
                writer.write(
                    f"    def accept(self, visitor: Visitor) -> Any:\n")
                writer.write("        pass\n\n")

                for t in types:
                    parts = t.split(":")
                    class_name: str = parts[0].strip()
                    fields: str = parts[1].strip()
                    GenerateAst.define_type(
                        writer, base_name, class_name, fields
                    )
                    writer.write("\n")

            print(f"Generated AST code in {output_dir / (base_name + '.py')}")
        
        except OSError as e:
            # Basic error handling if the file can't be opened/written (similar to original)
            print(f"Error writing to file {path}: {e}", file=sys.stderr)

    @staticmethod
    def define_visitor(writer, base_name: str, types: List[str]) -> None:
        writer.write(f"class Visitor(ABC):\n")
        for t in types:
            class_name = t.split(":")[0].strip()
            param_name = base_name.lower()
            method_name = f"visit_{class_name.lower()}_{param_name}"
            writer.write(f"    @abstractmethod\n")
            writer.write(
                f"    def {method_name}(self, {param_name}: {class_name}) -> Any:\n")
            writer.write(f"        pass\n\n")

    @staticmethod
    def define_type(writer, base_name: str, class_name: str, field_list: str) -> None:
        writer.write(f"class {class_name}({base_name}):\n")

        param_names = []
        init_params_with_types = []
        raw_fields = field_list.split(',') if field_list else []

        for field in raw_fields:
            field = field.strip()
            if not field:
                continue

            parts = field.split(' ', 1)
            if len(parts) != 2:
                print(
                    f"Warning: Skipping malformed field definition '{field}' in {class_name}", file=sys.stderr)
                continue
            field_type = parts[0]
            field_name = parts[1]

            param_names.append(field_name)
            init_params_with_types.append(f"{field_name}: {field_type}")

        params_str = ", ".join(init_params_with_types)
        writer.write(f"    def __init__(self, {params_str}):\n")

        if not param_names:
            writer.write(f"        pass\n")
        else:
            for name in param_names:
                writer.write(f"        self.{name} = {name}\n")
        writer.write("\n")

        visitor_param_name = "visitor"
        method_name = f"visit_{class_name.lower()}_{base_name.lower()}"
        writer.write(
            f"    def accept(self, {visitor_param_name}: Visitor) -> Any:\n")
        writer.write(
            f"        return {visitor_param_name}.{method_name}(self)\n")
        
        writer.write('\n')


if __name__ == "__main__":
    GenerateAst.main(sys.argv[1:])
