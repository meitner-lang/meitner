"""Confirmed defects found by the repository audit."""

import subprocess
import sys
import random

import pytest

from meitner.runner import run
from meitner.tokenizer import tokenize


def test_attached_comment_ends_word(capsys):
    run(tokenize("print 5//comment\nprint 6"), {})
    assert capsys.readouterr().out == "5\n6\n"


@pytest.mark.parametrize("separator", ["\r\n", "\r", "\u2028"])
def test_line_positions_follow_supported_line_separators(separator):
    tokens = tokenize("print 1" + separator + "print 2")
    assert (tokens[2].line, tokens[2].column) == (2, 1)


@pytest.mark.parametrize("separator", ["\n", "\r\n", "\r", "\u2028"])
def test_line_comment_ends_at_line_separator(separator):
    tokens = tokenize("// note" + separator + "print 1")
    assert [token.value for token in tokens] == ["print", "1"]


def test_quoted_forever_is_not_an_infinite_loop(tmp_path):
    # A subprocess bounds the old behavior, which otherwise loops forever.
    program = tmp_path / "quoted-forever.meit"
    program.write_text('loop "forever" { }', encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "meitner", str(program)],
                            capture_output=True, text=True, timeout=2)
    assert result.returncode == 1
    assert "loop needs a number" in result.stderr
    assert "Traceback" not in result.stderr


def test_deeply_nested_blocks_fail_cleanly():
    source = "if true {" * 1100 + "print 1" + "}" * 1100
    with pytest.raises(SyntaxError, match="nesting"):
        tokenize(source)


def test_maximum_supported_nesting_executes(capsys):
    source = "if true {" * 128 + "print 1" + "}" * 128
    run(tokenize(source), {})
    assert capsys.readouterr().out == "1\n"


def test_oversized_numeric_literal_is_not_silently_text(capsys):
    with pytest.raises(SyntaxError, match="Integer"):
        run(tokenize("print " + "9" * 4301), {})
    assert capsys.readouterr().out == ""


def test_largest_supported_numeric_literal_is_an_integer():
    variables = {}
    run(tokenize("setvar [ n ] " + "9" * 4300), variables)
    assert isinstance(variables["n"], int)


def test_oversized_arithmetic_does_not_leak_python_error():
    number = "9" * 3000
    with pytest.raises(TypeError, match="Integer"):
        run(tokenize(f"setvar [ n ] {number} multvar [ n ] [ n ]"), {})


def test_invalid_command_in_skipped_block_is_rejected():
    with pytest.raises(SyntaxError, match="Unknown command"):
        run(tokenize("if false { bogus } print 1"), {})


@pytest.mark.parametrize("source", ["{}", "if false { {} }"])
def test_bare_block_is_syntax_error(source):
    with pytest.raises(SyntaxError, match="Unexpected"):
        run(tokenize(source), {})


def test_variable_text_forever_is_not_an_infinite_loop():
    with pytest.raises(SyntaxError, match="loop needs a number"):
        run(tokenize('setvar [ n ] "forever" loop [ n ] { }'), {})


def test_small_integer_arithmetic_matches_python(capsys):
    rng = random.Random(8741)
    operations = {
        "addvar": lambda a, b: a + b,
        "subvar": lambda a, b: a - b,
        "multvar": lambda a, b: a * b,
        "divvar": lambda a, b: a // b,
    }
    nonzero_operands = [n for n in range(-10, 11) if n]
    commands = list(operations)
    for _ in range(100):
        left = rng.randint(-1000, 1000)
        right = rng.choice(nonzero_operands)
        command = rng.choice(commands)
        run(tokenize(f"setvar [ n ] {left} {command} [ n ] {right} print [ n ]"), {})
        assert capsys.readouterr().out == f"{operations[command](left, right)}\n"
