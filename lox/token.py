from typing import *
from .token_type import TokenType

class Token:
    def __init__(self, token_type: Final[TokenType], lexeme: Final[str], literal: Final[object], line: Final[int]):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        
    def __str__(self):
        # A more user-friendly format
        return f"[{self.line}] {self.token_type}: '{self.lexeme}' ({self.literal})"
        