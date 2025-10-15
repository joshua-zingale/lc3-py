from dataclasses import dataclass
import typing as t

from lc3_py.type_additions import Err
import lc3_py.lexing as lexing

@dataclass(frozen=True)
class Newline:
    number: int

@dataclass(frozen=True)
class Word:
    value: str

    def __eq__(self, other: t.Any):
        return isinstance(other, Word) and self.value.lower() == other.value.lower()
    def __hash__(self):
        return hash(self.value.lower())

@dataclass(frozen=True)
class DotWord:
    value: str

@dataclass(frozen=True)
class Char:
    value: str

@dataclass(frozen=True)
class Comment:
    value: str

@dataclass(frozen=True)
class Integer:
    value: int
    string: str


class InvalidLexeme(Err):
    def __init__(self, string: str):
        super().__init__(f"invalid chatacter sequence '{string}'")
        self._value = string
    @property
    def value(self) -> str:
        return self._value


_lex_table: lexing.StringRegexMapping[Lexeme] = {
    r"[\n\r][\s\n\r]*": lambda g: Newline(g[0].count("\n")),
    r"[#xX]\d+": lambda g: Integer(int(g[0][1:], 10 if g[0] == "#" else 16), g[0]),
    r"\.[^\s,]+": lambda g: DotWord(g[0][1:]),
    r'".*"': lambda g: g[0][1:-1],
    r"'.*'": lambda g: Char(g[0][1:-1]),
    r";[^\n\r]*": lambda g: Comment(g[0][1:]),
    r"[^\d\s,][^\s,]*": lambda g: Word(g[0]),
    r"\S*": lambda g: InvalidLexeme(g[0])
}

_match_functions = lexing.get_match_functions_from_regex(_lex_table)

Lexeme: t.TypeAlias =  Newline | Word | DotWord | Integer | str | Char | Comment

_skip_chars = ",\t "

def _skip_function(input_sequence: t.Sequence[str], position: int):
    while position < len(input_sequence) and input_sequence[position] in _skip_chars:
        position += 1
    return position


def lex_lc3(source: str) -> t.Sequence[lexing.Match[Lexeme]] | lexing.InvalidSequence[Lexeme]:
    return lexing.lex(source, _match_functions, _skip_function)