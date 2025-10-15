from dataclasses import dataclass
import enum
import typing as t

from lc3_py.type_additions import Err
from lc3_py.assembler.n_bit_number import FiveBitSigned, SixBitSigned, EightBitSigned, NineBitSigned, ElevenBitSigned

class Register(enum.StrEnum):
    R0 = "r0"
    R1 = "r1"
    R2 = "r2"
    R3 = "r3"
    R4 = "r4"
    R5 = "r5"
    R6 = "r6"
    R7 = "r7"

    @staticmethod
    def new(register_name: str) -> Register | Err:

        try:
            return Register(register_name)
        except ValueError:
            return Err(f"'{register_name}' is not a valid register.")

        

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
class Label:
    value: str

    @staticmethod
    def new(value: str) -> Label | Err:
        if any([v.isspace() for v in value]):
            return Err("a label cannot contain whitespace")
        
        if value.lower() in ["add", "and", "br", "jmp", "jsr", "jsrr", "ld", "ldi", "ldr", "lea", "not", "ret", "rti", "sti", "str", "trap", "puts", "out"]:
            return Err(f"'{value}' is not a valid label name because it is also an instruction name")
        return Label(value)
    
    def __eq__(self, other: t.Any):
        return isinstance(other, Label) and self.value.lower() == other.value.lower()
    def __hash__(self):
        return hash(self.value.lower())

@dataclass(frozen=True)
class LabelBr:
    n: bool
    z: bool
    p: bool
    label: Label 

@dataclass(frozen=True)
class LabelJsr:
    label: Label

@dataclass(frozen=True)
class LabelLd:
    destination: Register
    label: Label

@dataclass(frozen=True)
class LabelLdi:
    destination: Register
    label: Label

@dataclass(frozen=True)
class LabelLea:
    destination: Register
    label: Label

@dataclass(frozen=True)
class LabelSt:
    source: Register
    label: Label

@dataclass(frozen=True)
class LabelSti:
    source: Register
    label: Label



InstructionWithoutPcOffset: t.TypeAlias = Add | AddIm | And | AndIm | Jmp | Jsrr | Ldr | Not | Ret | Rti | Str | Trap
InstructionWithPcOffset: t.TypeAlias =  Br | Jsr | Ld | Ldi | Lea | St | Sti
Instruction: t.TypeAlias = InstructionWithoutPcOffset | InstructionWithPcOffset
InstructionWithLabel: t.TypeAlias = LabelBr | LabelJsr | LabelLd | LabelLdi | LabelLea | LabelSt | LabelSti | Label


