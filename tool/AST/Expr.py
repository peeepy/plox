from __future__ import annotations
from abc import ABC, abstractmethod
from typing import *
from lox.token import Token

class Visitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> Any:
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> Any:
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> Any:
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> Any:
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: Logical) -> Any:
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> Any:
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> Any:
        pass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        pass

class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_assign_expr(self)


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: Object):
        self.value = value

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_literal_expr(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_logical_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_variable_expr(self)


