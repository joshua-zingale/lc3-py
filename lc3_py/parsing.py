from dataclasses import dataclass
import re
import typing as t

from lc3_py.type_additions import Err, has_no_err, iserr


_T = t.TypeVar("_T")
InputSequence: t.TypeAlias = t.Sequence[_T]

_Lexeme = t.TypeVar("_Lexeme", covariant=True)


class SpanProtocol(t.Protocol):
    @property
    def start(self) -> int:
        """The starting index"""
        ...
    @property
    def end(self) -> int:
        """One greater than the last index"""
        ...

@dataclass(frozen=True)
class Span:
    start: int
    end: int

@dataclass(frozen=True)
class SpanWithLine:
    line: int
    char_in_line: int
    start: int
    end: int

    @property
    def length(self):
        return self.end - self.start

_Span = t.TypeVar("_Span", bound=SpanProtocol)
@dataclass(frozen=True)
class Match(t.Generic[_Lexeme, _Span]):
    lexeme: _Lexeme
    span: _Span


@dataclass(frozen=True)
class ErrMatch(Err, t.Generic[_Span]):
    span: _Span

    def __init__(self, message: str, span: _Span):
        super().__init__(message)
        object.__setattr__(self, 'span', span)


MatchFunction: t.TypeAlias = t.Callable[[InputSequence[_T], int], t.Optional[Match[_Lexeme, _Span] | ErrMatch[_Span]]]
SkipFunction: t.TypeAlias = t.Callable[[InputSequence[_T], int], int]


def match_first(
        input_sequence: InputSequence[_T],
        position: int,
        match_functions: t.Sequence[MatchFunction[_T, _Lexeme, _Span]],
        ) -> t.Optional[Match[_Lexeme, _Span] | ErrMatch[_Span]]:
    if position >= len(input_sequence):
        return None
    return next(filter(None, [match_function(input_sequence, position) for match_function in match_functions]))


# PatternRegexMapping: t.TypeAlias = t.Mapping[re.Pattern[str], t.Callable[[tuple[str, ...]], _Lexeme | Err]]
StringRegexMapping: t.TypeAlias = t.Mapping[str, t.Callable[[tuple[str, ...]], _Lexeme | Err]]
# RegexMapping: t.TypeAlias = PatternRegexMapping[_Lexeme] | StringRegexMapping[_Lexeme]
def get_match_functions_from_regex(mapping: StringRegexMapping[_Lexeme]) -> t.Sequence[MatchFunction[str, _Lexeme, Span]]:

    match_functions: list[MatchFunction[str, _Lexeme, Span]] = []
    for pattern, constructor in mapping.items():
        pattern = re.compile("^(" + pattern + ")")
        def match_function(
                input_sequence: t.Sequence[str],
                position: int,
                pattern: re.Pattern[str] = pattern,
                constructor: t.Callable[[tuple[str, ...]], _Lexeme | Err] = constructor) -> t.Optional[Match[_Lexeme, Span] | ErrMatch]:
            
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
        match_functions: t.Sequence[MatchFunction[_T, _Lexeme, _Span]],
        skip_function: t.Optional[SkipFunction[_T]] = None) -> t.Sequence[Match[_Lexeme, _Span]] | InvalidSequence[_Lexeme, _Span]:

    pos = 0
    matches: list[Match[_Lexeme, _Span] | ErrMatch] = []
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
    

class InvalidSequence(Err, t.Generic[_Lexeme, _Span]):
    def __init__(self, matches: list[Match[_Lexeme, _Span] | ErrMatch[_Span]]):
        super().__init__("there was at least one invalid lexeme")
        self._matches = matches

    @property
    def matches(self) -> list[Match[_Lexeme, _Span] | ErrMatch[_Span]]:
        return self._matches