import runner as run

tokens = []
variable_names = []
variable_values = []

def makevar(var, value):
    variable_names.append(var)
    variable_values.append(value)

def callvar(var):
    return variable_values[(variable_names.index(var))]

file_name = input("File name: ")
with open(file_name, encoding="utf-8") as file:
    content = file.read()

o = 0
while o < len(content):
    if content[o].isspace():
        o += 1
        continue

    if content[o] == "{":
        block = []
        tokens.append(block)
        o += 1

        while o < len(content) and content[o] != "}":
            if content[o].isspace():
                o += 1
                continue

            if content[o] == "/" and content[o + 1] == "/":
                while o < len(content) and content[o] != '/':
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

print(tokens)
print()
print("i will now attempt to run the code")
print()

run.run(tokens, variable_names, variable_values)
