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
        if self.match(TokenType.PRINT): return self.printStatement()
        if self.match(TokenType.LEFT_BRACE): return Stmt.Block(self.block())
        
        return self.expressionStatement()
    
    def declaration(self) -> Stmt.Stmt:
        try:
            if self.match(TokenType.VAR): return self.varDeclaration()

            return self.statement()
        except Parser.ParseError as error:
            self.synchronise()
        
    
    def printStatement(self) -> Stmt.Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)

    def varDeclaration(self) -> Stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expected a variable name.")
        
        initialiser: Expr.Expr = None
        if self.match(TokenType.EQUAL):
            initialiser = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Stmt.Var(name, initialiser)
    
    
    def expressionStatement(self) -> Stmt.Stmt:
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
        expr: Expr.Expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr.Expr = self.assignment()

            if isinstance(expr, Expr.Variable):
                name: Token = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target.")

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
