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
            # Quoted text stays together as one token between two '"' tokens.
            end = content.find('"', o + 1)
            if end == -1:
                raise SyntaxError("Unterminated quoted string")
            tokens.extend(['"', content[o + 1:end], '"'])
            o = end + 1

        elif ch == "[" or ch == "]":
            tokens.append(ch)
            o += 1

        else:
            # Ordinary word: runs until whitespace or a special character.
            start = o
            while (
                o < len(content)
                and not content[o].isspace()
                and content[o] not in '"{}[]'
            ):
                o += 1
            tokens.append(content[start:o])

    if nested:
        raise SyntaxError("Unterminated '{' block")
    return tokens, o


def tokenize(content):
    """Tokenize a whole program and return just the token list."""
    tokens, _ = parse(content, 0, nested=False)
    return tokens
