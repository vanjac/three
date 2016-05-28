__author__ = "vantjac"

from pathlib import Path

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

def getMap(name):
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


