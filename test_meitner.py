from pathlib import Path

import pytest

from meitner.cli import main
from meitner.tokenizer import tokenize

PROGRAMS = Path(__file__).parent / "programs"


def run_source(tmp_path, capsys, source):
    f = tmp_path / "t.meit"
    f.write_text(source, encoding="utf-8")
    code = main([str(f)])
    out = capsys.readouterr()
    return code, out.out, out.err


def test_hello_file(capsys):
    assert main([str(PROGRAMS / "hello.meit")]) == 0
    assert capsys.readouterr().out == "hello\n"


def test_tokenizer_nested_blocks():
    assert tokenize("if true { if true { print 1 } }") == [
        "if", "true", ["if", "true", ["print", "1"]]
    ]


def test_variables_and_arithmetic(tmp_path, capsys):
    code, out, _ = run_source(tmp_path, capsys, """
setvar [ n ] 10
addvar [ n ] 5
multvar [ n ] 2
subvar [ n ] 6
print [ n ]
""")
    assert code == 0 and out == "24\n"


def test_divvar_is_integer_division(tmp_path, capsys):
    code, out, _ = run_source(tmp_path, capsys, "setvar [ n ] 10\ndivvar [ n ] 4\nprint [ n ]")
    assert code == 0 and out == "2\n"


def test_else_and_variable_condition(tmp_path, capsys):
    code, out, _ = run_source(tmp_path, capsys, """
setvar [ flag ] false
if [ flag ] { print "a" } else { print "b" }
""")
    assert code == 0 and out == "b\n"


def test_nested_if_inside_else(tmp_path, capsys):
    code, out, _ = run_source(tmp_path, capsys, """
if 1 = 2 { print "x" }
else { if 2 = 2 { print "else-if" } }
""")
    assert code == 0 and out == "else-if\n"


def test_loop_count_and_zero(tmp_path, capsys):
    code, out, _ = run_source(tmp_path, capsys, """
setvar [ i ] 0
loop 3 { addvar [ i ] 1 }
loop 0 { print "never" }
print [ i ]
""")
    assert code == 0 and out == "3\n"


def test_true_is_not_one(tmp_path, capsys):
    code, out, _ = run_source(tmp_path, capsys, "if true = 1 { print \"bad\" } else { print \"ok\" }")
    assert code == 0 and out == "ok\n"


@pytest.mark.parametrize("source,message", [
    ("print [ nope ]", "Undefined variable"),
    ("setvar [ b ] true\naddvar [ b ] 1", "boolean"),
    ("setvar [ n ] 1\ndivvar [ n ] 0", "divide by zero"),
    ("print \"unterminated", "Unterminated"),
    ("}", "Unexpected '}'"),
    ("bogus", "Unknown command"),
])
def test_errors_exit_nonzero(tmp_path, capsys, source, message):
    code, _, err = run_source(tmp_path, capsys, source)
    assert code == 1 and message in err


def test_missing_file(capsys):
    assert main(["does_not_exist.meit"]) == 1
    assert "File not found" in capsys.readouterr().err
