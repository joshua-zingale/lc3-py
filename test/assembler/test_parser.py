from lc3_py.assembler.parser import *
from lc3_py.assembler.instructions import Add, LabelBr, Register, Label
from lc3_py.type_additions import iserr


def test_add():
    res = add.parse("add r0 r1 r7")
    assert not iserr(res), res
    print(res)


# def test_add():
#     matches = parse_lc3("""add r1, r1, r1""")
#     assert not iserr(matches)
#     assert len(matches) == 1
#     assert matches[0].lexeme == Add(Register("r1"), Register("r1"), Register("r1"))
#     assert matches[0].span.start == 0
#     assert matches[0].span.end == 4 

# def test_labelbr():
#     matches = parse_lc3("""brnp location""")
#     assert not iserr(matches)
#     assert len(matches) == 1
#     assert matches[0].lexeme == LabelBr(True, False, True, Label("location"))
#     assert matches[0].span.start == 0
#     assert matches[0].span.end == 2


# def test_add_and_label_labelbr():
#     matches = parse_lc3("""
# add r1, r1, r1
# brz label
# and r1 r2 #13""")
#     assert not iserr(matches)
#     assert len(matches) == 3