from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from lox.token import Token

class Visitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> Any:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> Any:
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> Any:
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        pass

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_var_stmt(self)


