from lc3_py import parsing as p
from lc3_py.type_additions import iserr
import operator as op

def test_string():
    assert p.string("bob").parse_many("bobbob") == ["bob", "bob"]
    assert iserr(p.string("bob").parse_many("bob bob"))
    assert iserr(p.string("bob").parse("bob bob"))
    assert p.string("yghuijfs324").parse("yghuijfs324") == "yghuijfs324"


def test_regex():
    assert p.regex(r"\w+ \d.\d\d").parse("abcdefg 3.14") == "abcdefg 3.14"
    assert p.regex(r"\w\d").parse_many("a1b2") == ["a1", "b2"]

def test_otherwise():
    assert (p.regex(r"\d.\d\d") | p.string("bob")).parse("3.14") == "3.14"
    assert (p.regex(r"\d.\d\d") | p.string("bob")).parse("bob") == "bob"
    assert iserr((p.regex(r"\d.\d\d") | p.string("bob")).parse("3.145"))

def test_postskip():
    assert iserr(p.regex(r"d.\d\d").parse("3.14    "))
    assert p.regex(r"\d.\d\d").postskip(p.regex(r"\s+")).parse("3.14   ") == "3.14"
    assert p.regex(r"\w\d").postskip(p.string("\n")).parse_many("a1\nb2") == ["a1", "b2"]
def test_preskip():
    assert iserr(p.regex(r"d.\d\d").parse("    3.14"))
    assert p.regex(r"\d.\d\d").preskip(p.regex(r"\s+")).parse("     3.14") == "3.14"

def test_as_token():
    string = "hello good\n   friend  "
    result = p.regex(r"\w+").as_token().postskip(p.regex(r"[\s\n\r]+")).parse_many(string)
    assert not iserr(result)
    assert result == [
        p.Token("hello", p.Span(0,5)),
        p.Token("good", p.Span(6,10)),
        p.Token("friend", p.Span(string.find("friend"),string.find("friend") + len("friend")))]

def test_as_token_with_postskip_first():
    string = "hello good\n   friend  "
    result = p.regex(r"\w+").postskip(p.regex(r"[\s\n\r]+")).as_token().parse_many(string)
    assert not iserr(result)
    assert result == [
        p.Token("hello", p.Span(0,6)),
        p.Token("good", p.Span(6, string.find("friend"))),
        p.Token("friend", p.Span(string.find("friend"), len(string)))]

def test_then():
    @p.combinator
    def number(seq: p.AdvancingSequence[int]):
        return seq.advance(1), seq[0]
    
    assert number.parse([1]) == 1
    assert number.then(number).parse([1,2]) == 3

    comb = p.regex(r"^\d+") + p.string(".")
    assert comb.parse("123.") == "123."
    assert iserr(comb.parse("123"))
    comb = comb + p.regex(r"^\d+")
    assert comb.parse("123.8") == "123.8"
    assert iserr(comb.parse("123. 8"))

def test_cons():
    comb = p.string("d").cons(p.regex(r"\d+").map(int))
    assert comb.parse("d198") == ("d", 198)
    assert iserr(comb.parse("dd"))
    assert iserr(comb.parse("198"))

def test_append():
    comb = p.string("d").cons(p.regex(r"\d+").map(int)).append(p.string("d"))
    assert comb.parse("d654d") == ("d", 654, "d")
    assert iserr(comb.parse("d"))
    assert iserr(comb.parse("198"))
    assert iserr(comb.parse("d198"))
    assert iserr(comb.parse("198"))

def test_expression():
    space = p.regex(r"^\s*")
    expr = p.forward(str, float, "Expression")
    term = p.forward(str, float, "Term")
    fac = p.forward(str, float, "Factor")
    num = p.regex(r"^(\d*\.)?\d+").map(float)

    expr.define(
        term.postskip(space)
        .cons(p.string("+").map(lambda x: op.add) | p.string("-").map(lambda x: op.sub))
        .postskip(space)
        .append(expr)
        .map(lambda x: x[1](x[0],x[2]))
        | term
    )
    term.define(
        fac.postskip(space)
        .cons(p.string("*").map(lambda x: op.mul) | p.string("/").map(lambda x: op.truediv))
        .postskip(space)
        .append(term)
        .map(lambda x: x[1](x[0],x[2]))
        | fac
        )
    fac.define(
        p.string("(")
        .postskip(space)
        .cons(expr)
        .postskip(space)
        .consume(p.string(")"))
        .map(lambda x: x[1])
        | num
    )
    assert num.parse("12") == 12
    assert expr.parse("12") == 12
    assert expr.parse("12 +8/2") == 16




    
