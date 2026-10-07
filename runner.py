"""Meitner interpreter: executes the token list produced by the tokenizer.

Commands (spaces around [ ], =, and the other tokens are required):
    print <value>
    setvar [ name ] <value>
    addvar|subvar|multvar|divvar [ name ] <value>
    if <value> { ... } [else { ... }]
    if <value> <op> <value> { ... } [else { ... }]     op: = != > <
    loop <count> { ... }        repeat a block <count> times
    loop forever { ... }        repeat a block until the program is stopped

A <value> is a bare number, "a string", true/false, or [ variable ].
"""


# ---------- Value helpers ----------

def to_int(value):
    """Convert a value to int for arithmetic, rejecting booleans and text."""
    if isinstance(value, bool):
        raise TypeError("Cannot use a boolean in arithmetic")
    try:
        return int(value)
    except ValueError:
        raise TypeError(f"Expected a number, got: {value}")


def format_value(value):
    """Booleans print as lowercase Meitner literals, not Python's True/False."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def read_value(x, t, variables):
    """Read one value starting at x[t].

    Returns (value, next_index) so callers know where the value ended.
    """
    if t >= len(x):
        raise SyntaxError("Unexpected end of code: expected a value")

    token = x[t]
    if isinstance(token, list):
        raise SyntaxError("Expected a value but found a { } block")

    if token == '"':                      # "text" is three tokens: " text "
        return x[t + 1], t + 3

    if token == "[":                      # [ name ] is three tokens too
        name, next_t = read_name(x, t)
        if name not in variables:
            raise NameError(f"Undefined variable: {name}")
        return variables[name], next_t

    if token == "true" or token == "false":
        return token == "true", t + 1

    try:                                  # bare numbers become ints
        return int(token), t + 1
    except ValueError:
        return token, t + 1               # anything else stays a plain word


def read_name(x, t):
    """Read '[ name ]' starting at x[t]. Returns (name, next_index)."""
    if t + 2 >= len(x) or x[t] != "[" or x[t + 2] != "]":
        raise SyntaxError("Expected a variable written as [ name ]")
    return x[t + 1], t + 3


def expect_block(x, t, command):
    """Return the { } block at x[t], or raise a clear error."""
    if t >= len(x) or not isinstance(x[t], list):
        raise SyntaxError(f"'{command}' must be followed by a {{ }} block")
    return x[t]


# ---------- Comparisons and arithmetic ----------

def same_value(left, right):
    """True if both values have the same type and are equal.

    Checking the type too keeps true from being equal to 1.
    """
    return type(left) is type(right) and left == right


def compare(left, op, right):
    if op == "=":
        return same_value(left, right)
    if op == "!=":
        return not same_value(left, right)
    if op == ">":
        return to_int(left) > to_int(right)
    if op == "<":
        return to_int(left) < to_int(right)
    raise SyntaxError(f"Unknown comparison operator: {op}")


def divide(a, b):
    """Integer (floor) division, so variables always stay whole numbers."""
    if b == 0:
        raise ZeroDivisionError("divvar: cannot divide by zero")
    return a // b


MATH_COMMANDS = {
    "addvar": lambda a, b: a + b,
    "subvar": lambda a, b: a - b,
    "multvar": lambda a, b: a * b,
    "divvar": divide,
}


# ---------- Interpreter ----------

def run(x, variables):
    """Run a list of tokens. `variables` is a dict shared with nested blocks.

    Every branch moves `t` to the index of the next command, so tokens that
    belong to a command are never mistaken for new commands.
    """
    t = 0
    while t < len(x):
        command = x[t]

        if command == "print":
            value, t = read_value(x, t + 1, variables)
            print(format_value(value))

        elif command == "setvar":
            # Creates the variable on first use, updates it afterwards.
            name, t = read_name(x, t + 1)
            variables[name], t = read_value(x, t, variables)

        elif command in MATH_COMMANDS:
            name, t = read_name(x, t + 1)
            operand, t = read_value(x, t, variables)
            if name not in variables:
                raise NameError(f"Undefined variable: {name}")
            variables[name] = MATH_COMMANDS[command](
                to_int(variables[name]), to_int(operand)
            )

        elif command == "if":
            left, i = read_value(x, t + 1, variables)

            if i < len(x) and isinstance(x[i], list):
                # Form 1: if <true/false/[ var ]> { ... }
                if not isinstance(left, bool):
                    raise SyntaxError("'if' needs true/false or a comparison")
                condition = left
            else:
                # Form 2: if <value> <op> <value> { ... }
                if i >= len(x):
                    raise SyntaxError("Unexpected end of code in 'if'")
                op = x[i]
                right, i = read_value(x, i + 1, variables)
                condition = compare(left, op, right)

            block = expect_block(x, i, "if")

            # An else exists if the if-block is followed by: else { ... }
            has_else = (
                i + 2 < len(x)
                and x[i + 1] == "else"
                and isinstance(x[i + 2], list)
            )

            if condition:
                run(block, variables)
            elif has_else:
                run(x[i + 2], variables)

            # Skip the whole statement, including the else block.
            t = i + 3 if has_else else i + 1

        elif command == "loop":
            count, i = read_value(x, t + 1, variables)
            block = expect_block(x, i, "loop")

            if count == "forever":
                # No break command yet, so this runs until you press Ctrl+C.
                while True:
                    run(block, variables)
            elif isinstance(count, int) and not isinstance(count, bool):
                for _ in range(count):    # 0 or negative: runs zero times
                    run(block, variables)
            else:
                raise SyntaxError("loop needs a number or 'forever'")

            t = i + 1

        else:
            raise SyntaxError(f"Unknown command: {command}")
