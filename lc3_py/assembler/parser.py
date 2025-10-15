import typing as t

from lc3_py.type_additions import iserr, Err, has_no_err
from lc3_py import lexing

from . import lexer
from . import n_bit_number
from . import instructions
from . import directives

class StatementWithLabel:
    labels: list[str]
    statement: instructions.InstructionWithLabel | instructions.InstructionWithoutPcOffset | directives.Fill | directives.Blkw | directives.Stringz

ParseTokens: t.TypeAlias = instructions.InstructionWithLabel | instructions.InstructionWithoutPcOffset | directives.Fill | directives.Blkw | directives.Stringz

@t.overload
def match[T](lexemes: t.Sequence[t.Any], l1: t.Type[T], /) -> t.TypeGuard[tuple[T]]: ...
@t.overload
def match[T1, T2](lexemes: t.Sequence[t.Any], l1: t.Type[T1], l2: t.Type[T2], /) -> t.TypeGuard[tuple[T1, T2]]: ...
@t.overload
def match[T1, T2, T3](lexemes: t.Sequence[t.Any], l1: t.Type[T1], l2: t.Type[T2], l3: t.Type[T3], /) -> t.TypeGuard[tuple[T1, T2, T3]]: ...
@t.overload
def match[T1, T2, T3, T4](lexemes: t.Sequence[t.Any], l1: t.Type[T1], l2: t.Type[T2], l3: t.Type[T3], l4: t.Type[T4], /) -> t.TypeGuard[tuple[T1, T2, T3, T4]]: ...
def match(lexemes: t.Sequence[t.Any], /, *args: t.Type[t.Any]) -> bool:
    if len(lexemes) < len(args):
        return False
    for lexeme, wanted_type in zip(lexemes, args):
        if not isinstance(lexeme, wanted_type):
            return False
    return True


def cut_beginning(f: t.Callable[[t.Sequence[lexer.Lexeme]], t.Optional[tuple[ParseTokens | Err, int]]]) -> t.Callable[[t.Sequence[lexer.Lexeme], int], t.Optional[lexing.Match[ParseTokens] | lexing.ErrMatch]]:
    def wrapped(seq: t.Sequence[lexer.Lexeme], pos: int) -> t.Optional[lexing.Match[ParseTokens] | lexing.ErrMatch]:
        r = f(seq)
        if r is None:
            return None
        obj, length = r
        span = lexing.Span(pos, pos + length)
        if iserr(obj):
            return lexing.ErrMatch(obj.error, span)
        return lexing.Match(obj, span)
    return wrapped

def begins(word_value: str):
    def wrapper(f: t.Callable[[t.Sequence[lexer.Lexeme]], tuple[ParseTokens | Err, int]]) -> t.Callable[[t.Sequence[lexer.Lexeme]], t.Optional[tuple[ParseTokens | Err, int]]]:
        def wrapped(seq: t.Sequence[lexer.Lexeme]):
            if len(seq) > 0 and isinstance(seq[0], lexer.Word) and seq[0].value.lower() == word_value.lower():
                obj, length = f(seq[1:])
                if iserr(obj):
                    return Err(f"invalid '{word_value}': {obj.error}"), length + 1
                return obj, length + 1
            return None
        return wrapped
    return wrapper


def ends_with_newline(f: t.Callable[[t.Sequence[lexer.Lexeme]], tuple[ParseTokens | Err, int]]) -> t.Callable[[t.Sequence[lexer.Lexeme]], tuple[ParseTokens | Err, int]]:
    def wrapped(seq: t.Sequence[lexer.Lexeme]):
        obj, length = f(seq)
        if iserr(obj):
            return obj, length
        if len(seq) > length and not isinstance(seq[length], lexer.Newline):
            return Err("expected newline after statement"), length
        elif len(seq) > length and isinstance(seq[length], lexer.Newline):
            return obj, length + 1
        return obj, length
    return wrapped


