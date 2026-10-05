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
        variable_values[(variable_names.index(var))]=value

    # Walk through tokens and dispatch each supported command.
    t = 0
    while t < len(x):
        if x[t] == "print":
            # Print either a variable value or a literal token.
            if x[t+1] == "[":
                print(callvar(x[t+2]))
            else:
                print(x[t+2])

        elif x[t] == "if":
            # Evaluate the condition and run its nested block when true.
            # "if true { ... }" has its block at t+2; comparisons like
            # "if a = b { ... }" have it at t+4.
            if x[t+1] == "true":
                run(x[t+2], variable_names, variable_values)
            elif x[t+2] == "=":
                if x[t+1] == x[t+3]:
                    run(x[t+4], variable_names, variable_values)
            elif x[t+2] == ">":
                if int(x[t+1]) > int(x[t+3]):
                    run(x[t+4], variable_names, variable_values)
            elif x[t+2] == "<":
                if int(x[t+1]) < int(x[t+3]):
                    run(x[t+4], variable_names, variable_values)
            elif x[t+2] == "!=":
                if x[t+1] != x[t+3]:
                    run(x[t+4], variable_names, variable_values)
        elif x[t] == "setvar":
            # Update an existing variable or create it on first assignment.
            if x[t+2] in variable_names:
                if x[t+4] == '"':
                    setvar(x[t+2],x[t+5])
                else:
                    setvar(x[t+2],x[t+4])
            else:
                if x[t+4] == '"':
                    makevar(x[t+2],x[t+5])
                else:
                    makevar(x[t+2],x[t+4])
        elif x[t] == "addvar":
            # Add a numeric value to the variable's current value.
            setvar(x[t+2],int(x[t+4])+int(callvar(x[t+2])))
        elif x[t] == "divvar":
            # divide a variable's value by an input number
            setvar(x[t+2],int(callvar(x[t+2]))/int(x[t+4]))
        elif x[t] == "subvar":
            # subtract a numeric value from the variable's current value
            setvar(x[t+2],int(callvar(x[t+2]))-int(x[t+4]))
        elif x[t] == "multvar":
            # multiply a variable's value by an input number
            setvar(x[t+2],int(callvar(x[t+2]))*int(x[t+4]))
        t += 1