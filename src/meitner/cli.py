"""Command-line entry point: `meitner file.meit`."""

import argparse
import sys

from . import __version__, runner
from .tokenizer import tokenize


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="meitner", description="Run a Meitner program."
    )
    ap.add_argument("file", help="path to a .meit source file")
    ap.add_argument(
        "--tokens", action="store_true", help="print the token list before running"
    )
    ap.add_argument("--version", action="version", version=f"meitner {__version__}")
    args = ap.parse_args(argv)

    try:
        with open(args.file, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1

    try:
        tokens = tokenize(content)
        if args.tokens:
            print(tokens)
            print()
        runner.run(tokens, {})
    except (SyntaxError, NameError, TypeError, ZeroDivisionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
