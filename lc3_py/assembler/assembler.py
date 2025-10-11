from dataclasses import dataclass
import enum
from system_constants import MIN_ADDRESS, MIN_USER_ADDRESS, MAX_ADDRESS
import typing as t

from lc3_py.type_additions import Result, Err, ErrList


class Address:

    def __init__(self, address: int):
        if not (MIN_ADDRESS < address < MAX_ADDRESS):
            raise ValueError(f"Invalid address x{address:X}")
        self._address = address

    @staticmethod
    def system(address: int) -> Result[Address, AddressErr]:
        if MIN_ADDRESS <= address <= MAX_ADDRESS:
            return Address(address)
        return AddressErr("invalid address", address, MIN_ADDRESS, MAX_ADDRESS)
        
    @staticmethod
    def user(address: int) -> Result[Address, Err]:
        if MIN_ADDRESS <= address < MIN_USER_ADDRESS:
                return AddressErr("invalid address for user program", address, MIN_USER_ADDRESS, MAX_ADDRESS)
        if  MIN_USER_ADDRESS <= address <= MAX_ADDRESS:
                return Address(address)
        return Err(f"invalid address: x{address:X}")
        
    @property
    def value(self) -> int:
        return self._address

class SymbolTable():
    def __init__(self):
        self._dict: dict[Label, Address] = dict()
    def add(self, label: Label, address: Address) -> Result[None, Err]:
        if label in self._dict:
            return Err(f"label '{label.value}' has been defined twice")
        self._dict[label] = address
    def get_value(self, label: Label) -> Result[Address, Err]:
        return self._dict.get(label, Err(f"undefined label '{label.value}'"))

class Label:
    def __init__(self, label: str):
        self._label = label

    @property
    def value(self) -> str:
        return self._label
    
    @staticmethod
    def new(label: str) -> Result[Label, Err]:
        if len(label) == 0:
            return Err("label must not have an empty name")
        if label[0].isdigit():
            return Err("label cannot begin with a digit")
        if any([c.isspace() for c in label]):
            return Err("label cannot contain space")
        
        return Label(label)
    
    def __eq__(self, other: t.Any) -> bool:
        return isinstance(other, Label) and self.value == other.value
    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return f"Label({self._label})"
    def __repr__(self):
        return str(self)

class RegisterName(enum.StrEnum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"
    R6 = "R6"
    R7 = "R7"

@dataclass(frozen=True)
class Lea:
    dest: RegisterName
    address: Address

@dataclass(frozen=True)
class Halt:
    address: Address
    
@dataclass(frozen=True)
class StringZ:
    string: str
    address: Address

Instruction: t.TypeAlias = Lea | Halt
Directive: t.TypeAlias = StringZ
Statement: t.TypeAlias = Instruction | Directive
     


def pre_assemble(source: str) -> Result[tuple[list[Statement], SymbolTable], ErrList]: ...
"""Returns a list of instructions rom assembly"""

def assemble(source: str) -> Result[bytes, ErrList]: ...


class AddressErr(Err):
    def __init__(self, message: str, address: int, minimum: int, maximum: int):
        super().__init__(f"{message}: x{address:X}: must be between x{minimum:X} and x{maximum:X}")




    
