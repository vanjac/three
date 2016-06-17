# three

When three is finished, it will be a 3d game engine with a map editor, written in Python and with Python scripting. But right now it is nowhere near finished.

## Starting

three requires Python 3.4, and all of the pip packages listed in `dependencies.txt`. You may have to install extra things to get those packages to work properly; look it up.

To use three, you need a game directory to work with. `gameDirTemplate` has a sample game directory layout with some useful materials.

three has 2 modes of operation: run mode, and edit mode. Run mode doesn't do anything at all at the moment, and edit mode doesn't do very much either. To start three in edit mode, type `python3 three.py path/to/game/dir mapName e`. `mapName` is relative to the `maps` folder in the game directory; if the map does not exist, it will be created. The `e` indicates edit mode; you can use `r` or omit it entirely for run mode.

If a window with green and blue lines appears, it worked.

## Controls

- Right click, then use the mouse and `WASDQE` keys to fly around. Use the mouse wheel to control fly speed.
- `nb` to create a New Box and enter translate adjust mode to move it (see below)
- Left click to select objects; hold shift to select multiple.
- `a` to select none or all objects
- Backspace to delete objects
- `c` to duplicate the selected object(s), and enter translate adjust mode to move them (see below)
- `mv` to switch to vertex select mode, `mf` for face select and `mo` for object select mode (default)
- `g` to enter translate ("Grab") adjust mode for the selected objects (see below)
- `r` to enter Rotate adjust mode
- `s Enter` to enter Resize adjust mode, which changes the dimensions of the selected object(s)
- `Shift-s Enter` to enter Scale adjust mode
- With the two vertices of an edge selected, `d` to divide the edge
- `Esc` to cancel all current operations
- `` ` `` to save

### Adjust Mode

Adjust mode is used to translate, rotate, and scale objects.

- Move the mouse to move, rotate, or scale objects
- `x` `y` and `z` to select the x, y, and z axes for adjusting. The mouse only has two axes so you can only be adjusting two at a time. The last two letters you type are the axes you are adjusting - if you type the same letter twice, you only adjust one axis.
- Left click or `Enter` to confirm and exit adjust mode
- `Esc` to cancel
- `[` and `]` to increase / decrease the grid size. The grid is different for translating, rotating, and scaling.
- `s` to toggle snap to grid. The grid is relative, so if you are already off the grid you will continue to be off the grid, but you will still move in grid size increments.
- `a` to move to the nearest, absolute grid point for the selected axes
- `o` to jump to the origin
- A number, terminated by an `x` `y` or `z`, to set the value of a certain axis.
- `r` to toggle relative / absolute coordinates when entering axis values. Relative coordinates are relative to the starting position.
