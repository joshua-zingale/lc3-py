from dataclasses import dataclass
import enum
import typing as t


from lc3_py.type_additions import iserr, Err
from lc3_py import parsing

from . import lexer
from . import n_bit_number
from . import instructions
from . import directives

class StatementWithLabel:
    labels: list[str]
    statement: instructions.InstructionWithLabel | instructions.InstructionWithoutPcOffset | directives.Fill | directives.Blkw | directives.Stringz

@dataclass(frozen=True)
class CodeBlockWithLabels:
    origin: n_bit_number.SixteenBitNumber
    



def _parse_lc3_from_matches(lexeme_matches: t.Sequence[parsing.Match[lexer.Lexeme, parsing.Span]]):

    lexemes = list(map(lambda l: l.lexeme, lexeme_matches))

    
def parse_lcr_from_lexemes(lexemes: list[lexer.Lexeme]):
    return parsing.parse

def parse_lcr(source: str):
    lexeme_matches = lexer.lex_lc3(source)
    if iserr(lexeme_matches):
        return lexeme_matches
    
    matches = _parse_lc3_from_matches(lexeme_matches)
    if iserr(matches):
        return matches
    return matches
    
