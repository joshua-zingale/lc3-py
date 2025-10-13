from dataclasses import dataclass
import enum
import typing as t

from lc3_py.type_additions import Err

class Register(enum.StrEnum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"
    R6 = "R6"
    R7 = "R7"

def _construct_n_bit[T](constructor: t.Callable[[int], T], value: int, bits: int) -> T | Err:
    if value >= 2**(bits-1) or value < 2**(bits-1):
        return Err(f"the number '{value}' (base 10) can not be fit into {bits} bits as a signed integer.")
    return constructor(value)


class FiveBitNumber(int):
    @staticmethod
    def new(value: int) -> FiveBitNumber | Err:
        return _construct_n_bit(FiveBitNumber, value, 5)
    
class SixBitNumber(int):
    @staticmethod
    def new(value: int) -> SixBitNumber | Err:
        return _construct_n_bit(SixBitNumber, value, 6)
    
class EightBitNumber(int):
    @staticmethod
    def new(value: int) -> EightBitNumber | Err:
        return _construct_n_bit(EightBitNumber, value, 8)

class NineBitNumber(int):
    @staticmethod
    def new(value: int) -> NineBitNumber | Err:
        return _construct_n_bit(NineBitNumber, value, 9)
    
class ElevenBitNumber(int):
    @staticmethod
    def new(value: int) -> ElevenBitNumber | Err:
        return _construct_n_bit(ElevenBitNumber, value, 11)
    
@dataclass(frozen=True)
class Add:
    destination: Register
    operand_1: Register
    operand_2: Register

@dataclass(frozen=True)
class AddIm:
    destination: Register
    operand_1: Register
    operand_2: FiveBitNumber

@dataclass(frozen=True)
class And:
    destination: Register
    operand_1: Register
    operand_2: Register

@dataclass(frozen=True)
class AndIm:
    destination: Register
    operand_1: Register
    operand_2: FiveBitNumber

@dataclass(frozen=True)
class Br:
    n: bool
    z: bool
    p: bool
    pc_offset: NineBitNumber


@dataclass(frozen=True)
class Jmp:
    base_register: Register

@dataclass(frozen=True)
class Jsr:
    pc_offset: ElevenBitNumber

@dataclass(frozen=True)
class Jsrr:
    base_register: Register

@dataclass(frozen=True)
class Ld:
    destination: Register
    pc_offset: NineBitNumber

@dataclass(frozen=True)
class Ldi:
    destination: Register
    pc_offset: NineBitNumber

@dataclass(frozen=True)
class Ldr:
    destination: Register
    base_register: Register
    offset: SixBitNumber

@dataclass(frozen=True)
class Lea:
    destination: Register
    pc_offset: NineBitNumber

@dataclass(frozen=True)
class Not:
    destination: Register
    source: Register

@dataclass(frozen=True)
class Ret: pass

@dataclass(frozen=True)
class Rti: pass

@dataclass(frozen=True)
class St:
    source: Register
    pc_offset: NineBitNumber

@dataclass(frozen=True)
class Sti:
    source: Register
    pc_offset: NineBitNumber

@dataclass(frozen=True)
class Str:
    source: Register
    base_register: Register
    offset: SixBitNumber

@dataclass(frozen=True)
class Trap:
    vector: EightBitNumber




@dataclass(frozen=True)
class LabelBr:
    n: bool
    z: bool
    p: bool
    label: str 

@dataclass(frozen=True)
class LabelJsr:
    pc_offset: ElevenBitNumber

@dataclass(frozen=True)
class LabelLd:
    destination: Register
    label: str

@dataclass(frozen=True)
class LabelLdi:
    destination: Register
    label: str

@dataclass(frozen=True)
class LabelLea:
    destination: Register
    label: str

@dataclass(frozen=True)
class LabelSt:
    source: Register
    label: str

@dataclass(frozen=True)
class LabelSti:
    source: Register
    label: str



InstructionWithoutPcOffset: t.TypeAlias = Add | AddIm | And | AndIm | Jmp | Jsrr | Ldr | Not | Ret | Rti | Str | Trap
InstructionWithPcOffset: t.TypeAlias =  Br | Jsr | Ld | Ldi | Lea | St | Sti
Instruction: t.TypeAlias = InstructionWithoutPcOffset | InstructionWithPcOffset
InstructionWithLabel: t.TypeAlias = LabelBr | LabelJsr | LabelLd | LabelLdi | LabelLea | LabelSt | LabelSti


