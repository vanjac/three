__author__ = "jacobvanthoog"

from pathlib import Path
import os.path
import pickle
import webbrowser

gameDirPath = None

def setGameDir(path):
    """
    Set the Path to the game directory - required for most files operations.
    """
    global gameDirPath
    if path == None:
        gameDirPath = None
    else:
        gameDirPath = path.resolve()

def getGameDir():
    """
    Get the Path to the game directory.
    """
    return gameDirPath

def getMapDir():
    """
    Get the Path to the directory containing maps.
    """
    return getGameDir() / "maps"

def getMapList():
    """
    Get the Path to the text file containing a list of maps.
    """
    return getGameDir() / "maps.txt"

def getMap(name, createIfNotFound=True):
    """
    Get the Path to the map with the specified name. If it doesn't exist, 
    optionally create an empty file with that name and return it, otherwise
    return None.
    """
    try:
        return (getMapDir() / name).resolve()
    except FileNotFoundError:
        if createIfNotFound:
            with open(os.path.join(str(getMapDir()), name), 'a') as f:
                pass
            return (getMapDir() / name).resolve()
        else:
            return None

def getMapNumber(number):
    """
    Get the Path to the map with the name at the specified index in the maps
    list file (starts at 1). If it doesn't exist, create an empty file with that 
    name and return it.
    """
    if number < 0:
        print("Map number out of range!")
        return None
    try:
        with getMapList().open() as f:
            lines = f.readlines()
            try:
                mapName = lines[number].strip()
                print("Map name:", mapName)
                return getMap(mapName)
            except IndexError:
                print("Map number out of range!")
                return None
    except FileNotFoundError:
        print("Maps list file not found!")
        return None

def getResourcePath(directoryPath, name):
    """
    Given a root resource directory path, and a file name with '/' used as the
    path separator and no extension, return the full Path. Return None if not
    found.
    """
    try:
        dirs = name.split('/')
        parentDir = directoryPath
        for d in dirs[:-1]:
            parentDir = parentDir / d
        parentDir = parentDir.resolve()
        
        name = dirs[-1]
        for child in parentDir.iterdir():
            cName = ""
            cNames = child.name.split('.')
            if len(cNames) == 1 or len(cNames) == 2:
                cName = cNames[0]
            else:
                cName = cNames[0]
                for n in cNames[1:-1]:
                    cName += "." + n

            if cName == name:
                return child

        return None
    except (FileNotFoundError, OSError):
        return None

def getMaterialDir():
    """
    Get the Path to the directory containing materials.
    """
    return getGameDir() / "materials"

def getMaterial(name):
    """
    Get the Path to the material with the specified name.
    """
    return getResourcePath(getMaterialDir(), name)

def getScriptDir():
    """
    Get the Path to the directory containing scripts.
    """
    return getGameDir() / "scripts"

def getScript(name):
    """
    Get the Path to the script with the specified name.
    """
    return getResourcePath(getScriptDir(), name)
    
def loadScript(path):
    """
    Load the text contents of a script file path.
    """
    with path.open() as f:
        return f.read()

def saveMapState(path, state):
    """
    Save map state to a file. ``path`` is a Path to the map file. ``state`` is
    an EditorState object
    """
    with path.open('wb') as f:
        pickle.dump(state, f, protocol=4)

def loadMapState(path):
    """
    Load the map state at the specified file Path. Return an EditorState object,
    or None.
    """
    try:
        with path.open('rb') as f:
            editorState = pickle.load(f)
            editorState.onLoad()
            return editorState
    except EOFError: # map is empty
        return None

def openProperties(text):
    """
    Create a temporary file for properties containing the specified text, then
    open it in a text editor.
    """
    path = getGameDir() / "propsTemp.txt"
    with path.open('w') as f:
        f.write(text)
    webbrowser.open(str(path))

def readProperties():
    """
    Read the contents of the temporary properties file.
    """
    path = getGameDir() / "propsTemp.txt"
    with path.open() as f:
        return f.read()

