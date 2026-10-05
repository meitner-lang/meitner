def run(x, varn, varv):

    # Keep the caller's variable lists available to nested command blocks.
    variable_names = varn
    variable_values = varv

    # Helpers used by the variable-related commands below.
    def makevar(var, value):
        variable_names.append(var)
        variable_values.append(value)

    def callvar(var):
        return variable_values[(variable_names.index(var))]

    def setvar(var, value):
        variable_values[(variable_names.index(var))] = value

    # Boolean literal helpers.
    def is_bool_token(token):
        return token == "true" or token == "false"

    def to_bool(token):
        if token == "true":
            return True
        if token == "false":
            return False
        raise SyntaxError(f"Expected 'true' or 'false', got: {token}")

    def format_value(value):
        # Booleans print as lowercase Meitner literals, not Python's True/False.
        if isinstance(value, bool):
            return "true" if value else "false"
        return value

    def to_int(value):
        if isinstance(value, bool):
            raise TypeError("Cannot use a boolean in arithmetic")
        return int(value)

    # Walk through tokens and dispatch each supported command.
    t = 0
    while t < len(x):
        if x[t] == "print":
            # Print a variable value, a boolean literal, or a quoted string.
            if x[t+1] == "[":
                print(format_value(callvar(x[t+2])))
            elif is_bool_token(x[t+1]):
                print(x[t+1])
            else:
                print(x[t+2])

        elif x[t] == "if":
            # Two forms:
            #   if left op right { ... }   (block at t+4)
            #   if true/false { ... }      (block at t+2)
            if isinstance(x[t+2], list):
                condition = to_bool(x[t+1])
                block_idx = t + 2
            else:
                left, op, right = x[t+1], x[t+2], x[t+3]

                if op == "=":
                    condition = left == right
                elif op == "!=":
                    condition = left != right
                elif op == ">":
                    condition = int(left) > int(right)
                elif op == "<":
                    condition = int(left) < int(right)
                else:
                    raise SyntaxError(f"Unknown comparison operator: {op}")

                block_idx = t + 4

            # An else is present if the token after the if-block is "else"
            # followed by a block.
            has_else = (
                block_idx + 2 < len(x)
                and x[block_idx + 1] == "else"
                and isinstance(x[block_idx + 2], list)
            )

            if condition:
                run(x[block_idx], variable_names, variable_values)
            elif has_else:
                run(x[block_idx + 2], variable_names, variable_values)

            # Skip past the whole statement so the else block is never
            # scanned as if it were standalone code.
            t = block_idx + 2 if has_else else block_idx

        elif x[t] == "setvar":
            # Update an existing variable or create it on first assignment.
            if x[t+4] == '"':
                value = x[t+5]
            elif is_bool_token(x[t+4]):
                value = to_bool(x[t+4])
            else:
                value = x[t+4]

            if x[t+2] in variable_names:
                setvar(x[t+2], value)
            else:
                makevar(x[t+2], value)

        elif x[t] == "addvar":
            # Add a numeric value to the variable's current value.
            setvar(x[t+2], to_int(x[t+4]) + to_int(callvar(x[t+2])))
        elif x[t] == "divvar":
            # divide a variable's value by an input number
            setvar(x[t+2], to_int(callvar(x[t+2])) / to_int(x[t+4]))
        elif x[t] == "subvar":
            # subtract a numeric value from the variable's current value
            setvar(x[t+2], to_int(callvar(x[t+2])) - to_int(x[t+4]))
        elif x[t] == "multvar":
            # multiply a variable's value by an input number
            setvar(x[t+2], to_int(callvar(x[t+2])) * to_int(x[t+4]))
        t += 1