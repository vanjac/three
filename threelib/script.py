__author__ = "jacobvanthoog"

localDict = dict(globals())


def runScript(script):
    """
    Run a script. Scripts will share the same local dictionary.
    """
    if script != "":
        exec(script, localDict, localDict)

def setVariable(script, varName):
    """
    Set a variable from the value of the script. Return the value.
    """
    if script == "":
        value = None
    else:
        value = eval(script, localDict, localDict)
    if varName != "":
        localDict[varName] = value
    return value

