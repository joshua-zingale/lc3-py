from dataclasses import dataclass
import re
import typing as t

from lc3_py.type_additions import Result, Err, iserr, has_no_err

@dataclass(frozen=True)
class Token:
    line: int
    char: int
    length: int
    lexeme: Lexeme

@dataclass(frozen=True)
class InvalidToken(Err):
    line: int
    char: int
    length: int
    lexeme: InvalidLexeme

    def __init__(self, line: int, char: int, length: int, lexeme: InvalidLexeme):
        super().__init__(f"'{lexeme.value}' is not a valid token")
        object.__setattr__(self, 'line', line)
        object.__setattr__(self, 'char', char)
        object.__setattr__(self, 'length', length)
        object.__setattr__(self, 'lexeme', lexeme)

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
        self._value = string
    @property
    def value(self) -> str:
        return self._value

class EOF: ...

_lex_table_uncompiled: dict[str, t.Callable[[str], Result[Lexeme, InvalidLexeme]]]= {
    r"[\n\r][\s\n\r]*": lambda s: Newline(s.count("\n")),
    r"[#xX]\d+": lambda s: int(s[1:], 10 if s[0] == "#" else 16),
    r"\.[^\s,]+": lambda s: DotWord(s[1:]),
        r'".*"': lambda s: s[1:-1],
    r"'.*'": lambda s: Char(s[1:-1]),
    r";[^\n\r]*": lambda s: Comment(s[1:]),
    r"[^\d\s,][^\s,]*": Word,
    r"\S*": InvalidLexeme
}

_lex_table = {
    re.compile(r"^[,\t ]*(" + regex + r")[,\t ]*"): constructor for regex, constructor in _lex_table_uncompiled.items()
}

Lexeme: t.TypeAlias =  Newline | Word | DotWord | int | str | Char | Comment

def _try_match(pattern: re.Pattern[str], string: str) -> t.Optional[re.Match[str]]:
    """Returns the next match for a patternin a string if it exists."""
    return next(re.finditer(pattern, string), None)

def _advance(source: str, pos: int) -> tuple[Lexeme | InvalidLexeme | EOF, int, int]:
    """Get the next lexeme in source[pos:]"""
    if pos >= len(source):
        return EOF(), pos, pos
    for pattern, constructor in _lex_table.items():
        match = _try_match(pattern, source[pos:])
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
    tokens: list[Token | InvalidToken] = []
    while True:
        lexeme, start_pos, end_pos = _advance(source, pos)
        if isinstance(lexeme, EOF):
            break
        
        if iserr(lexeme):
            tokens.append(InvalidToken(line=line,char=pos - line_start_char,length=end_pos-start_pos,lexeme=lexeme))
        else:
            tokens.append(Token(line=line,char=pos - line_start_char,length=end_pos-start_pos,lexeme=lexeme))

        if isinstance(lexeme, Newline):
            line += lexeme.number
            line_start_char = end_pos
        pos = end_pos
        
    if has_no_err(tokens):
        return tokens
    return InvalidTokenPresent(tokens)
    

class InvalidTokenPresent(Err):
    def __init__(self, tokens: list[Token | InvalidToken]):
        super().__init__("there was at least one invalid token")
        self._tokens = tokens

    @property
    def tokens(self) -> list[Token | InvalidToken]:
        return self._tokens