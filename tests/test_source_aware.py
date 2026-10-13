"""Tokenizer and interpreter regressions for supported Meitner syntax."""

import pytest

from meitner.cli import main
from meitner.runner import compare, run
from meitner.tokenizer import Block, Token, tokenize


def flatten(tokens):
    for token in tokens:
        if isinstance(token, list):
            yield from flatten(token)
        else:
            yield token


@pytest.mark.parametrize("source", ["", " \t\n\n  "])
def test_empty_and_whitespace_sources(source):
    assert tokenize(source) == []


def test_ordinary_token_kinds_values_and_positions():
    tokens = tokenize("\tsetvar [ x ] 12\n\n  print [ x ]")
    assert [(t.kind, t.value, t.line, t.column) for t in tokens] == [
        ("WORD", "setvar", 1, 2),
        ("SYMBOL", "[", 1, 9),
        ("WORD", "x", 1, 11),
        ("SYMBOL", "]", 1, 13),
        ("WORD", "12", 1, 15),
        ("WORD", "print", 3, 3),
        ("SYMBOL", "[", 3, 9),
        ("WORD", "x", 3, 11),
        ("SYMBOL", "]", 3, 13),
    ]


@pytest.mark.parametrize("source, expected", [
    ('print "two words"', [("SYMBOL", '"', 1, 7),
                          ("STRING", "two words", 1, 8),
                          ("SYMBOL", '"', 1, 17)]),
    ('print ""', [("SYMBOL", '"', 1, 7),
                 ("STRING", "", 1, 8),
                 ("SYMBOL", '"', 1, 8)]),
    ('print "a\nb"', [("SYMBOL", '"', 1, 7),
                     ("STRING", "a\nb", 1, 8),
                     ("SYMBOL", '"', 2, 2)]),
])
def test_string_positions(source, expected):
    assert [(t.kind, t.value, t.line, t.column)
            for t in tokenize(source)[1:]] == expected


def test_nested_blocks_record_both_braces_and_inner_tokens():
    tokens = tokenize("if true {\n  loop 2 {\n    print 1\n  }\n}")
    outer = tokens[2]
    inner = outer[2]
    assert isinstance(outer, Block) and isinstance(inner, Block)
    assert (outer.open_brace.line, outer.open_brace.column) == (1, 9)
    assert (outer.close_brace.line, outer.close_brace.column) == (5, 1)
    assert (inner.open_brace.line, inner.open_brace.column) == (2, 10)
    assert (inner.close_brace.line, inner.close_brace.column) == (4, 3)
    assert (inner[0].value, inner[0].line, inner[0].column) == ("print", 3, 5)
    assert [(t.value, t.line, t.column) for t in flatten(tokens)
            if isinstance(t, Token) and t.value == "print"] == [("print", 3, 5)]


@pytest.mark.parametrize("source, values, last_position", [
    ("// heading\nprint 1", ["print", "1"], (2, 7)),
    ("print 1 // trailing\nprint 2", ["print", "1", "print", "2"], (2, 7)),
    ('print "// inside"', ["print", '"', "// inside", '"'], (1, 17)),
])
def test_comments(source, values, last_position):
    tokens = tokenize(source)
    assert [token.value for token in tokens] == values
    assert (tokens[-1].line, tokens[-1].column) == last_position


@pytest.mark.parametrize("source, message", [
    ('print "unfinished', "Unterminated quoted string"),
    ("}", "Unexpected '}'"),
    ("if true { print 1", "Unterminated '{' block"),
])
def test_lexer_rejects_unclosed_or_unexpected_delimiters(source, message):
    with pytest.raises(SyntaxError, match=message):
        tokenize(source)


def test_runner_keeps_original_tokens_through_nested_execution(capsys):
    tokens = tokenize("loop 2 {\n if true { print \"ok\" }\n}")
    outer, inner = tokens[2], tokens[2][2]
    command = inner[0]
    run(tokens, {})
    assert capsys.readouterr().out == "ok\nok\n"
    assert tokens[2] is outer and outer[2] is inner and inner[0] is command
    assert (command.line, command.column) == (2, 12)


def test_nested_runtime_error_identifies_original_command_and_block():
    tokens = tokenize("loop 1 {\n if true {\n  print [ missing ]\n }\n}")
    command = tokens[2][2][0]
    with pytest.raises(NameError) as raised:
        run(tokens, {})
    assert raised.value.token is command
    assert raised.value.block is tokens[2][2]
    assert raised.value.location == (3, 3)
    assert tokens[2][2].open_brace.line == 2


