class TokenError(Exception):
    def __init__(self, message, line):
        super().__init__(message + f", at line {line}")
        self.message = message
        self.line = line

class LoomSyntaxError(Exception):
    def __init__(self, message, token=None):
        line = "" if token is None else f", at line {str(token.line)}"
        super().__init__(message + line)
        self.token = token