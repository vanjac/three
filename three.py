__author__ = "vantjac"
__name__ = "__main__"

import sys
from pathlib import Path
from threelib import files
from threelib.edit.editorMain import EditorMain

THREE_VERSION = 0

print("three version " + str(THREE_VERSION))

# interpret command-line args
gameDirPathString = ""
mapName = ""
editorMode = False

numArgs = len(sys.argv)

if numArgs == 1:
    exit()
if numArgs == 2:
    print("Please enter a map name.")
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
        print("Map not found")
        exit()
except ValueError: # mapName is not a number
    try:
        files.setCurrentMap(files.getMap(mapName))
    except FileNotFoundError:
        print("Map not found")
        exit()

print("Map path: " + str(files.getCurrentMap()))
if editorMode:
    print("Edit mode.")
    EditorMain.main()
else:
    print("Run mode.")
