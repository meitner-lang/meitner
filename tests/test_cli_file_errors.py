"""Regression coverage for CLI failures while opening or reading source files."""

import builtins

from meitner.cli import main


def test_directory_argument_returns_error(tmp_path, capsys):
    assert main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "directory" in captured.err.lower()
    assert "Traceback" not in captured.err


def test_invalid_utf8_returns_error(tmp_path, capsys):
    source = tmp_path / "invalid.meit"
    source.write_bytes(b"print \xff")
    assert main([str(source)]) == 1
    captured = capsys.readouterr()
    assert "UTF-8" in captured.err
    assert "Traceback" not in captured.err


def test_permission_denied_returns_error(tmp_path, capsys, monkeypatch):
    source = tmp_path / "blocked.meit"
    source.write_text('print "hello"', encoding="utf-8")
    original_open = builtins.open

    def denied_open(file, *args, **kwargs):
        if str(file) == str(source):
            raise PermissionError(13, "Permission denied", str(source))
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", denied_open)
    assert main([str(source)]) == 1
    captured = capsys.readouterr()
    assert "Permission denied" in captured.err
    assert "Traceback" not in captured.err


def test_other_read_error_returns_error(tmp_path, capsys, monkeypatch):
    source = tmp_path / "broken.meit"
    source.write_text('print "hello"', encoding="utf-8")
    original_open = builtins.open

    def failing_open(file, *args, **kwargs):
        if str(file) == str(source):
            raise OSError("Simulated I/O failure")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing_open)
    assert main([str(source)]) == 1
    captured = capsys.readouterr()
    assert "Simulated I/O failure" in captured.err
    assert "Traceback" not in captured.err
