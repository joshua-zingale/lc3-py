import abc
import bisect
from dataclasses import dataclass
import itertools
import re
import typing as t

from lc3_py.type_additions import Err, iserr


# def parsed[_T](obj: t.Optional[_T] | Err) -> t.TypeIs[_T]:
#     return obj is not None and not iserr(obj)


class AdvancingSequence[T](t.Protocol):
    @property
    def pos(self) -> int:
        """The index of the beginning of this sequence in the original sequence"""
        ...
    def advance(self, number: int, /) -> t.Self:
        """Gets a slice self[number:] without copying any memory"""
        ...
    def __getitem__(self, index: int, /) -> T: ...
    def __iter__(self) -> t.Iterator[T]: ...
    def __len__(self) -> int: ...

class Advancer[_T](t.Sequence[_T]):
    def __init__(self, sequence: t.Sequence[_T], _pos: int = 0):
        self._sequence = sequence
        self._pos = _pos
    @property
    def pos(self):
        """The index of the beginning of this sequence in the original sequence"""
        return self._pos
    def advance(self, number: int) -> t.Self:
        """Gets a slice self[number:] without copying any memory"""
        return self.__class__(self._sequence, _pos = number + self._pos)
    def __len__(self):
        return max(len(self._sequence) - self._pos, 0)
    @t.overload
    def __getitem__(self, index: int) -> _T: ...
    @t.overload
    def __getitem__(self, index: slice) -> t.Sequence[_T]: ...
    def __getitem__(self, index: int | slice) -> _T | t.Sequence[_T]:
        if isinstance(index, slice):
            return self._sequence[self.pos:][index]
        return self._sequence[self.pos + index]
    def __str__(self):
        return f"{self.__class__.__name__}({self._sequence[self.pos:]})"
    def __repr__(self):
        return str(self)
    


class StrAdvancer(Advancer[str]):
        
        def __init__(self, sequence: str, *, _pos: int = 0, _view: memoryview | None = None, _byte_offsets: list[int] | None = None):
            super().__init__(sequence, _pos=_pos)

            self._sequence = t.cast(str, self._sequence) # type: ignore

            self._view = _view or memoryview(sequence.encode("utf-8"))
            self._byte_offsets = _byte_offsets or [0, *itertools.accumulate(map(lambda c: len(c.encode()), sequence))]

        def advance(self, number: int) -> t.Self:
            """Gets a slice self[number:] without copying any memory"""
            return self.__class__(self._sequence, _pos = number + self._pos, _view = self._view, _byte_offsets=self._byte_offsets)
        def __buffer__(self, flags: int = 0) -> memoryview:
            return self._view[self._byte_offsets[self._pos]:]
        
        def byte_advance(self, number: int, /) -> t.Self:
            end_byte = self._byte_offsets[self.pos] + number
            positions_to_advance = 0
            while self._byte_offsets[self.pos + positions_to_advance] < end_byte:
                positions_to_advance += 1
            assert self._byte_offsets[self.pos + positions_to_advance] == end_byte
            return self.advance(positions_to_advance)


_In = t.TypeVar("_In")
_Out = t.TypeVar("_Out")
_Err = t.TypeVar("_Err", bound=Err)
CombinatorResult: t.TypeAlias =  tuple[AdvancingSequence[_In], _Out] | _Err
CombinatorFunction: t.TypeAlias = t.Callable[[AdvancingSequence[_In]], CombinatorResult[_In, _Out, _Err]]



class IndexToPositionConverter:
    def __init__(self, text: str):
        self._line_starts = [0]
        for i, char in enumerate(text):
            if char == "\n":
                self._line_starts.append(i + 1)
            elif char == "\r" and not (i + 1 < len(text) and text[i + 1] == "\n"):
                self._line_starts.append(i + 1)
    def get(self, index: int) -> Position:
        if index < 0:
            raise ValueError("Index cannot be negative.")
        line_index = bisect.bisect_right(self._line_starts, index) - 1
        line_start_index = self._line_starts[line_index]
        char_offset = index - line_start_index
        return Position(line=line_index + 1, char=char_offset)


@dataclass(frozen=True)
class Position:
    line: int
    char: int


@dataclass(frozen=True)
class Token[T]:
    obj: T
    span: Span


@dataclass(frozen=True)
class ErrToken(Err):
    start: int

    def __init__(self, message: str, start: int):
        super().__init__(message)
        object.__setattr__(self, 'start', start)

@dataclass(frozen=True)
class Span():
    start: int
    end: int


