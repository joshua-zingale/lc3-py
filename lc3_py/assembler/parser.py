import typing as t
from lc3_py import parsing as p

from . import n_bit_number
from . import instructions as inst
from . import directives

ParseTokens: t.TypeAlias = inst.InstructionWithLabel | inst.InstructionWithoutPcOffset | directives.Fill | directives.Blkw | directives.Stringz


def string(string: str):
    return p.regex("^" + "".join(map(lambda x: f"[{x.lower()}{x.upper()}]", string)))

space = p.regex("^[ \t]")

register = p.regex(r"^[rR][0-7]").map(inst.Register)
immediate = p.regex_groups(r"#(-?\d+)").map(lambda x: int(x[0])) |  p.regex_groups(r"x(-?\d+)").map(lambda x: int(x[0], 16))

add = (string("add")
       .consume(space)
       .cons(register)
       .consume(space)
       .append(register)
       .consume(space)
       .append(register)
       .map(lambda x: inst.Add(*x[1:])))

add = (string("add")
       .consume(space)
       .cons(register)
       .consume(space)
       .append(register)
       .consume(space)
       .append(immediate.map(n_bit_number.FiveBitSigned.new))
       .map(lambda x: inst.AddIm(*x[1:])))

# and_ = string("and")
# br = p.regex("^[bB][rR][nN]?[zZ]?[pP]?")
# jmp = string("jmp")
# jsr = string("jsr")
# jsrr = string("jsrr")
# ld = string("ld")
# ldi = string("ldi")
# ldr = string("ldr")
# lea = string("lea")
# not_ = string("not")
# ret = string("ret")
# rti = string("rti")
# st = string("st")
# sti = string("sti")
# str_ = 
# trap = string("str")
