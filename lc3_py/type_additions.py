import typing as t

_T = t.TypeVar("_T")
_E = t.TypeVar("_E", bound="Err")

Result: t.TypeAlias = t.Union[_T, _E]

def iserr(res: t.Any) -> t.TypeIs[Err]:
    if isinstance(res, Err):
        return True
    return False

def expect(res: Result[_T, _E], reason: t.Optional[str] = None) -> _T:
    """Casts a Result to the non-:class:`Err` value.
    
    :throws ExpectationError: If the result is an object that inherits form :class:`Err`.
    """
    if iserr(res):
        raise ExpectationError(res, reason)
    return res

class ExpectationError(ValueError):
    def __init__(self, err: Err, reason: t.Optional[str] = None):
        if reason is None:
            super().__init__(f"Expectation violated: found {type(err).__name__}: {err.error}")
        else:
            super().__init__(f"Expectation violated: {reason}: found {type(err).__name__}: {err.error}")

class Err:
    def __init__(self, error: str):
        self._error = error
    @property
    def error(self) -> str:
        return self._error
    
    def __str__(self) -> str:
        return self.error
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

class ErrList(list[Err], Err):
    def __init__(self, error: str):
        super().__init__()
        self._error = error

    @property
    def error(self) -> str:
        return self._error

    def __str__(self) -> str:
        return f"[{", ".join(map(repr, self))}]"
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(error={self.error}, {self})"


class UnreachableError(RuntimeError): ...