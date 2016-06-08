# three

When three is finished, it will be a 3d game engine with a map editor, written in Python and with Python scripting. But right now it is nowhere near finished.

## Running

three requires Python 3.4, and all of the pip packages listed in `dependencies.txt`. You may have to install extra things to get those packages to work properly; look it up.

To use three, you need a game directory to work with. `gameDirTemplate` has a sample game directory layout with some useful materials. You'll need to create a `maps` folder in this.

three has 2 modes of operation: run mode, and edit mode. Run mode doesn't do anything at all at the moment, and edit mode doesn't do very much either. To start three in edit mode, type `python3 three.py path/to/game/dir mapName e`. `mapName` is relative to the `maps` folder in the game directory; if the map does not exist, it will be created. The `e` indicates edit mode; you can use `r` or omit it entirely for run mode.

If a window with colorful triangles appears, it worked. Try mashing on the keyboard and clicking with different mouse buttons and you can probably get something to happen. If your mouse becomes hidden or strange things start happening, press escape. Close the window to quit.
