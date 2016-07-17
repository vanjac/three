__author__ = "vantjac"

from pathlib import Path
import os.path
import pickle
import webbrowser

gameDirPath = None
mapPath = None

def setGameDir(path):
    global gameDirPath
    if path == None:
        gameDirPath = None
    else:
        gameDirPath = path.resolve()

def getGameDir():
    return gameDirPath

def setCurrentMap(path):
    global mapPath
    if path == None:
        mapPath = None
    else:
        mapPath = path.resolve()

def getCurrentMap():
    return mapPath

def getMapDir():
    return getGameDir() / "maps"

def getMapList():
    return getGameDir() / "maps.txt"

# create map if it doesn't exist
def getMap(name):
    try:
        return (getMapDir() / name).resolve()
    except FileNotFoundError:
        with open(os.path.join(str(getMapDir()), name), 'a') as f:
            pass
        return (getMapDir() / name).resolve()

def getMapNumber(number):
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
        print("File not found!")
        return None

def getMaterialDir():
    return getGameDir() / "materials"

def getMaterial(name):
    return (getMaterialDir() / (name + ".bmp")).resolve()


# path is a Path to the map file
# state is an EditorState object
def saveMapState(path, state):
    with path.open('wb') as f:
        pickle.dump(state, f, protocol=4)

# return an EditorState object, or None
def loadMapState(path):
    try:
        with path.open('rb') as f:
            return pickle.load(f)
    except EOFError: # map is empty
        return None


# create a temporary file for properties, then open it in an editor
def openProperties(text):
    path = getGameDir() / "propsTemp.txt"
    with path.open('w') as f:
        f.write(text)
    webbrowser.open(str(path))

def readProperties():
    path = getGameDir() / "propsTemp.txt"
    with path.open() as f:
        return f.read()
