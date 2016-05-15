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
    if number <= 0:
        return None
    try:
        with getMapList().open() as f:
            lines = f.readlines()
            try:
                return getMap(lines[number].strip())
            except IndexError:
                return None
    except FileNotFoundError:
        return None

def getMaterialDir():
    return getGameDir() / "materials"

def getMaterial(name):
    return (getMaterialDir() / name).resolve()


