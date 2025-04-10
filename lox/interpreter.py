from tool.AST import Stmt, Expr
from lox.token_type import TokenType
from lox.token import Token
from lox.errors.runtime_error import RuntimeException
from typing import List
from lox.environment import Environment
import time
from lox.lox_callable import LoxCallable
from lox.lox_class import LoxClass
from lox.lox_function import LoxFunction
from lox.native_functions import define_native_functions
from lox.errors.return_error import Return

class Interpreter(Expr.Visitor, Stmt.Visitor):
    def __init__(self, error_reporter):
        self.error_reporter = error_reporter
        self.global_vars: Environment = Environment()
        self.environment: Environment = self.global_vars
        self.locals = {}
        
        # Register all native functions
        define_native_functions(self.global_vars)
    
    def interpret(self, statements: List[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeException as error:
            self.error_reporter(error)
                
            
    def stringify(self, object: object) -> str:
        if object is None: return "null"
        
        if isinstance(object, float):
            text: str = str(object)
            if text.endswith(".0"):
                text = text[0:len(text) - 2]
            return text
        
        return str(object)
    
    # Expression visitor implementations
    def visit_literal_expr(self, expr: Expr.Literal) -> object:
        return expr.value
    
    def visit_unary_expr(self, expr: Expr.Unary) -> object:
        right: object = self.evaluate(expr.right)
        
        match(expr.operator.token_type):
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)
            
        return None
    
    def visit_logical_expr(self, expr: Expr.Logical) -> object:
        left: object = self.evaluate(expr.left)

        if expr.operator.token_type is TokenType.OR:
            # If the left side is truthy, return it immediately (short-circuit).
            if self.is_truthy(left):
                return left
            # Otherwise (left side is falsey), evaluate and return the right side.
            else:
                return self.evaluate(expr.right)  # Evaluate the right side

        # --- Handle the AND operator here (assuming you have one) ---
        elif expr.operator.token_type is TokenType.AND:
            # If the left side is falsey, return it immediately (short-circuit).
            if not self.is_truthy(left):
                return left
            # Otherwise (left side is truthy), evaluate and return the right side.
            else:
                return self.evaluate(expr.right)

        # Should not happen if parser only allows OR/AND for Logical expressions
        return None  # Or raise an error
            
            
    def visit_variable_expr(self, expr: Expr.Variable) -> object:
        return self.lookup_variable(expr.name, expr)
    
    def lookup_variable(self, name: Token, expr: Expr.Expr) -> object:
        if expr in self.locals:
            distance = self.locals[expr]
            if distance is not None:
                return self.environment.get_at(distance, name.lexeme)
        return self.global_vars.get(name)
    
    
    def check_number_operand(self, operator: Token, operand: object) -> None:
        if isinstance(operand, float): return
        raise RuntimeException("Operand must be a number.", operator)
    
    def check_number_operands(self, operator: Token, left: object, right: object) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeException("Operands must be numbers.", operator)
    
    
    def is_truthy(self, obj: object) -> bool:
        if obj is None:       # Check for Lox null (Python None)
            return False
        if isinstance(obj, bool):  # Check for Booleans
            return obj            # Return True or False directly
        if isinstance(obj, (int, float)):  # Check for numbers
            return obj != 0       # Zero is falsey, non-zero is truthy
        if isinstance(obj, str):  # Check for strings
            return len(obj) > 0   # Empty string is falsey
        # Add checks for other Lox types if necessary (e.g., functions, classes later)
        # Lox doesn't typically have lists/dicts built-in like Python,
        # so checking numeric zero and empty string covers most Python-like cases
        # relevant to standard Lox.

        return True  # Everything else defaults to truthy

    def is_equal(self, a: object, b: object) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False

        return a == b
    
    def visit_grouping_expr(self, expr: Expr.Grouping) -> object:
        return self.evaluate(expr.expression)
    
    
    def evaluate(self, expr: Expr.Expr) -> object:
        return expr.accept(self)
    
    
    def execute(self, stmt: Stmt.Stmt) -> None:
        stmt.accept(self)
    
    
    def resolve(self, expr: Expr.Expr, depth: int) -> None:
        self.locals[expr] = depth
        
        
    def execute_block(self, statements: List[Stmt.Stmt], environment: Environment) -> None:
        previous: Environment = self.environment
        
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
            
            
    def visit_block_stmt(self, stmt: Stmt.Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))
        
    def visit_class_stmt(self, stmt: Stmt.Class) -> None:
        self.environment.define(stmt.name.lexeme, None)
        klass = LoxClass(stmt.name.lexeme)
        self.environment.assign(stmt.name, klass)
    
    
    # Statement visitor implementations
    def visit_expression_stmt(self, stmt: Stmt.Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: Stmt.Function) -> None:
        function: LoxFunction = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: Stmt.If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch is not None:
            self.execute(stmt.elseBranch)
            
            
    def visit_print_stmt(self, stmt: Stmt.Print) -> None:
        value: object = self.evaluate(stmt.expression)
        print(self.stringify(value))
    
    def visit_return_stmt(self, stmt: Stmt.Return) -> None:
        value: object = None
        if stmt.value is not None: value = self.evaluate(stmt.value)
        
        raise Return(value)
    
    
    def visit_var_stmt(self, stmt: Stmt.Var) -> None:
        value: object = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
            
        self.environment.define(stmt.name.lexeme, value)


    def visit_while_stmt(self, stmt: Stmt.While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        
        
    def visit_assign_expr(self, expr: Expr.Assign) -> object:
        value: object = self.evaluate(expr.value)
        distance: int = self.locals[expr]
        
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.global_vars.assign(expr.name, value)
            
        return value


    # Binary operators
    def visit_binary_expr(self, expr: Expr.Binary) -> object:
        left: object = self.evaluate(expr.left)
        right: object = self.evaluate(expr.right)
        
        match(expr.operator.token_type):
            # Comparison operators
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            # Binary operators
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                # Both operands are numbers
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                
                # Both operands are strings
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                
                # Either operand is a string, other is number
                if isinstance(left, str) or isinstance(right, str):
                    left_as_string = self.stringify(left)
                    right_as_string = self.stringify(right)
                    return left_as_string + right_as_string

                # Get the type names dynamically
                left_type = type(left).__name__
                right_type = type(right).__name__
                raise RuntimeException(f"Unsupported operand types for '{expr.operator.lexeme}': cannot use with '{left_type}' and '{right_type}'.", expr.operator
                                    )
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if left or right == 0:
                    raise RuntimeException(f"Cannot divide by zero.", expr.operator)
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            # Equality operators
            case TokenType.BANG_EQUAL: return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL: return self.is_equal(left, right)
            
        return None
    

    def visit_call_expr(self, expr: Expr.Call) -> object:
        callee: object = self.evaluate(expr.callee)

        arguments: List[object] = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeException(
                "You can only call functions and classes.", expr.paren)

        function: LoxCallable = callee

        # Check arity after we have the function and arguments
        if len(arguments) != function.arity():
            raise RuntimeError(
                f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return function.call(self, arguments)
