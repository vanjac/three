__author__ = "vantjac"

from pathlib import Path
import os.path
import pickle

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
        open(os.path.join(str(getMapDir()), name), 'a')
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
    return (getMaterialDir() / name).resolve()


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
