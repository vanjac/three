__author__ = "vantjac"
__name__ = "__main__"

import sys
from pathlib import Path

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
    gameDirPath = Path(gameDirPathString).resolve()
except FileNotFoundError:
    print("Game directory not found")
    exit()

print("Game directory: " + str(gameDirPath))

try:
    mapNumber = int(mapName) - 1
    mapListPath = gameDirPath / "maps.txt"
    try:
        with mapListPath.open() as f:
            lines = f.readlines()
            try:
                mapName = lines[mapNumber].strip()
            except IndexError:
                print("Invalid map number")
                exit()
    except FileNotFoundError:
        print("No maps.txt found in directory")
        exit()
except ValueError: # mapName is not a number
    pass

try:
    mapPath = (gameDirPath / "maps" / mapName).resolve()
except FileNotFoundError:
    print("Map not found")
    exit()

print("Map name: " + mapName)
print("Map path: " + str(mapPath))
if editorMode:
    print("Edit mode.")
else:
    print("Run mode.")
