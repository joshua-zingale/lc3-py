from lc3_py.parsing import string, regex
from lc3_py.type_additions import iserr


def test_string():
    assert string("bob").parse_many("bobbob") == ["bob", "bob"]
    assert iserr(string("bob").parse_many("bob bob"))
    assert iserr(string("bob").parse("bob bob"))
    assert string("yghuijfs324").parse("yghuijfs324") == "yghuijfs324"


def test_regex():
    assert regex(r"\w+ \d.\d\d").parse("abcdefg 3.14") == "abcdefg 3.14"

def test_or():
    assert (regex(r"\d.\d\d") | string("bob")).parse("3.14") == "3.14"
    assert (regex(r"\d.\d\d") | string("bob")).parse("bob") == "bob"
    assert iserr((regex(r"\d.\d\d") | string("bob")).parse("3.145"))

def test_postskip():
    assert iserr(regex(r"d.\d\d").parse("3.14    "))
    assert regex(r"\d.\d\d").postskip(regex(r"\s+")).parse("3.14   ") == "3.14"

def test_preskip():
    assert iserr(regex(r"d.\d\d").parse("    3.14"))
    assert regex(r"\d.\d\d").preskip(regex(r"\s+")).parse("     3.14") == "3.14"