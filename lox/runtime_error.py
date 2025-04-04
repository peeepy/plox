class RuntimeException(RuntimeError):
    def __init__(self, message: str, token):
        super().__init__(message) 
        self.token = token
        self.message = message
        