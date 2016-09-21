__author__ = "jacobvanthoog"

localDict = { }


def runScript(script):
    """
    Run a script. Scripts will share the same local dictionary.
    """
    exec(script, globals(), localDict)

def setVariable(script, varName):
    """
    Set a variable from the value of the script. Return the value.
    """
    value = eval(script, globals(), localDict)
    if varName != "":
        localDict[varName] = value
    return value

