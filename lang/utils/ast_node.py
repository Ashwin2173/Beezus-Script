class NodeType:
    RETURN_DECLARATION = 0
    VARIABLE_DECLARATION = 1
    CONSTANTS_DECLARATION = 2
    FUNCTION_DECLARATION = 3
    CALL_EXPRESSION = 4
    EXPRESSION = 5
    BINARY_EXPRESSION = 6
    UNARY_EXPRESSION = 7
    INTEGER_LITERAL = 8
    STRING_LITERAL = 9
    DOUBLE_LITERAL = 10
    MEMBERSHIP_EXPRESSION = 11
    IDENTITY = 12

def get_default_type_mapping(_type):
    default_types = {
        "integer": "int64",
        "string": "string",
        "double": "float64",
        "void": ""
    }
    return default_types.get(_type) if _type in default_types else _type