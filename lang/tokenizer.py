import re

from lang.expections import TokenError, LoomSyntaxError

class TokenType:
    ID = 0
    INTEGER = 1
    DOUBLE = 2
    STRING = 3

    KW_FUNCTION = 3
    KW_RETURN = 4
    KW_VAR = 5
    KW_PACKAGE = 6
    KW_IMPORT = 7
    KW_PASS = 8
    KW_CONST = 9

    SEMICOLON = 100
    OPEN_PARAM = 101
    CLOSE_PARAM = 102
    OPEN_BRACE = 103
    CLOSE_BRACE = 104
    EQUAL = 105
    DOT = 106
    COMMA = 107
    EQUAL_EQUAL = 108
    BANG_EQUAL = 109
    NOT = 110
    LESSER = 111
    GREATER = 112
    LESSER_EQUAL = 113
    GREATER_EQUAL = 114
    PLUS = 115
    MINUS = 116
    STAR = 117
    SLASH = 118

    GHOST_NAME = 200

    def to_string(tokenType):
        for attr in dir(TokenType):
            if getattr(TokenType, attr) == tokenType:
                return attr
        return None

class Token:
    def __init__(self, raw, type, line): 
        self.raw = raw
        self.type = type
        self.line = line

    def expect(self, *type):
        if not self.match(*type):
            expected = ', '.join([TokenType.to_string(t) for t in type])
            expected = expected.lower()
            raise LoomSyntaxError(f"Expected '{expected}', But got '{self.raw}'", self)
        
    def match(self, *type): 
        return self.type in type

class Tokenizer:
    def __init__(self, program, grammar):
        self.program = program
        self.grammar = grammar
        self.line = 1

    def tokenize(self):
        tokens = list()
        compiled_grammar = re.compile(self.grammar, re.VERBOSE)
        for item in compiled_grammar.finditer(self.program):
            token_type, raw_token = self.__get_token_type(item.groupdict())
            if token_type is None: continue
            tokens.append(
                Token(raw_token, token_type, self.line)
            )
            if token_type == TokenType.STRING: self.line += raw_token.count('\n')
        return tokens
            
    def __get_token_type(self, token):
        if token['IDENTIFIER'] is not None:
            token_type = self.__is_keyword(token['IDENTIFIER'])
            return TokenType.ID if token_type is None else token_type, token['IDENTIFIER']
        elif token['INTEGER'] is not None:
            return TokenType.INTEGER, token['INTEGER']
        elif token['FLOAT'] is not None:
            return TokenType.DOUBLE, token['FLOAT']
        elif token['STRING'] is not None:
            return TokenType.STRING, token['STRING']
        elif token['OPERATOR'] is not None:
            symbol_type = self.__get_symbol(token['OPERATOR'])
            if symbol_type is None: raise TokenError(f"Invalid Token '{token['OPERATOR']}'", self.line)
            return symbol_type, token['OPERATOR']
        elif token['DOT_OPERATOR'] is not None:
            return TokenType.DOT, token['DOT_OPERATOR']
        elif token['NEWLINE'] is not None:
            self.line += 1
            return None, None
        else:
            raise TokenError("Reached Unreachable code @Tokenizer -> get_token_type", self.line)
        
    def __is_keyword(self, identifier):
        return {
            "function": TokenType.KW_FUNCTION,
            "return": TokenType.KW_RETURN,
            "var": TokenType.KW_VAR,
            "const": TokenType.KW_CONST,
            "package": TokenType.KW_PACKAGE, 
            "import": TokenType.KW_IMPORT,
            "pass": TokenType.KW_PASS,
            "main__": TokenType.GHOST_NAME
        }.get(identifier)
    
    def __get_symbol(self, symbol):
        return {
            '(': TokenType.OPEN_PARAM,
            ')': TokenType.CLOSE_PARAM,
            '{': TokenType.OPEN_BRACE,
            '}': TokenType.CLOSE_BRACE,
            ';': TokenType.SEMICOLON,
            '=': TokenType.EQUAL,
            ',': TokenType.COMMA,
            '==': TokenType.EQUAL_EQUAL,
            '!=': TokenType.BANG_EQUAL,
            '>': TokenType.GREATER,
            '<': TokenType.LESSER,
            '>=': TokenType.GREATER_EQUAL,
            '<=': TokenType.LESSER_EQUAL,
            '!': TokenType.NOT,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH
        }.get(symbol)
        
