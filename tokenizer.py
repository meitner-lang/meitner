import runner as run

# Token output and variable storage shared with the runner.
tokens = []
variable_names = []
variable_values = []

def makevar(var, value):
    variable_names.append(var)
    variable_values.append(value)

def callvar(var):
    return variable_values[(variable_names.index(var))]

# Read the source file that will be tokenized.
file_name = input("File name: ")
with open(file_name, encoding="utf-8") as file:
    content = file.read()

# Scan the source one character at a time and build tokens.
o = 0
while o < len(content):
    if content[o].isspace():
        o += 1
        continue

    if content[o] == "{":
        # Collect a brace-delimited command block as a nested token list.
        block = []
        tokens.append(block)
        o += 1

        while o < len(content) and content[o] != "}":
            if content[o].isspace():
                o += 1
                continue

            # Ignore comments (they run to the end of the line) and
            # preserve quoted text as a single token.
            if content[o] == "/" and o + 1 < len(content) and content[o + 1] == "/":
                while o < len(content) and content[o] != '\n':
                    o += 1

            elif content[o] == '"':
                o += 1
                start = o

                while o < len(content) and content[o] != '"':
                    o += 1

                if o >= len(content):
                    raise SyntaxError("Unterminated quoted string inside '{ ... }'")

                block.extend(['"', content[start:o], '"'])
                o += 1

            elif content[o] == "[":
                block.append("[")
                o += 1

            elif content[o] == "]":
                block.append("]")
                o += 1

            else:
                start = o
                while (
                    o < len(content)
                    and not content[o].isspace()
                    and content[o] not in {'"', '}', '[', ']'}
                ):
                    o += 1

                block.append(content[start:o])

        if o >= len(content):
            raise SyntaxError("Unterminated '{' block")

        o += 1  # Consume the closing brace

    # Handle comments, quoted strings, brackets, and ordinary tokens.
    elif content[o] == "/" and o + 1 < len(content) and content[o + 1] == "/":
        while o < len(content) and content[o] != '\n':
            o += 1
    elif content[o] == '"':
        o += 1
        start = o

        while o < len(content) and content[o] != '"':
            o += 1

        if o >= len(content):
            raise SyntaxError("Unterminated quoted string")

        tokens.extend(['"', content[start:o], '"'])
        o += 1

    elif content[o] == "[":
        tokens.append("[")
        o += 1

    elif content[o] == "]":
        tokens.append("]")
        o += 1

    else:
        start = o
        while (
            o < len(content)
            and not content[o].isspace()
            and content[o] not in {'"', '{', '}', '[', ']'}
        ):
            o += 1

        tokens.append(content[start:o])

# Show the tokens, then pass them to the interpreter.
print(tokens)
print()
print("i will now attempt to run the code")
print()

run.run(tokens, variable_names, variable_values)