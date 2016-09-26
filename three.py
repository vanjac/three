__author__ = "vantjac"
__name__ = "__main__"

import sys
from pathlib import Path
from threelib import files

THREE_VERSION = 0

print("three version " + str(THREE_VERSION))

# interpret command-line args
gameDirPathString = None
mapName = None
editorMode = False

flags = [ ]

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            if len(arg) > 1:
                flag = arg[1:]
                if flag.lower() == "edit":
                    editorMode = True
                elif flag.lower() == "run":
                    editorMode = False
                else:
                    flags.append(arg[1:])
            else:
                print("Invalid argument", arg)
                exit()
        elif gameDirPathString == None:
            gameDirPathString = arg
        elif mapName == None:
            mapName = arg
        else:
            print("Invalid argument", arg)

if mapName == None:
    print("To run, three needs:")
    print("  - A game directory path with a maps folder")
    print("  - A map name or number")
    print("     (a number will read map names from maps.txt in the game"
        + " directory)")
    print("  - A mode: r or e for run or edit mode. Default is run mode.")
    print("See the README")
    exit()

try:
    files.setGameDir(Path(gameDirPathString))
except FileNotFoundError:
    print("Game directory not found")
    exit()
    

mapPath = None

try:
    mapNumber = int(mapName) - 1
    mapPath = files.getMapNumber(mapNumber)
    if mapPath == None:
        print("Map number", mapNumber + 1, "not found")
        exit()
except ValueError: # mapName is not a number
    try:
        mapPath = files.getMap(mapName, createIfNotFound=editorMode)
        if mapPath == None:
            print("Map", mapName, "not found")
            exit()
    except FileNotFoundError:
        print("Map", mapName, "not found")
        exit()

state = files.loadMapState(mapPath)
if editorMode:
    from threelib.appInstance.gl import GLAppInstance
    from threelib.edit.gl.glEditor import GLEditor
    interface = GLEditor(mapPath, state)
    GLAppInstance(interface, flags)
else:
    if state == None:
        print("Map", mapName, "not found")
        exit()
    from threelib.appInstance.gl import GLAppInstance
    from threelib.run.gl.glRunner import GLRunner
    interface = GLRunner(state)
    GLAppInstance(interface, flags)

