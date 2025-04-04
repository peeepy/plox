from lox.token import Token
from lox.runtime_error import RuntimeException

class Environment:
    def __init__(self):
        self.values: Final[dict] = {}
    
    def define(self, name: str, value: object) -> None:
        self.values[name] = value
        
    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        raise RuntimeException(f"Undefined variable '{name.lexeme}'.", name)
    
    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return
        
        raise RuntimeException(f"Undefined variable `{name.lexeme}`.", name)