import typing as t
from lc3_py.type_additions import iserr
from lc3_py.assembler.lexer import *

def test_hello_world():

    matches = lex_lc3("""
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
    assert not iserr(matches)
    for lexed_token, lexeme in zip(matches, should_be):
        assert lexed_token.lexeme == lexeme
    assert len(matches) == len(should_be)


def test_spans():
    source = """
.ORIG x3000
LEA R0, , label-here ; Comment here is #1 and x13 X13 "WOW"!!! oh yea
                 
      PUTS
HALT
label-here .STRINGZ,    "Hello, World!"
.END
"""
    matches = lex_lc3(source)
    assert not iserr(matches)
    comment = next(filter(lambda m: not iserr(m) and isinstance(m.lexeme, Comment), matches))
    dot_word = next(filter(lambda m: not iserr(m) and isinstance(m.lexeme, DotWord), matches[2:]))

    comment_text = '; Comment here is #1 and x13 X13 "WOW"!!! oh yea'
    dot_word_text = ".STRINGZ"

    assert comment.span.start == source.find(comment_text) and comment.span.end == source.find(comment_text) + len(comment_text)
    assert dot_word.span.start == source.find(dot_word_text) and dot_word.span.end == source.find(dot_word_text) + len(dot_word_text)


def test_hello_world_with_error():
    source = """
.ORIG x3000
LEA R0, , label-here ; Comment here is #1 and x13 X13 "WOW"!!! oh yea
                 123abc
      PUTS
HALT
label-here .STRINGZ,    "Hello, World!"
.END
"""
    matches = lex_lc3(source)
    should_be: list[Lexeme | t.Type[Err]] = [
        Newline(1),
        DotWord("ORIG"), 0x3000, Newline(1),
        Word("LEA"), Word("R0"), Word("label-here"), Comment(" Comment here is #1 and x13 X13 \"WOW\"!!! oh yea"), Newline(1),
        Err, Newline(1),
        Word("PUTS"), Newline(1),
        Word("HALT"), Newline(1),
        Word("label-here"), DotWord("STRINGZ"), "Hello, World!", Newline(1),
        DotWord("END"), Newline(1),
    ]
    assert iserr(matches)
    for lexed_token, lexeme in zip(matches.matches, should_be):
        if iserr(lexed_token):
            assert lexeme is Err
            assert lexed_token.span.start == source.find("123abc") and  lexed_token.span.end == source.find("123abc") + len("123abc")
        else:
            assert lexed_token.lexeme == lexeme
    assert len(matches.matches) == len(should_be)