def test_legacy_string_tokens_and_blocks_still_run(capsys):
    run(["setvar", "[", "n", "]", "2", "loop", "2",
         ["addvar", "[", "n", "]", "1"], "print", "[", "n", "]"], {})
    assert capsys.readouterr().out == "4\n"


@pytest.mark.parametrize("source, output", [
    ('print "setvar print loop"', "setvar print loop\n"),
    ('setvar [ a ] 2\nsetvar [ b ] [ a ]\naddvar [ b ] 3\nprint [ b ]', "5\n"),
    ('if 2 != 3 { if 3 > 2 { print "yes" } }', "yes\n"),
    ('if 2 < 2 { print "bad" } else { print "equal" }', "equal\n"),
    ('loop 2 { loop 2 { print 1 } print 2 }', "1\n1\n2\n1\n1\n2\n"),
    ('if true { } else { print "bad" }\nloop -1 { print "bad" }\nprint 3', "3\n"),
])
def test_supported_execution_cases(source, output, capsys):
    run(tokenize(source), {})
    assert capsys.readouterr().out == output


@pytest.mark.parametrize("source, error, message", [
    ("print [ missing ]", NameError, "Undefined variable"),
    ("setvar [ n ] nope addvar [ n ] 1", TypeError, "Expected a number"),
    ("setvar [ n ] true addvar [ n ] 1", TypeError, "boolean"),
    ("setvar [ n ] 1 divvar [ n ] 0", ZeroDivisionError, "divide by zero"),
    ("print [ x", SyntaxError, "Expected a variable"),
    ("setvar [ ] 2", SyntaxError, "Expected a variable"),
    ("if true = true print 1", SyntaxError, "must be followed"),
    ("loop 1 print 2", SyntaxError, "must be followed"),
    ("print { print 1 }", SyntaxError, "Expected a value"),
    ("bogus", SyntaxError, "Unknown command"),
    ("if 1 >= 0 { print 1 }", SyntaxError, "Unknown comparison operator"),
])
def test_runner_error_paths(source, error, message):
    with pytest.raises(error, match=message) as raised:
        run(tokenize(source), {})
    assert raised.value.token is not None


def test_comparison_accepts_structured_operator():
    assert compare(2, Token("WORD", "<", 4, 7), 3)


def test_cli_valid_empty_tokens_and_version(tmp_path, capsys):
    program = tmp_path / "valid.meit"
    program.write_text("print 3", encoding="utf-8")
    assert main([str(program)]) == 0
    assert capsys.readouterr().out == "3\n"
    assert main(["--tokens", str(program)]) == 0
    output = capsys.readouterr().out
    assert "Token(kind='WORD', value='print', line=1, column=1)" in output
    assert output.endswith("3\n")
    program.write_text("", encoding="utf-8")
    assert main([str(program)]) == 0
    assert capsys.readouterr().out == ""
    with pytest.raises(SystemExit) as raised:
        main(["--version"])
    assert raised.value.code == 0
    assert "meitner " in capsys.readouterr().out


def test_cli_tokens_show_block_brace_locations(tmp_path, capsys):
    program = tmp_path / "block.meit"
    program.write_text("if true {\n print 1\n}", encoding="utf-8")
    assert main(["--tokens", str(program)]) == 0
    output = capsys.readouterr().out
    assert "Block(" in output
    assert "value='{', line=1, column=9" in output
    assert "value='}', line=3, column=1" in output


def test_cli_missing_file_reports_stderr(tmp_path, capsys):
    assert main([str(tmp_path / "missing.meit")]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "File not found" in captured.err


@pytest.mark.xfail(strict=True, raises=IsADirectoryError,
                   reason="CLI directory error handling is task #9")
def test_cli_directory_path_expected_failure(tmp_path):
    assert main([str(tmp_path)]) == 1


@pytest.mark.xfail(strict=True, raises=UnicodeDecodeError,
                   reason="CLI invalid UTF-8 handling is task #9")
def test_cli_invalid_utf8_expected_failure(tmp_path):
    program = tmp_path / "invalid.meit"
    program.write_bytes(b"\xff")
    assert main([str(program)]) == 1


@pytest.mark.xfail(strict=True, raises=PermissionError,
                   reason="CLI permission error handling is task #9")
def test_cli_permission_denied_expected_failure(tmp_path):
    program = tmp_path / "restricted.meit"
    program.write_text("print 1", encoding="utf-8")
    program.chmod(0)
    try:
        if program.read_text(encoding="utf-8") == "print 1":
            pytest.skip("File permissions do not restrict this test process")
    except PermissionError:
        pass
    finally:
        program.chmod(0o600)
    program.chmod(0)
    try:
        assert main([str(program)]) == 1
    finally:
        program.chmod(0o600)
