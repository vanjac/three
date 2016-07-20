__author__ = "vantjac"
__name__ = "__main__"

import sys
from pathlib import Path
from threelib import files
from threelib.edit.gl.glMain import EditorMain

THREE_VERSION = 0

print("three version " + str(THREE_VERSION))

# interpret command-line args
gameDirPathString = ""
mapName = ""
editorMode = False

numArgs = len(sys.argv)

if numArgs == 1 or numArgs == 2:
    print("To run, three needs:")
    print("  - A game directory path with a maps folder")
    print("  - A map name or number")
    print("     (a number will read map names from maps.txt in the game"
        + " directory)")
    print("  - A mode: r or e for run or edit mode. Default is run mode.")
    exit()
if numArgs >= 3:
    gameDirPathString = sys.argv[1]
    mapName = sys.argv[2]
    if numArgs >= 4:
        editorMode = (sys.argv[3] == 'e')

try:
    files.setGameDir(Path(gameDirPathString))
except FileNotFoundError:
    print("Game directory not found")
    exit()

print("Game directory: " + str(files.getGameDir()))

try:
    mapNumber = int(mapName) - 1
    files.setCurrentMap(files.getMapNumber(mapNumber))
    if files.getCurrentMap() == None:
        print("Map number", mapNumber + 1, "not found")
        exit()
except ValueError: # mapName is not a number
    try:
        files.setCurrentMap(files.getMap(mapName))
        if files.getCurrentMap() == None:
            print("Map", mapName, "not found")
            exit()
    except FileNotFoundError:
        print("Map", mapName, "not found")
        exit()

print("Map path: " + str(files.getCurrentMap()))
if editorMode:
    print("Edit mode")
    EditorMain.main(files.loadMapState(files.getCurrentMap()))
else:
    print("Run mode")
    print("Not supported yet")
