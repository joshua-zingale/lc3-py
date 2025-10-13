import typing as t

from lc3_py.type_additions import Err

class FiveBitSigned(int):
    @staticmethod
    def new(value: int) -> FiveBitSigned | Err:
        return _construct_n_bit_signed(FiveBitSigned, value, 5)
    
class SixBitSigned(int):
    @staticmethod
    def new(value: int) -> SixBitSigned | Err:
        return _construct_n_bit_signed(SixBitSigned, value, 6)
    
class EightBitSigned(int):
    @staticmethod
    def new(value: int) -> EightBitSigned | Err:
        return _construct_n_bit_signed(EightBitSigned, value, 8)

class NineBitSigned(int):
    @staticmethod
    def new(value: int) -> NineBitSigned | Err:
        return _construct_n_bit_signed(NineBitSigned, value, 9)
    
class ElevenBitSigned(int):
    @staticmethod
    def new(value: int) -> ElevenBitSigned | Err:
        return _construct_n_bit_signed(ElevenBitSigned, value, 11)
    

class SixteenBitNumber(int):
    @staticmethod
    def new(value: int) -> SixteenBitNumber | Err:
        return _construct_n_bit_signed(SixteenBitNumber, value, 16)


    

def _construct_n_bit_signed[T](constructor: t.Callable[[int], T], value: int, bits: int) -> T | Err:
    if value >= 2**(bits-1) or value < 2**(bits-1):
        return Err(f"the number '{value}' (base 10) can not be fit into {bits} bits as a signed integer.")
    return constructor(value)


def _construct_n_bit_signed_overflow_okay[T](constructor: t.Callable[[int], T], value: int, bits: int) -> T | Err:
    if value >= 2**(bits) or value < 2**(bits-1):
        return Err(f"the number '{value}' (base 10) can not be fit into {bits} bits.")
    return constructor(value)
