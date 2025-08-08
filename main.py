import os

from lang.parser import Parser
from lang.tokenizer import Tokenizer
from lang.compiler import Compiler
from lang.utils.generator import Generator
from lang.expections import LoomSyntaxError

def main(file_path):
    with open(file_path) as program_file:
        raw_program = program_file.read()

    with open("lang/token.g") as grammar_file:
        token_grammar = grammar_file.read()

    tokenizer = Tokenizer(raw_program, token_grammar)
    tokens = tokenizer.tokenize()

    generator = Generator(tokens)
    parser = Parser(generator)
    tree = parser.parse()
    if tree is None:
        raise LoomSyntaxError("Incomplete program file")

    # import json
    tree['import'] = list(tree['import'])
    # print(json.dumps(tree, indent=2))

    file = Compiler(tree)
    new_file_path = ".".join(file_path.split(".")[:-1]) + ".go"
    with open(new_file_path, 'w') as compiled_file:
        compiled_file.write(file.compile())

    os.system(f"gofmt -w {new_file_path}")
    print(f"[RUNNING] go run {new_file_path}")
    os.system(f"go run {new_file_path}")
    # os.system(f"del {new_file_path}")

if __name__ == '__main__':
    main("examples/assignment.bz")
