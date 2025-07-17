from lang.tokenizer import TokenType
from lang.expections import LoomSyntaxError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pointer = 0
        self.program = {
            "package": None,
            "import": set(),
            "body": []
        }
    
    def parse(self):
        while self.tokens.has_next():
            token = self.tokens.peek()
            if token.type == TokenType.KW_PACKAGE:
                self.parse_package()
            elif token.type == TokenType.KW_IMPORT:
                self.parse_import()
            elif token.type == TokenType.KW_FUNCTION:
                self.parse_function()
            else:
                print(token.raw)
                raise LoomSyntaxError("Invalid Syntax", token)
            self.tokens.next()
        return self.program
    
    def parse_statements(self):
        statements = list()
        while self.tokens.has_next():
            token = self.tokens.next()
            if token.type == TokenType.KW_RETURN:
                statements.append(self.parse_return())
            elif token.type == TokenType.KW_PASS or token.type == TokenType.SEMICOLON:
                self.parse_pass()
            elif token.type == TokenType.CLOSE_BRACE:
                break
            else:
                print(token.raw)
                raise LoomSyntaxError("Invalid Syntax @statement", token)
        return statements
    
    def parse_package(self):
        self.tokens.next()
        self.tokens.peek().expect(TokenType.ID)
        package_name = self.tokens.peek()
        if self.program['package'] is not None:
            raise LoomSyntaxError("Re-declaration of package", package_name)
        self.program['package'] = package_name.raw
        self.tokens.next().expect(TokenType.SEMICOLON)

    def parse_import(self):
        self.tokens.next()
        self.tokens.peek().expect(TokenType.ID)
        import_module = self.tokens.peek().raw
        self.program['import'].add(import_module)
        self.tokens.next().expect(TokenType.SEMICOLON)

    def parse_return(self):
        line = self.tokens.peek().line
        self.tokens.next().expect(TokenType.INTEGER)
        expression = self.tokens.peek()
        self.tokens.next().expect(TokenType.SEMICOLON)
        return {
            "type": "return",
            "expression": expression.raw,
            "line": line
        }
    
    def parse_pass(self):
        self.tokens.next()

    def parse_function(self):
        line = self.tokens.peek().line
        self.tokens.next()
        self.tokens.peek().expect(TokenType.ID)
        function_name = self.tokens.peek().raw
        function_args = self.parse_function_args()
        function_body = self.parse_block()
        if function_name == "main": function_name = "__main__"
        self.program['body'].append({
            "type": "function",
            "name": function_name,
            "line": line,
            "params": function_args,
            "body": function_body
        })

    def parse_function_args(self):
        args = list()
        self.tokens.next().expect(TokenType.OPEN_PARAM)
        if self.tokens.peek(1).type == TokenType.CLOSE_PARAM:
            self.tokens.next()
            return args
        while True:
            self.tokens.next().expect(TokenType.ID)
            arg = self.tokens.peek()
            if arg.raw in args:
                raise LoomSyntaxError(f"Duplicate parameter '{arg.raw}' in function declaration", arg)
            args.append(arg.raw)
            if self.tokens.next().type == TokenType.CLOSE_PARAM:
                return args
            self.tokens.peek().expect(TokenType.COMMA)

    def parse_block(self):
        self.tokens.next().expect(TokenType.OPEN_BRACE)
        statements = self.parse_statements()
        self.tokens.peek().expect(TokenType.CLOSE_BRACE)
        return statements