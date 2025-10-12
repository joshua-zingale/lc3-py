
from lc3_py.type_additions import iserr
from lc3_py.assembler.lexer import *
def test_hello_world():

    tokens = lex("""
.ORIG x3000
LEA R0, , label-here ; Comment here is #1 and x13 X13 "WOW"!!! oh yea
                 
      PUTS
HALT
label-here .STRINGZ,    "Hello, World!"
.END
""")
    should_be: list[Lexeme] = [
        Newline(1),
        DotWord("ORIG"), 0x3000, Newline(1),
        Word("LEA"), Word("R0"), Word("label-here"), Comment(" Comment here is #1 and x13 X13 \"WOW\"!!! oh yea"), Newline(2),
        Word("PUTS"), Newline(1),
        Word("HALT"), Newline(1),
        Word("label-here"), DotWord("STRINGZ"), "Hello, World!", Newline(1),
        DotWord("END"), Newline(1),
    ]
    assert not iserr(tokens)
    for lexed_token, lexeme in zip(tokens, should_be):
        assert lexed_token.lexeme == lexeme
    assert len(tokens) == len(should_be)
