from lc3_py.parsing import string, regex, Token, Span, combinator, AdvancingSequence
from lc3_py.type_additions import iserr


def test_string():
    assert string("bob").parse_many("bobbob") == ["bob", "bob"]
    assert iserr(string("bob").parse_many("bob bob"))
    assert iserr(string("bob").parse("bob bob"))
    assert string("yghuijfs324").parse("yghuijfs324") == "yghuijfs324"


def test_regex():
    assert regex(r"\w+ \d.\d\d").parse("abcdefg 3.14") == "abcdefg 3.14"
    assert regex(r"\w\d").parse_many("a1b2") == ["a1", "b2"]

def test_otherwise():
    assert (regex(r"\d.\d\d") | string("bob")).parse("3.14") == "3.14"
    assert (regex(r"\d.\d\d") | string("bob")).parse("bob") == "bob"
    assert iserr((regex(r"\d.\d\d") | string("bob")).parse("3.145"))

def test_postskip():
    assert iserr(regex(r"d.\d\d").parse("3.14    "))
    assert regex(r"\d.\d\d").postskip(regex(r"\s+")).parse("3.14   ") == "3.14"
    assert regex(r"\w\d").postskip(string("\n")).parse_many("a1\nb2") == ["a1", "b2"]
def test_preskip():
    assert iserr(regex(r"d.\d\d").parse("    3.14"))
    assert regex(r"\d.\d\d").preskip(regex(r"\s+")).parse("     3.14") == "3.14"

def test_as_token():
    string = "hello good\n   friend  "
    result = regex(r"\w+").as_token().postskip(regex(r"[\s\n\r]+")).parse_many(string)
    assert not iserr(result)
    assert result == [
        Token("hello", Span(0,5)),
        Token("good", Span(6,10)),
        Token("friend", Span(string.find("friend"),string.find("friend") + len("friend")))]

def test_as_token_with_postskip_first():
    string = "hello good\n   friend  "
    result = regex(r"\w+").postskip(regex(r"[\s\n\r]+")).as_token().parse_many(string)
    assert not iserr(result)
    assert result == [
        Token("hello", Span(0,6)),
        Token("good", Span(6,string.find("friend"))),
        Token("friend", Span(string.find("friend"), len(string)))]

def test_then():
    @combinator
    def number(seq: AdvancingSequence[int]):
        return seq.advance(1), seq[0]
    
    assert number.parse([1]) == 1
    assert number.then(number).parse([1,2]) == 3

    comb = regex(r"^\d+") + string(".")
    assert comb.parse("123.") == "123."
    assert iserr(comb.parse("123"))
    comb = comb + regex(r"^\d+")
    assert comb.parse("123.8") == "123.8"
    assert iserr(comb.parse("123. 8"))