@dataclass(frozen=True)
class Combinator(abc.ABC, t.Generic[_In, _Out, _Err]):
    function: CombinatorFunction[_In, _Out, _Err]
    name: str
    

    def as_token(self) -> Combinator[_In, Token[_Out], ErrToken]:
        @combinator(f"with_token({self.name})")
        def comb(seq: AdvancingSequence[_In]):
            start = seq.pos
            res = self(seq)
            if iserr(res):
                return ErrToken(res.error, start=start)
            return res[0], Token(res[1], span=Span(start=start, end=res[0].pos))
        return comb
            

    def postskip(self, skipper: Combinator[_In, t.Any, Err]) -> Combinator[_In, _Out, _Err]:
        @combinator(f"skipper({self.name})")
        def comb(seq: AdvancingSequence[_In]):
            res = self(seq)
            if iserr(res):
                return res
            obj = res[1]
            seq = res[0]
            while not iserr(res := skipper(seq)):
                seq = res[0]

            return seq, obj
        return comb
    
    def preskip(self, skipper: Combinator[_In, t.Any, Err]) -> Combinator[_In, _Out, _Err]:
        @combinator(f"skipper({self.name})")
        def comb(seq: AdvancingSequence[_In]):
            while not iserr(res := skipper(seq)):
                seq = res[0]
            res = self(seq)
            return res
        return comb

    def parse_many(self, seq: t.Sequence[_In]) -> t.Sequence[_Out] | Err:
        out: list[_Out] = []

        inp_advancer = sequence_to_advancer(seq)
    
        while not iserr(v := self(inp_advancer)):
            out.append(v[1])
            inp_advancer = v[0]
        if len(inp_advancer) > 0:
            return v
        return out
    
    def parse(self, seq: t.Sequence[_In]) -> _Out | Err:
        inp_advancer = sequence_to_advancer(seq)
        if iserr(v := self(inp_advancer)):
            return v
        
        if len(v[0]) > 0:
            return Err("extra tokens found after parsing")
        return v[1]

    def __call__(self, inp: AdvancingSequence[_In]) -> CombinatorResult[_In, _Out]:
        return self.function(inp)
    def __or__(self, other: Combinator[_In, _T]):
        @combinator(f"{self.name} | {other.name}")
        def comb(seq: AdvancingSequence[_In]) -> CombinatorResult[_In, _Out | _T]:
            res = self(seq)
            if iserr(res):
                return other(seq)
            return res
        return comb


            


def sequence_to_advancer[T](seq: t.Sequence[T]) -> AdvancingSequence[T]:
    if isinstance(seq, str):
        return StrAdvancer(seq) # type: ignore
    elif isinstance(seq, Advancer):
        return seq # type: ignore
    else:
        return Advancer(seq) # type: ignore
    
def optimize_str_advancer(advancer: AdvancingSequence[str]) -> StrAdvancer:
    if isinstance(advancer, StrAdvancer):
        return advancer
    return StrAdvancer(*advancer, _pos = advancer.pos)




@t.overload
def combinator(name: str, /) -> t.Callable[[CombinatorFunction[_In, _Out, _Err]], Combinator[_In, _Out, _Err]]: ...
@t.overload
def combinator(function: CombinatorFunction[_In, _Out, _Err], /) -> Combinator[_In, _Out, _Err]: ...
def combinator(name_or_function: CombinatorFunction[_In, _Out, _Err] | str, /) -> Combinator[_In, _Out, _Err] | t.Callable[[CombinatorFunction[_In, _Out, _Err]], Combinator[_In, _Out, _Err]]:
    if isinstance(name_or_function, str):
        def wrapped(function: CombinatorFunction[_In, _Out, _Err]):
            return Combinator[_In, _Out, _Err](function=function, name=name_or_function)
        return wrapped
    return Combinator(function=name_or_function, name=name_or_function.__name__)


def start_match(t1: AdvancingSequence[t.Any], t2: t.Sequence[t.Any], ) -> bool:
    return len(t1) >= len(t2) and all([e1 == e2 for e1, e2 in zip(t1, t2)])

def string(string: str):
    if len(string) == 0:
        raise ValueError("string must be nonempty")
    @combinator(f"'{string}'")
    def c(seq: AdvancingSequence[str]):
        if start_match(seq, string):
            return seq.advance(len(string)), string
        return Err("")
    return c


def regex(pattern: str):
    if len(pattern) == 0:
        raise ValueError("pattern must be nonempty")
    compiled_pattern = re.compile(f"{pattern}".encode())
    @combinator(f"r'{pattern}'")
    def c(seq: AdvancingSequence[str]):
        seq = optimize_str_advancer(seq)
        match = next(re.finditer(compiled_pattern, seq), Err(f"expected r'{pattern}'"))
        if iserr(match):
            return match
        return seq.byte_advance(match.end()), tuple(map(bytes.decode, match.groups())) or bytes.decode(match.group(0))
    return c

