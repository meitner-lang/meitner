from dataclasses import dataclass
from bisect import bisect_right

@dataclass
class Token:
    kind: str
    value: str
    line: int
    column: int


class Block(list):
    """A token list with the locations of its surrounding braces."""

    def __init__(self, tokens, open_brace, close_brace):
        super().__init__(tokens)
        self.open_brace = open_brace
        self.close_brace = close_brace

    def __repr__(self):
        return (f"Block({list.__repr__(self)}, open_brace={self.open_brace!r}, "
                f"close_brace={self.close_brace!r})")

    @property
    def line(self):
        return self.open_brace.line

    @property
    def column(self):
        return self.open_brace.column

def get_location(content, position):
    line = content.count("\n", 0, position) + 1

    last_newline = content.rfind("\n", 0, position)
    column = position - last_newline

    return line, column


"""Meitner tokenizer: turns source text into a nested list of tokens."""


def parse(content, o, nested, _line_starts=None, _open_brace=None):
    """Turn source text into tokens, starting at index o.

    A { } block becomes a nested list, parsed by calling this function again,
    so blocks can contain other blocks. Returns (tokens, next_index).
    """
    if _line_starts is None:
        _line_starts = [0] + [i + 1 for i, ch in enumerate(content) if ch == "\n"]

    def location(position):
        line_index = bisect_right(_line_starts, position) - 1
        return line_index + 1, position - _line_starts[line_index] + 1

    tokens = []

    while o < len(content):
        ch = content[o]

        if ch.isspace():
            o += 1

        elif content.startswith("//", o):
            # Comments run to the end of the line.
            while o < len(content) and content[o] != "\n":
                o += 1

        elif ch == "{":
            line, column = location(o)
            opening = Token("SYMBOL", "{", line, column)
            block, o = parse(content, o + 1, nested=True,
                             _line_starts=_line_starts, _open_brace=opening)
            tokens.append(block)

        elif ch == "}":
            if not nested:
                raise SyntaxError("Unexpected '}' with no matching '{'")
            line, column = location(o)
            closing = Token("SYMBOL", "}", line, column)
            return Block(tokens, _open_brace, closing), o + 1

        elif ch == '"':
            end = content.find('"', o + 1)

            if end == -1:
                raise SyntaxError("Unterminated quoted string")

            open_line, open_column = location(o)
            text_line, text_column = location(o + 1)
            close_line, close_column = location(end)

            tokens.extend([
                Token("SYMBOL", '"', open_line, open_column),
                Token("STRING", content[o + 1:end], text_line, text_column),
                Token("SYMBOL", '"', close_line, close_column)
            ])

            o = end + 1

        elif ch == "[" or ch == "]":
            line, column = location(o)

            tokens.append(
                Token(
                    kind="SYMBOL",
                    value=ch,
                    line=line,
                    column=column
                )
            )

            o += 1

        else:
            start = o

            while (
                o < len(content)
                and not content[o].isspace()
                and content[o] not in '"{}[]'
            ):
                o += 1

            line, column = location(start)

            tokens.append(
                Token(
                    kind="WORD",
                    value=content[start:o],
                    line=line,
                    column=column
                )
            )


    if nested:
        raise SyntaxError("Unterminated '{' block")
    return tokens, o


def tokenize(content):
    """Tokenize a whole program and return just the token list."""
    tokens, _ = parse(content, 0, nested=False)
    return tokens


if __name__ == "__main__":
    source = 'setvar [ x ] 10\nprint [ x ]'

    result = tokenize(source)

    for token in result:
        print(token)