@cut_beginning
@begins("add")
@ends_with_newline
def parse_add(args: t.Sequence[lexer.Lexeme]):
    if match(args, lexer.Word, lexer.Word, lexer.Word):
        registers = instructions.Register.new(args[0].value), instructions.Register.new(args[1].value), instructions.Register.new(args[2].value)
        if has_no_err(registers):
            return instructions.Add(*registers), 3
        return Err("expected three registers following an ADD instructions"), 3
    if match(args, lexer.Word, lexer.Word, lexer.Integer):
        registers = instructions.Register.new(args[0].value), instructions.Register.new(args[1].value)
        if has_no_err(registers):
            immediate = n_bit_number.FiveBitSigned.new(args[2].value)
            if iserr(immediate):
                return immediate, 3
            return instructions.AddIm(*registers, immediate), 3
    return Err("expected either two registers and an integer immediate or three registers following an ADD instruction."), 0


@cut_beginning
@begins("and")
@ends_with_newline
def parse_and(args: t.Sequence[lexer.Lexeme]):
    if match(args, lexer.Word, lexer.Word, lexer.Word):
        registers = instructions.Register.new(args[0].value), instructions.Register.new(args[1].value), instructions.Register.new(args[2].value)
        if has_no_err(registers):
            return instructions.And(*registers), 3
        return Err("expected three registers following an AND instructions"), 3
    if match(args, lexer.Word, lexer.Word, lexer.Integer):
        registers = instructions.Register.new(args[0].value), instructions.Register.new(args[1].value)
        if has_no_err(registers):
            immediate = n_bit_number.FiveBitSigned.new(args[2].value)
            if iserr(immediate):
                return immediate, 3
            return instructions.AndIm(*registers, immediate), 3
    return Err("expected either two registers and an integer immediate or three registers following an AND instruction."), 0

@cut_beginning
def parse_br_or_label(lexemes: t.Sequence[lexer.Lexeme]):
    if len(lexemes) > 0 and isinstance(lexemes[0], lexer.Word) and lexemes[0].value[:2].lower() == "br":
        instruction = lexemes[0].value
        flag_char = 2
        n, z, p = False, False, False
        if len(instruction) > flag_char and instruction[flag_char] == "n":
            n = True
            flag_char += 1
        if len(instruction) > flag_char and instruction[flag_char] == "z":
            z = True
            flag_char += 1
        if len(instruction) > flag_char and instruction[flag_char] == "p":
            p = True
            flag_char += 1
        if len(instruction) > flag_char:
            return instructions.Label(instruction), 1
        args = lexemes[1:]
        if match(args, lexer.Word):
            label = instructions.Label.new(args[0].value)
            if iserr(label):
                return label, 2
            if len(lexemes) > 2 and not isinstance(lexemes[3], lexer.Newline):
                return Err("expected newline after statement"), 2
            return instructions.LabelBr(n,z,p, label), 2
    return None

@cut_beginning
@begins("jmp")
@ends_with_newline
def parse_jmp(args: t.Sequence[lexer.Lexeme]):
    if match(args, lexer.Word):
        register = instructions.Register.new(args[0].value)
        if iserr(register):
            return register, 1
        return instructions.Jmp(register), 1
    return Err("expected a register following a JMP instruction"), 0


parsing_functions = [
    parse_add,
    parse_and,
    parse_br_or_label,
    parse_jmp,
]

def skip_function(seq: t.Sequence[lexer.Lexeme], pos: int) -> int:
    while len(seq) > pos and isinstance(seq[pos], lexer.Newline):
        pos += 1
    return pos

def parse_lc3(source: str):
    lexeme_matches = lexer.lex_lc3(source)
    if iserr(lexeme_matches):
        return lexeme_matches
    
    lexemes = list(map(lambda l: l.lexeme, lexeme_matches))
    matches = lexing.lex(lexemes, parsing_functions, skip_function)
    if iserr(matches):
        return matches
    return matches
    
