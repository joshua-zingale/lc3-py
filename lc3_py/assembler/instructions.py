from dataclasses import dataclass
import enum
import typing as t

from lc3_py.type_additions import Err

from lc3_py.assembler.n_bit_number import FiveBitSigned, SixBitSigned, EightBitSigned, NineBitSigned, ElevenBitSigned

class Register(enum.StrEnum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"
    R6 = "R6"
    R7 = "R7"

@dataclass(frozen=True)
class Add:
    destination: Register
    operand_1: Register
    operand_2: Register

@dataclass(frozen=True)
class AddIm:
    destination: Register
    operand_1: Register
    operand_2: FiveBitSigned

@dataclass(frozen=True)
class And:
    destination: Register
    operand_1: Register
    operand_2: Register

@dataclass(frozen=True)
class AndIm:
    destination: Register
    operand_1: Register
    operand_2: FiveBitSigned

@dataclass(frozen=True)
class Br:
    n: bool
    z: bool
    p: bool
    pc_offset: NineBitSigned


@dataclass(frozen=True)
class Jmp:
    base_register: Register

@dataclass(frozen=True)
class Jsr:
    pc_offset: ElevenBitSigned

@dataclass(frozen=True)
class Jsrr:
    base_register: Register

@dataclass(frozen=True)
class Ld:
    destination: Register
    pc_offset: NineBitSigned

@dataclass(frozen=True)
class Ldi:
    destination: Register
    pc_offset: NineBitSigned

@dataclass(frozen=True)
class Ldr:
    destination: Register
    base_register: Register
    offset: SixBitSigned

@dataclass(frozen=True)
class Lea:
    destination: Register
    pc_offset: NineBitSigned

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
    pc_offset: NineBitSigned

@dataclass(frozen=True)
class Sti:
    source: Register
    pc_offset: NineBitSigned

@dataclass(frozen=True)
class Str:
    source: Register
    base_register: Register
    offset: SixBitSigned

@dataclass(frozen=True)
class Trap:
    vector: EightBitSigned




@dataclass(frozen=True)
class LabelBr:
    n: bool
    z: bool
    p: bool
    label: str 

@dataclass(frozen=True)
class LabelJsr:
    pc_offset: ElevenBitSigned

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


