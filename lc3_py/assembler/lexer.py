from dataclasses import dataclass
import re
import typing as t

from lc3_py.type_additions import Result, Err

@dataclass(frozen=True)
class Token:
    line: int
    char: int
    length: int
    lexeme: Result[Lexeme, InvalidLexeme]


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
        super().__init__(f"invalid token '{string}'")
        self._token = string
    @property
    def token(self) -> str:
        return self._token

# class Skip: ...
class EOF: ...

_lex_table_uncompiled: dict[str, t.Callable[[str], Result[Lexeme, InvalidLexeme]]]= {
    r"[\n\r]+": lambda s: Newline(s.count("\n")),
    r"[#x]\d+": lambda s: int(s[1:], 10 if s[0] == "#" else 16),
    r"\.[^\s,]+": lambda s: DotWord(s[1:]),
        r'".*""': lambda s: s[1:-1],
    r"'.*'": lambda s: Char(s[1:-1]),
    r";.*": lambda s: Comment(s[1:]),
    r"[^\d\s,][^\s,]*": Word,
    r".*": InvalidLexeme
}

lex_table = {
    re.compile(r"^[,\s]*(" + regex + r")"): constructor for regex, constructor in _lex_table_uncompiled.items()
}

Lexeme: t.TypeAlias =  Newline | Word | DotWord | int | str | Char

def try_match(pattern: re.Pattern[str], string: str) -> t.Optional[re.Match[str]]:
    """Returns the next match for a patternin a string if it exists."""
    return next(re.finditer(pattern, string), None)

def advance(source: str, pos: int) -> tuple[Lexeme | InvalidLexeme | EOF, int, int]:
    """Get the next lexeme in source[pos:]"""
    if pos >= len(source):
        return EOF(), pos, pos
    for pattern, constructor in lex_table.items():
        match = try_match(pattern, source[pos:])
        if match is None:
            continue

        lexeme_string = match.groups()[0]
        lexeme = constructor(lexeme_string)
        return lexeme, *map(lambda x: x + pos, match.span(0)) # type: ignore
    return EOF(), len(source), len(source)



def lex(source: str) -> Result[list[Token], InvalidTokenPresent]:

    pos = 0
    line_start_char = 0
    line = 1
    tokens: list[Token] = []
    invalid = False
    while True:
        lexeme, start_pos, end_pos = advance(source, pos)
        if isinstance(lexeme, EOF):
            break
        if isinstance(lexeme, InvalidLexeme):
            invalid = True        
        
        tokens.append(Token(line=line,char=pos - line_start_char,length=end_pos-start_pos,lexeme=lexeme))
        if isinstance(lexeme, Newline):
            line += lexeme.number
            line_start_char = end_pos
        pos = end_pos
        
    if invalid:
        return InvalidTokenPresent(tokens)
    return tokens
    

class InvalidTokenPresent(Err):
    def __init__(self, tokens: list[Token]):
        super().__init__("there was at least one invalid token")
        self._tokens = tokens

    @property
    def tokens(self) -> list[Token]:
        return self._tokens