def run(x, varn, varv):

    variable_names = varn
    variable_values = varv

    def makevar(var, value):
        variable_names.append(var)
        variable_values.append(value)

    def callvar(var):
        return variable_values[(variable_names.index(var))]

    def setvar(var, value):
        variable_values[(variable_names.index(var))]=value

    t = 0
    while t < len(x):
        if x[t] == "print":
            if x[t+1] == "[":
                print(callvar(x[t+2]))
            else:
                print(x[t+2])

        elif x[t] == "if":
            if x[t+2] == "=":
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
                    setvar(x[t+2],int(x[t+4])+int(callvar(x[t+2])))            

        t += 1