from lang.utils.ast_node import NodeType, get_default_type_mapping

class Compiler:
    def __init__(self, program):
        self.program = program
        self.compiled = [self.load_default()]

    def load_default(self):
        with open("lang/default.go") as default_go:
            return default_go.read()

    def compile(self):
        body = self.program['body']
        for statement in body:
            _type = statement['type']
            if _type == NodeType.FUNCTION_DECLARATION:
                name = statement['name']
                return_type = get_default_type_mapping(statement['returnType'])
                params = ", ".join([f"{p_name} {get_default_type_mapping(p_type)}"
                                    for p_name, p_type in statement['params']])
                self.compiled.append(f"func {name}({params}) {return_type} {{")
                self.compile_statements(statement['body'])
                self.compiled.append("}")
            else:
                raise Exception("Unimplemented global statement: " + str(_type))
        return "\n".join(self.compiled)

    def compile_statements(self, statements):
        for statement in statements:
            self.compiled.append(self.get_compiled_statement(statement))

    def get_compiled_statement(self, statement):
        _type = statement['type']
        if _type in {NodeType.VARIABLE_DECLARATION, NodeType.CONSTANTS_DECLARATION}:
            declaration_type = "var" if _type == NodeType.VARIABLE_DECLARATION else "const"
            data_type = get_default_type_mapping(statement['dataType'])
            name = statement['variable']
            expression = self.get_compiled_expression(statement['expression'])
            return f"{declaration_type} {name} {data_type} = {expression}"
        elif _type == NodeType.EXPRESSION:
            return self.get_compiled_expression(statement['expression'])
        elif _type == NodeType.RETURN_DECLARATION:
            expression = self.get_compiled_expression(statement['expression'])
            return f"return {expression}"
        elif _type == NodeType.IF_STATEMENT:
            expression = self.get_compiled_expression(statement['test'])
            compiled_consequent = self.get_compiled_statement(statement['consequent'])
            compiled_if = f"if {expression} {{ {compiled_consequent} }}"
            if statement['alternate'] is not None:
                compiled_alternate = self.get_compiled_statement(statement['alternate'])
                compiled_if = f"{compiled_if} else {{ {compiled_alternate} }}"
            return compiled_if
        elif _type == NodeType.BLOCK_STATEMENT:
            return "\n".join([self.get_compiled_statement(line) for line in statement['body']])
        else:
            raise Exception("Unimplemented inner statement: " + str(_type))

    def get_compiled_expression(self, expression):
        _type = expression['type']
        if _type == NodeType.EXPRESSION:
            return self.get_compiled_expression(expression['expression'])
        elif _type in {NodeType.STRING_LITERAL, NodeType.INTEGER_LITERAL}:
            return str(expression['value'])
        elif _type == NodeType.IDENTITY:
            return expression['name']
        elif _type == NodeType.BINARY_EXPRESSION:
            left = self.get_compiled_expression(expression['left'])
            right = self.get_compiled_expression(expression['right'])
            return f"{left} {expression['operation']} {right}"
        elif _type == NodeType.CALL_EXPRESSION:
            name = self.get_membership_name(expression['callee'])
            arguments = ", ".join([
                self.get_compiled_expression(argument) for argument in expression['arguments']])
            return f"{name}({arguments})"
        else:
            raise Exception("Unimplemented expression type: " + str(_type))

    def get_membership_name(self, membership):
        _type = membership['type']
        if _type == NodeType.IDENTITY:
            return membership['name']
        elif _type == NodeType.MEMBERSHIP_EXPRESSION:
            return membership['name'] + "_" + self.get_membership_name(membership['property'])
        else:
            raise Exception("Unimplemented membership expression type: " + str(_type))