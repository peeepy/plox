from typing import List

from lox.token_type import TokenType
from lox.token import Token
from tool.AST import Stmt, Expr

""" Context-Free Grammar:
expression     → equality ;
equality       → comparison ( ( "!=" | "==" ) comparison )* ;
comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term           → factor ( ( "-" | "+" ) factor )* ;
factor         → unary ( ( "/" | "*" ) unary )* ;
unary          → ( "!" | "-" ) unary
               | primary ;
primary        → NUMBER | STRING | "true" | "false" | "null"
               | "(" expression ")" ;
"""

class Parser:
    class ParseError(RuntimeError): pass
    
    def __init__(self, tokens: List[Token], error_reporter):
        self.tokens = tokens
        self.current = 0
        self.error_reporter = error_reporter
    
    # @staticmethod
    def parse(self) -> List[Stmt.Stmt]:
        statements: List[Stmt.Stmt] = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def expression(self) -> Expr.Expr:
        return self.assignment()

    def statement(self) -> Stmt.Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.PRINT): return self.print_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.LEFT_BRACE): return Stmt.Block(self.block())
        
        return self.expression_statement()
    

    def for_statement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")

        # Initialiser
        initialiser: Stmt.Stmt = None
        if self.match(TokenType.SEMICOLON):
            initialiser = None
        elif self.match(TokenType.VAR):
            initialiser = self.var_declaration()
        else:
            initialiser = self.expression_statement()

        # Condition
        condition: Expr.Expr = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")

        # Increment
        increment: Expr.Expr = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")

        # Body
        body: Stmt.Stmt = self.statement()

        # Desugaring: Transform for loop into equivalent while loop structure

        # Increment
        if increment is not None:
            body = Stmt.Block([body, Stmt.Expression(increment)])

        # Condition
        if condition is None:
            condition = Expr.Literal(True)
        body = Stmt.While(condition, body)

        # Initialiser
        if initialiser is not None:
            body = Stmt.Block([initialiser, body])

        return body
    
    def if_statement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition: Expr.Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")
        
        then_branch: Stmt = self.statement()
        else_branch: Stmt = None
        if self.match(TokenType.ELSE): else_branch = self.statement()
        
        return Stmt.If(condition, then_branch, else_branch)
    
    def declaration(self) -> Stmt.Stmt:
        try:
            if self.match(TokenType.VAR): return self.var_declaration()

            return self.statement()
        except Parser.ParseError as error:
            self.synchronise()
        
    
    def print_statement(self) -> Stmt.Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)

    def var_declaration(self) -> Stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expected a variable name.")
        
        initialiser: Expr.Expr = None
        if self.match(TokenType.EQUAL):
            initialiser = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Stmt.Var(name, initialiser)
    
    def while_statement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition: Expr.Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after 'condition'.")
        body: Stmt.Stmt = self.statement()
        
        return Stmt.While(condition, body)
    
    
    def expression_statement(self) -> Stmt.Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)
    
    def block(self) -> List[Stmt.Stmt]:
        statements: List[Stmt.Stmt] = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
            
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to finish block.")
        return statements
    
    def assignment(self) -> Expr.Expr:
        expr: Expr.Expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr.Expr = self.assignment()

            if isinstance(expr, Expr.Variable):
                name: Token = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr
    
    # Logical operator methods
    def logical_or(self) -> Expr.Expr:
        expr: Expr.Expr = self.logical_and()
        
        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr.Expr = self.logical_and()
            expr = Expr.Logical(expr, operator, right)
            
        return expr
    
    def logical_and(self) -> Expr.Expr:
        expr: Expr.Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr.Expr = self.equality()
            expr = Expr.Logical(expr, operator, right)

        return expr
    
    
    # Binary operator methods
    def equality(self) -> Expr.Expr:
        expr: Expr.Expr = self.comparison()
        
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.comparison()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def comparison(self) -> Expr.Expr:
        expr: Expr.Expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.term()
            expr = Expr.Binary(expr, operator, right)

        return expr
    
    def term(self) -> Expr.Expr:
        expr: Expr.Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr.Expr = self.factor()
            expr = Expr.Binary(expr, operator, right)

        return expr
    
    def factor(self) -> Expr.Expr:
        expr: Expr.Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr.Expr = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr

    # Unary operators
    def unary(self) -> Expr.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr.Expr = self.unary()
            return Expr.Unary(operator, right)

        return self.primary()
    
    # Primary expressions
    def primary(self) -> Expr.Expr:
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE):
            return Expr.Literal(True)
        if self.match(TokenType.NULL):
            return Expr.Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr: Expr.Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Expr.Grouping(expr)
        
        raise self.error(self.peek(), "Expected an expression.")
        
        
    # Helper methods
    def match(self, *types) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        
        return False
    
    
    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type): return self.advance()
        
        raise self.error(self.peek(), message)
    
    def check(self, type: TokenType) -> bool:
        if self.is_at_end(): return False
        return self.peek().token_type == type
    
    
    def advance(self) -> Token:
        if not self.is_at_end(): self.current += 1
        return self.previous()
    
    
    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF
    
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    
    # Error handling
    def error(self, token: Token, message: str) -> ParseError: 
        self.error_reporter(token, message)
        return Parser.ParseError
    
    
    def synchronise(self) -> None:
        self.advance()
        
        while not self.is_at_end():
            if self.previous().token_type is TokenType.SEMICOLON: return
            
            match(self.peek().token_type):
                case TokenType.CLASS | TokenType.FUN | TokenType.VAR | TokenType.FOR | TokenType.IF | TokenType.WHILE | TokenType.PRINT | TokenType.RETURN:
                    return
            
            self.advance()
