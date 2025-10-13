from dataclasses import dataclass
import enum
import typing as t

from lc3_py.type_additions import Err

from .n_bit_number import SixteenBitNumber

@dataclass(frozen=True)
class Blkw:
    number: int

@dataclass(frozen=True)
class End: pass

@dataclass(frozen=True)
class Fill:
    data: SixteenBitNumber

@dataclass(frozen=True)
class Orig:
    string: str

@dataclass(frozen=True)
class Stringz:
    string: str

Directives: t.TypeAlias = Blkw | End | Fill | Orig | Stringz






