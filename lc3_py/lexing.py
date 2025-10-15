from dataclasses import dataclass
import re
import typing as t

from lc3_py.type_additions import Err, has_no_err, iserr


_T = t.TypeVar("_T")
InputSequence: t.TypeAlias = t.Sequence[_T]

_Lexeme = t.TypeVar("_Lexeme", covariant=True)

@dataclass(frozen=True)
class Span:
    start: int
    end: int

@dataclass(frozen=True)
class Match(t.Generic[_Lexeme]):
    lexeme: _Lexeme
    span: Span


@dataclass(frozen=True)
class ErrMatch(Err):
    span: Span

    def __init__(self, message: str, span: Span):
        super().__init__(message)
        object.__setattr__(self, 'span', span)


class AdvancingSequence[_T]:
    def __init__(self, sequence: t.Sequence[_T], _pos: int = 0):
        self._sequence = sequence
        self._pos = _pos
    @property
    def pos(self):
        """The index of the beginning of this sequence in the original sequence"""
        return self._pos
    def advance(self, number: int) -> AdvancingSequence[_T]:
        """Gets a slice self[number:] without copying any memory"""
        return AdvancingSequence(self._sequence, _pos = number + self._pos)
    def __len__(self):
        return max(len(self._sequence) - self._pos, len(self._sequence))
    @t.overload
    def __getitem__(self, index: int) -> _T: ...
    @t.overload
    def __getitem__(self, index: slice) -> t.Sequence[_T]: ...
    def __getitem__(self, index: int | slice) -> _T | t.Sequence[_T]:
        return self._sequence[self.pos:][index]
    def __str__(self):
        return f"{self.__class__.__name__}({self._sequence[self.pos:]})"
    def __repr__(self):
        return str(self)

class AdvancingStr(AdvancingSequence[str]):
        def __init__(self, sequence: str, _pos: int = 0, _view: memoryview | None = None):
            super().__init__(sequence, _pos=_pos)
            if not sequence.isascii():
                raise ValueError("Sequence must only contain ASCII characters")
            self._buffer_cache = None
            self._sequence = t.cast(str, self._sequence) # type: ignore
            if _view is None:
                self._view = memoryview(sequence.encode("utf-8"))
            else:
                self._view = _view
        def __buffer__(self, flags: int = 0) -> memoryview:
            return self._view[self._pos:]


MatchFunction: t.TypeAlias = t.Callable[[InputSequence[_T], int], t.Optional[Match[_Lexeme] | ErrMatch]]
SkipFunction: t.TypeAlias = t.Callable[[InputSequence[_T], int], int]


def match_first(
        input_sequence: InputSequence[_T],
        position: int,
        match_functions: t.Sequence[MatchFunction[_T, _Lexeme]],
        ) -> t.Optional[Match[_Lexeme] | ErrMatch]:
    if position >= len(input_sequence):
        return None
    return next(filter(None, [match_function(input_sequence, position) for match_function in match_functions]))


# PatternRegexMapping: t.TypeAlias = t.Mapping[re.Pattern[str], t.Callable[[tuple[str, ...]], _Lexeme | Err]]
StringRegexMapping: t.TypeAlias = t.Mapping[str, t.Callable[[tuple[str, ...]], _Lexeme | Err]]
# RegexMapping: t.TypeAlias = PatternRegexMapping[_Lexeme] | StringRegexMapping[_Lexeme]
def get_match_functions_from_regex(mapping: StringRegexMapping[_Lexeme]) -> t.Sequence[MatchFunction[str, _Lexeme]]:

    match_functions: list[MatchFunction[str, _Lexeme]] = []
    for pattern, constructor in mapping.items():
        pattern = re.compile("^(" + pattern + ")")
        def match_function(
                input_sequence: t.Sequence[str],
                position: int,
                pattern: re.Pattern[str] = pattern,
                constructor: t.Callable[[tuple[str, ...]], _Lexeme | Err] = constructor) -> t.Optional[Match[_Lexeme] | ErrMatch]:
            
            assert isinstance(input_sequence, str)

            match = next(re.finditer(pattern, input_sequence[position:]), None)
            if match:
                span = Span(start = position + match.span(0)[0], end= position + match.span(0)[1])
                lexeme = constructor(match.groups())
                if iserr(lexeme):
                    return ErrMatch(lexeme.error, span)
                return Match(
                    lexeme=lexeme,
                    span=span)
            return None

        match_functions.append(match_function)
    return match_functions



def lex(
        input_sequence: InputSequence[_T],
        match_functions: t.Sequence[MatchFunction[_T, _Lexeme]],
        skip_function: t.Optional[SkipFunction[_T]] = None) -> t.Sequence[Match[_Lexeme]] | InvalidSequence[_Lexeme]:

    pos = 0
    matches: list[Match[_Lexeme] | ErrMatch] = []
    while True:
        if skip_function:
            pos = skip_function(input_sequence, pos)
        match = match_first(input_sequence, pos, match_functions)
        if not match:
            break
        matches.append(match)
        pos = match.span.end
        
    if has_no_err(matches):
        return matches
    return InvalidSequence(matches)
    

class InvalidSequence(Err, t.Generic[_Lexeme]):
    def __init__(self, matches: list[Match[_Lexeme] | ErrMatch]):
        super().__init__("there was at least one invalid lexeme")
        self._matches = matches

    @property
    def matches(self) -> list[Match[_Lexeme] | ErrMatch]:
        return self._matches