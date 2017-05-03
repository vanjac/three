__author__ = "jacobvanthoog"

import sys
from pathlib import Path
import os.path
import pickle
import webbrowser
import platform
import configparser
from threelib.edit.state import EditorState


gameDirPath = None

def setGameDir(path):
    """
    Set the Path to the game directory - required for most files operations.
    """
    global gameDirPath
    if path is None:
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
            parentDir = (parentDir / d).resolve()
            if parentDir.name.lower() == d.lower() and parentDir.name != d:
                print("Please use correct case in file paths!")
                return None

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

def getMeshDir():
    """
    Get the Path to the directory containing meshes.
    """
    return getGameDir() / "meshes"

def getMesh(name):
    """
    Get the Path to the mesh with the specified name.
    """
    return getResourcePath(getMeshDir(), name)

def getAudioDir():
    """
    Get the Path to the directory containing scripts.
    """
    return getGameDir() / "audio"

def getAudio(name):
    """
    Get the Path to the script with the specified name.
    """
    return getResourcePath(getAudioDir(), name)

def saveMapState(path, state):
    """
    Save map state to a file. ``path`` is a Path to the map file. ``state`` is
    an EditorState object
    """
    # large meshes will cause a lot of recursion while pickling
    # the recursion limit will temporarily be increased
    # TODO: some testing needs to be done for the best recursion depth value
    # TODO: avoid recursion in meshes?
    oldRecursionLimit = sys.getrecursionlimit() # default is 1000 for me
    sys.setrecursionlimit(10000)
    
    try:
        with path.open('wb') as f:
            pickle.dump(state, f, protocol=4)
    finally:
        sys.setrecursionlimit(oldRecursionLimit)

def loadMapState(path):
    """
    Load the map state at the specified file Path. Return an EditorState object,
    or None.
    """
    try:
        with path.open('rb') as f:
            state = pickle.load(f)
    except FileNotFoundError:
        print("File not found:", path)
        return None
    except EOFError: # map is empty
        return None
    except (ImportError, AttributeError, pickle.UnpicklingError) as e:
        print("The map couldn't be loaded.")
        print(e)
        return None
    except BaseException as e:
        print("Unknown error while loading map.")
        print(str(e))
        return None

    try:
        state.MAJOR_VERSION
    except AttributeError:
        state.MAJOR_VERSION = -1
        state.MINOR_VERSION = 0

    print("File version:",
          str(state.MAJOR_VERSION) + "." + str(state.MINOR_VERSION))
    print("Current editor file version:", str(EditorState.CURRENT_MAJOR_VERSION)
          + "." + str(EditorState.CURRENT_MINOR_VERSION))
    if state.MAJOR_VERSION > EditorState.CURRENT_MAJOR_VERSION:
        print("This file was created with a newer version of three, and cannot"
              " be opened.")
        return None
    elif state.MAJOR_VERSION < EditorState.CURRENT_MAJOR_VERSION:
        print("This file was created with an older version of three. If you"
              " save it now, you won't be able to open it with an older version"
              " again.")
        state = _convertStateToCurrentVersion(state)
    elif state.MINOR_VERSION > EditorState.CURRENT_MINOR_VERSION:
        print("This file was created with a newer version of three. Some"
              " features may be missing, and may be lost if you save.")
    elif state.MINOR_VERSION < EditorState.CURRENT_MINOR_VERSION:
        print("This file was created with an older version of three. If you"
              " save it now, some features may be missing if you try to open"
              " it with an older version again.")
        state = _convertStateToCurrentVersion(state)

    if state is None:
        return None
    state.onLoad()
    return state

# maps tuples of (majorVersion, minorVersion) to functions
editorStateConverters = { }

def _convertStateToCurrentVersion(editorState):
    targetMajor = EditorState.CURRENT_MAJOR_VERSION
    targetMinor = EditorState.CURRENT_MINOR_VERSION

    while editorState.MAJOR_VERSION != targetMajor \
       or editorState.MINOR_VERSION != targetMinor:
        versionTuple = (editorState.MAJOR_VERSION, editorState.MINOR_VERSION)
        if versionTuple in editorStateConverters:
            editorState = editorStateConverters[versionTuple](editorState)
        else:
            print("Cannot convert this file!")
            return None
    return editorState

def editorStateConverter(majorVersion, minorVersion):
    """
    A decorator for functions that can convert an old EditorState version to a
    newer one.
    """
    def decorator(function):
        editorStateConverters[ (majorVersion, minorVersion) ] = function
        return function
    return decorator


def openProperties(text):
    """
    Create a temporary file for properties containing the specified text, then
    open it in a text editor.
    """
    path = getGameDir() / "propsTemp.txt"
    with path.open('w') as f:
        f.write(text)
    if platform.system() == "Darwin":
        os.system("open " + str(path))
    else:
        webbrowser.open(str(path))

def readProperties():
    """
    Read the contents of the temporary properties file.
    """
    path = getGameDir() / "propsTemp.txt"
    with path.open() as f:
        return f.read()

def readGameConfig():
    """
    Read the game configuration file. Return a ConfigParser.
    """
    config = configparser.ConfigParser()
    config.read(str(getGameDir() / "config.ini"))
    return config
