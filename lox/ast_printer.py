from tool.AST.Expr import *
from typing import List
from lox.token_type import TokenType
from lox.token import Token
import sys

class AstPrinter(Visitor):
    def __init__(self):
        pass
    
    def print(self, expr: Expr) -> str:
        return expr.accept(self)
    
    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesise(expr.operator.lexeme, expr.left, expr.right)
    
    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesise("group", expr.expression)
    
    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None: return "null"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesise(expr.operator.lexeme, expr.right)
    
    
    def parenthesise(self, name: str, *exprs) -> str:
        # 1. Call accept() on each expression and convert the result to a string.
        processed_expr_strings = [str(expr.accept(self)) for expr in exprs]

        # 2. Combine the initial 'name' with the processed expression strings.
        all_parts = [name] + processed_expr_strings

        # 3. Join all parts with spaces.
        content = " ".join(all_parts)

        # 4. Wrap the joined content in parentheses.
        return f"({content})"
    
    @staticmethod
    def main(args: List[str]) -> None:
        expression: Expr = Binary(Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)), 
                                       Token(TokenType.STAR,  "*", None, 1),
                                       Grouping(Literal(45.67)))
        
        printer_instance = AstPrinter()
        print(printer_instance.print(expression))
        

if __name__ == "__main__":
    AstPrinter.main(sys.argv[1:])

    