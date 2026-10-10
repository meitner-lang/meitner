from dataclasses import dataclass

@dataclass
class Token:
    kind: str
    value: str
    line: int
    column: int

def get_location(content, position):
    line = content.count("\n", 0, position) + 1

    last_newline = content.rfind("\n", 0, position)
    column = position - last_newline

    return line, column


"""Meitner tokenizer: turns source text into a nested list of tokens."""


def parse(content, o, nested):
    """Turn source text into tokens, starting at index o.

    A { } block becomes a nested list, parsed by calling this function again,
    so blocks can contain other blocks. Returns (tokens, next_index).
    """
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
            block, o = parse(content, o + 1, nested=True)
            tokens.append(block)

        elif ch == "}":
            if not nested:
                raise SyntaxError("Unexpected '}' with no matching '{'")
            return tokens, o + 1          # end of this block

        elif ch == '"':
            end = content.find('"', o + 1)

            if end == -1:
                raise SyntaxError("Unterminated quoted string")

            open_line, open_column = get_location(content, o)
            text_line, text_column = get_location(content, o + 1)
            close_line, close_column = get_location(content, end)

            tokens.extend([
                Token("SYMBOL", '"', open_line, open_column),
                Token("STRING", content[o + 1:end], text_line, text_column),
                Token("SYMBOL", '"', close_line, close_column)
            ])

            o = end + 1

        elif ch == "[" or ch == "]":
            line, column = get_location(content, o)

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

            line, column = get_location(content, start)

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