from dataclasses import dataclass
import re
import typing as t

from lc3_py.type_additions import Result, Err
import lc3_py.parsing as parsing

@dataclass(frozen=True)
class Newline:
    number: int

@dataclass(frozen=True)
class Word:
    value: str

@dataclass(frozen=True)
class DotWord:
    value: str

@dataclass(frozen=True)
class Char:
    value: str

@dataclass(frozen=True)
class Comment:
    value: str


class InvalidLexeme(Err):
    def __init__(self, string: str):
        super().__init__(f"invalid chatacter sequence '{string}'")
        self._value = string
    @property
    def value(self) -> str:
        return self._value


_lex_table: parsing.StringRegexMapping[Lexeme] = {
    r"[\n\r][\s\n\r]*": lambda g: Newline(g[0].count("\n")),
    r"[#xX]\d+": lambda g: int(g[0][1:], 10 if g[0] == "#" else 16),
    r"\.[^\s,]+": lambda g: DotWord(g[0][1:]),
    r'".*"': lambda g: g[0][1:-1],
    r"'.*'": lambda g: Char(g[0][1:-1]),
    r";[^\n\r]*": lambda g: Comment(g[0][1:]),
    r"[^\d\s,][^\s,]*": lambda g: Word(g[0]),
    r"\S*": lambda g: InvalidLexeme(g[0])
}

_match_functions = parsing.get_match_functions_from_regex(_lex_table)

Lexeme: t.TypeAlias =  Newline | Word | DotWord | int | str | Char | Comment

_skip_chars = ",\t "

def _skip_function(input_sequence: t.Sequence[str], position: int):
    while position < len(input_sequence) and input_sequence[position] in _skip_chars:
        position += 1
    return position


def lex_lc3(source: str) -> t.Sequence[parsing.Match[Lexeme, parsing.Span]] | parsing.InvalidSequence[Lexeme, parsing.Span]:
    return parsing.lex(source, _match_functions, _skip_function)