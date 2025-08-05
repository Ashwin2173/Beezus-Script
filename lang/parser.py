from lang.tokenizer import TokenType
from lang.expections import LoomSyntaxError
from lang.utils.ast_node import NodeType

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pointer = 0
        self.data_types = {"integer", "string", "double"}
        self.package_name = None
        self.program = {
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
                raise LoomSyntaxError("Invalid Syntax", token)
            self.tokens.next()
        return self.program
    
    def parse_statements(self):
        statements = list()
        while self.tokens.has_next():
            if self.tokens.next().type == TokenType.CLOSE_BRACE: break
            statement = self.parse_statement()
            if statement is not None:
                statements.append(statement)
        return statements

    def parse_statement(self):
        token = self.tokens.peek()
        if token.type == TokenType.KW_RETURN:
            return self.parse_return()
        elif token.type == TokenType.KW_VAR or token.type == TokenType.KW_CONST:
            return self.parse_declaration()
        elif token.type == TokenType.KW_IF:
            return self.parse_if()
        elif token.type == TokenType.OPEN_BRACE:
            return self.parse_block_statement()
        else:
            expression = self.parse_expression()
            self.tokens.next().expect(TokenType.SEMICOLON)
            return expression

    def parse_package(self):
        self.tokens.next()
        self.tokens.peek().expect(TokenType.ID)
        package_name = self.tokens.peek()
        if self.package_name is not None:
            raise LoomSyntaxError("Re-declaration of package", package_name)
        self.package_name = package_name.raw
        self.tokens.next().expect(TokenType.SEMICOLON)

    def parse_import(self):
        self.tokens.next()
        self.tokens.peek().expect(TokenType.ID)
        import_module = self.tokens.peek().raw
        self.program['import'].add(import_module)
        self.tokens.next().expect(TokenType.SEMICOLON)

    def parse_return(self):
        line = self.tokens.peek().line
        self.tokens.next()
        expression = self.parse_expression()
        self.tokens.next().expect(TokenType.SEMICOLON)
        return {
            "type": NodeType.RETURN_DECLARATION,
            "line": line,
            "expression": expression
        }

    def parse_block_statement(self):
        line = self.tokens.peek().line
        statements = self.parse_block()
        return {
            "type": NodeType.BLOCK_STATEMENT,
            "line": line,
            "body": statements
        }

    def parse_if(self):
        line = self.tokens.peek().line
        self.tokens.next()
        expression = self.parse_expression()
        self.tokens.next()
        consequent = self.parse_statement()
        return {
            "type": NodeType.IF_STATEMENT,
            "line": line,
            "test": expression,
            "consequent": consequent,
        }

    def parse_declaration(self):
        token = self.tokens.peek()
        type_ = NodeType.VARIABLE_DECLARATION
        if token.type == TokenType.KW_CONST:
            type_ = NodeType.CONSTANTS_DECLARATION
        self.tokens.next().expect(TokenType.ID)
        data_type = self.tokens.peek().raw
        self.tokens.next().expect(TokenType.ID)
        variable = self.tokens.peek().raw
        self.tokens.next().expect(TokenType.EQUAL)
        self.tokens.next()
        expression = self.parse_expression()
        self.tokens.next().expect(TokenType.SEMICOLON)
        return {
            "type": type_,
            "line": token.line,
            "dataType": data_type,
            "variable": variable,
            "expression": expression
        }

    def parse_pass(self):
        self.tokens.next()

    def parse_function(self):
        line = self.tokens.peek().line
        self.tokens.next()
        self.tokens.peek().expect(TokenType.ID)
        return_type = "void"        # To support fancy no return type declaration
        function_name = self.tokens.peek().raw
        if self.tokens.peek(1).match(TokenType.ID):
            return_type = function_name
            function_name = self.tokens.next().raw
        function_args = self.parse_function_args()
        self.tokens.next()
        function_body = self.parse_block()
        if function_name == "main":
            function_name = "main__"
        else:
            function_name = f"{self.package_name}_{function_name}"
        self.program['body'].append({
            "type": NodeType.FUNCTION_DECLARATION,
            "returnType": return_type,
            "name": function_name,
            "line": line,
            "params": function_args,
            "body": function_body
        })

    def parse_function_args(self):
        args = set()
        args_list = list()
        self.tokens.next().expect(TokenType.OPEN_PARAM)
        if self.tokens.peek(1).type == TokenType.CLOSE_PARAM:
            self.tokens.next()
            return args_list
        while True:
            self.tokens.next().expect(TokenType.ID)
            data_type = self.tokens.peek()
            self.tokens.next().expect(TokenType.ID)
            arg = self.tokens.peek()
            if arg.raw in args:
                raise LoomSyntaxError(f"Duplicate parameter '{arg.raw}' in function declaration", arg)
            args.add(arg.raw)
            args_list.append((arg.raw, data_type.raw))
            if self.tokens.next().type == TokenType.CLOSE_PARAM:
                return args_list
            self.tokens.peek().expect(TokenType.COMMA)

    def parse_block(self):
        self.tokens.peek().expect(TokenType.OPEN_BRACE)
        statements = self.parse_statements()
        self.tokens.peek().expect(TokenType.CLOSE_BRACE)
        return statements

    def parse_function_call(self, identifier):
        self.tokens.next()
        arguments = self.parse_function_arguments()
        self.tokens.peek().expect(TokenType.CLOSE_PARAM)
        return {
            "type": NodeType.CALL_EXPRESSION,
            "callee": identifier,
            "arguments": arguments
        }
    
    def parse_function_arguments(self):
        arguments = list()
        while not self.tokens.peek().match(TokenType.CLOSE_PARAM):
            arguments.append(self.parse_expression())
            if self.tokens.has_next() and not self.tokens.next().match(TokenType.CLOSE_PARAM):
                self.tokens.peek().expect(TokenType.COMMA)
                self.tokens.next()
        return arguments

    def parse_expression(self):
        line = self.tokens.peek().line
        expression = {
            "type": NodeType.EXPRESSION,
            "line": line,
            "expression": self.equality()
        }
        self.tokens.next(-1)
        return expression
    
    def equality(self):
        left_expression = self.comparison()
        while self.tokens.has_next() and self.tokens.peek().match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operation = self.tokens.peek().raw
            self.tokens.next()
            right_expression = self.comparison()
            left_expression = {
                "type": NodeType.BINARY_EXPRESSION,
                "left": left_expression,
                "operation": operation,
                "right": right_expression
            }
        return left_expression

    def comparison(self):
        left_expression = self.term()
        while self.tokens.has_next() and self.tokens.peek().match(TokenType.LESSER, TokenType.GREATER,
                                                                  TokenType.LESSER_EQUAL, TokenType.GREATER_EQUAL):
            operation = self.tokens.peek().raw
            self.tokens.next()
            right_expression = self.term()
            left_expression = {
                "type": NodeType.BINARY_EXPRESSION,
                "left": left_expression,
                "operation": operation,
                "right": right_expression
            }
        return left_expression

    def term(self):
        left_expression = self.factor()
        while self.tokens.has_next() and self.tokens.peek().match(TokenType.PLUS, TokenType.MINUS):
            operation = self.tokens.peek().raw
            self.tokens.next()
            right_expression = self.factor()
            left_expression = {
                "type": NodeType.BINARY_EXPRESSION,
                "left": left_expression,
                "operation": operation,
                "right": right_expression
            }
        return left_expression

    def factor(self):
        left_expression = self.unary()
        while self.tokens.has_next() and self.tokens.peek().match(TokenType.STAR, TokenType.SLASH):
            operation = self.tokens.peek().raw
            self.tokens.next()
            right_expression = self.unary()
            left_expression = {
                "type": NodeType.BINARY_EXPRESSION,
                "left": left_expression,
                "operation": operation,
                "right": right_expression
            }
        return left_expression

    def unary(self):
        if self.tokens.has_next() and self.tokens.peek().match(TokenType.NOT, TokenType.MINUS):
            operation = self.tokens.peek().raw
            self.tokens.next()
            right_expression = self.unary()
            return {
                "type": NodeType.UNARY_EXPRESSION,
                "operation": operation,
                "right": right_expression
            }
        return self.primary()

    def primary(self):
        if not self.tokens.has_next():
            raise LoomSyntaxError("Invalid expression", self.tokens.peek(-1))
        token = self.tokens.peek()
        if token.match(TokenType.INTEGER):
            self.tokens.next()
            return {
                "type": NodeType.INTEGER_LITERAL,
                "value": int(token.raw)
            }
        elif token.match(TokenType.STRING):
            self.tokens.next()
            return {
                "type": NodeType.STRING_LITERAL,
                "value": token.raw
            }
        elif token.match(TokenType.DOUBLE):
            self.tokens.next()
            return {
                "type": NodeType.DOUBLE_LITERAL,
                "value": token.raw
            }
        elif token.match(TokenType.ID):
            identifier = self.parse_id()
            if self.tokens.peek().match(TokenType.OPEN_PARAM):
                function_call = self.parse_function_call(identifier)
                self.tokens.next()
                return function_call
            return identifier
        else:
            raise LoomSyntaxError(f"Invalid literal '{token.raw}'", token)
    
    def parse_id(self):
        token = self.tokens.peek()
        if self.tokens.has_next() and self.tokens.peek(1).match(TokenType.DOT):
            self.tokens.next().expect(TokenType.DOT)
            self.tokens.next()
            return {
                "type": NodeType.MEMBERSHIP_EXPRESSION,
                "name": token.raw,
                "property": self.parse_id()
            }
        elif token.match(TokenType.ID):
            self.tokens.next()
            return {
                "type": NodeType.IDENTITY,
                "name": token.raw
            }
        else:
            raise LoomSyntaxError("Invalid expression", self.tokens.peek())
