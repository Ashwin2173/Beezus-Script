from lang.parser import Parser
from lang.tokenizer import Tokenizer
from lang.utils.generator import Generator
from lang.expections import LoomSyntaxError

def main(file_path):
    raw_program = None
    token_grammer = None

    with open(file_path) as program_file:
        raw_program = program_file.read()

    with open("lang/token.g") as grammer_file:
        token_grammer = grammer_file.read()

    tokenizer = Tokenizer(raw_program, token_grammer)
    tokens = tokenizer.tokenize()

    generator = Generator(tokens)
    parser = Parser(generator)
    tree = parser.parse()
    if tree is None:
        raise LoomSyntaxError("Incomplete program file")

    import json
    tree['import'] = list(tree['import'])
    print(json.dumps(tree, indent=2))
    
if __name__ == '__main__':
    main("examples/main.ls")