from typing import *
from lox.token_type import TokenType
from lox.token import Token
from numbers import Number

class Scanner:
    def __init__(self, source: Final[str], error_reporter):
        self.source = source
        self.tokens: Final[List[Token]] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.error_reporter = error_reporter
        
        self.keywords: Final[dict[str, TokenType]] = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "null": TokenType.NULL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE
        }
        
        
    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens


    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    
    def advance(self):
        char_to_return = self.source[self.current]
        self.current += 1
        return char_to_return


    def add_token(self, token_type: TokenType, literal: object = None) -> None:
        text: str = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
        
    
    def scan_token(self) -> None:
        c = self.advance()
        match c:
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
                return
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)
                return
            case '{':
                self.add_token(TokenType.LEFT_BRACE)
                return
            case '}':
                self.add_token(TokenType.RIGHT_BRACE)
                return
            case ',':
                self.add_token(TokenType.COMMA)
                return
            case '.':
                self.add_token(TokenType.DOT)
                return
            case '-':
                self.add_token(TokenType.MINUS)
                return
            case '+':
                self.add_token(TokenType.PLUS)
                return
            case ';':
                self.add_token(TokenType.SEMICOLON)
                return
            case '*':
                self.add_token(TokenType.STAR)
                return
            case '!':
                self.add_token(TokenType.BANG_EQUAL if self.match(
                    '=') else TokenType.BANG)
                return
            case '=':
                self.add_token(TokenType.EQUAL_EQUAL if self.match(
                    '=') else TokenType.EQUAL)
                return
            case '<':
                self.add_token(TokenType.LESS_EQUAL if self.match(
                    '=') else TokenType.LESS)
                return
            case '>':
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
                return
            case '/':
                if self.match('/'):
                    # A comment goes until the end of the line
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
                return
            
            case ' ' |'\r' | '\t':
                # Ignore whitespace
                pass

            case '\n':
                # Add a new line
                self.line += 1
                pass
            
            case '"' | "'":
                self.string(c)

            # Handling defaults
            case _:
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    error_message = f"Unexpected character: '{c}'"
                    self.error_reporter(self.line, error_message)
    
    
        # Handle numbers
    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fractional part of the number
        if self.peek() == '.' and self.is_digit(self.peek_next):
            # Consume the '.'
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(
            self.source[self.start:self.current]))
        
        
    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text: str = self.source[self.start:self.current]
        token_type: TokenType = self.keywords.get(text, TokenType.IDENTIFIER)
        if token_type is None:
            token_type = TokenType.IDENTIFIER
        self.add_token(token_type)


    def match(self, expected) -> bool:
        if self.is_at_end(): return False
        if self.source[self.current] != expected: return False
        
        self.current += 1
        return True
    
    
    def peek(self):
        if self.is_at_end(): return '\0'
        
        return self.source[self.current]
    
    
    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'

        return self.source[self.current + 1]
    
    
    def is_digit(self, c) -> bool:
        return c >= '0' and c <= '9'
    
    def string(self, opening_quote: str) -> None:
        # Loop while the next char is NOT the required closing quote and not EOF
        while self.peek() != opening_quote and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1 
            self.advance()  # Consume character inside the string

        # Check why the loop ended
        if self.is_at_end():
            # Reached EOF before finding the closing quote
            self.error_reporter(self.line, "Unterminated string.")
            return  # Stop processing this token

        # If we're here, peek() == opening_quote because the loop stopped.
        # Consume the closing quote.
        self.advance()

        # Extract the value (start was set before calling string())
        # +1 to skip opening quote, -1 to skip the closing quote we just consumed
        value: str = self.source[self.start + 1: self.current - 1]
        self.add_token(TokenType.STRING, value)

        
    def is_alpha(self, c) -> bool:
        return c.isalpha() or c == '_'
    

    def is_alpha_numeric(self, c) -> bool:
        return self.is_alpha(c) or self.is_digit(c)
    
    
