
from lc3_py.type_additions import iserr
from lc3_py.assembler.lexer import *
def test_line():

    tokens = lex("lea r0, label_here\n    add r0, r1, #20")
    assert not iserr(tokens)
    # assert len(tokens) == 3, tokens
    # assert isinstance(tokens[0].lexeme, Word)
    # assert isinstance(tokens[1].lexeme, Word)
    # assert isinstance(tokens[2].lexeme, Word)
    # assert tokens[0].lexeme.value == "lea"
    # assert tokens[1].lexeme.value == "r0"
    # assert tokens[2].lexeme.value == "label_here"

    print(tokens)