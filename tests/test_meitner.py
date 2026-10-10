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

@pytest.mark.parametrize("source, expected", [
    # Empty and ordinary values
    ('print ""', "\n"),
    ('print 0', "0\n"),
    ('print -7', "-7\n"),
    ('print true\nprint false', "true\nfalse\n"),

    # Variable copying and reassignment
    (
        'setvar [ a ] 5\n'
        'setvar [ b ] [ a ]\n'
        'print [ b ]',
        "5\n",
    ),
    (
        'setvar [ x ] 3\n'
        'setvar [ x ] 9\n'
        'print [ x ]',
        "9\n",
    ),

    # Negative arithmetic and floor division
    (
        'setvar [ n ] 5\n'
        'subvar [ n ] 8\n'
        'print [ n ]',
        "-3\n",
    ),
    (
        'setvar [ n ] -7\n'
        'divvar [ n ] 2\n'
        'print [ n ]',
        "-4\n",
    ),

    # Conditional branches
    (
        'if 3 > 2 { print "yes" } '
        'else { print "no" }',
        "yes\n",
    ),
    (
        'if 3 < 2 { print "yes" } '
        'else { print "no" }',
        "no\n",
    ),

    # Equality must respect value types
    (
        'if "5" = 5 { print "equal" } '
        'else { print "different" }',
        "different\n",
    ),

    # Variables holding booleans
    (
        'setvar [ ok ] true\n'
        'if [ ok ] { print "yes" }',
        "yes\n",
    ),

    # Zero and negative loop counts
    (
        'loop 0 { print "bad" }\n'
        'loop -2 { print "bad" }\n'
        'print "done"',
        "done\n",
    ),

    # Nested loops
    (
        'loop 2 { loop 3 { print "x" } }',
        "x\n" * 6,
    ),
])
def test_valid_edge_cases(tmp_path, capsys, source, expected):
    code, stdout, stderr = run_source(
        tmp_path, capsys, source
    )

    assert code == 0, stderr
    assert stdout == expected
    assert stderr == ""

@pytest.mark.parametrize("source, expected_error", [
    # Missing operands
    (
        "print",
        "expected a value",
    ),
    (
        "setvar [ x ]",
        "expected a value",
    ),

    # Malformed variable references
    (
        "print [ x",
        "Expected a variable",
    ),
    (
        "setvar x 5",
        "Expected a variable",
    ),

    # Invalid arithmetic
    (
        "setvar [ x ] nope\naddvar [ x ] 1",
        "Expected a number",
    ),
    (
        "setvar [ x ] 2\ndivvar [ x ] 0",
        "divide by zero",
    ),

    # Invalid condition
    (
        "if 1 { print 1 }",
        "needs true/false",
    ),

    # Invalid loops
    (
        'loop false { print "bad" }',
        "loop needs a number",
    ),
    (
        "loop 2",
        "must be followed",
    ),

    # Unclosed block
    (
        "if true { print 3",
        "Unterminated",
    ),

    # Unknown command
    (
        "not_a_command",
        "Unknown command",
    ),
])
def test_invalid_programs(
    tmp_path, capsys, source, expected_error
):
    code, stdout, stderr = run_source(
        tmp_path, capsys, source
    )

    assert code == 1
    assert expected_error in stderr

@pytest.mark.xfail(
    strict=True,
    reason="Tokenizer does not recognize attached comments"
)
def test_comment_without_space(tmp_path, capsys):
    source = 'print 5//comment'

    code, stdout, stderr = run_source(
        tmp_path, capsys, source
    )

    assert code == 0
    assert stdout == "5\n"
    assert stderr == ""
