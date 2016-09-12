# three

When three is finished, it will be a 3d game engine with a map editor, written in Python and with Python scripting. But right now it is nowhere near finished.

## Starting

three requires at least Python 3.4, and these pip packages:
- pillow: installation instruction [here](https://pillow.readthedocs.io/en/3.0.0/installation.html).
  - On Mac you will need to run `xcode-select --install` first.
- PyOpenGL and optionally PyOpenGL_accelerate: installation instructions [here](http://pyopengl.sourceforge.net/documentation/installation.html).
  - PyOpenGL_accelerate seems to have problems on Windows.
  - On Linux, you will first need to use a package manager to install `python3-dev` (or `python3-devel`), and `freeglut` (or equivalent).
    - On Fedora, you might need to run `dnf install redhat-rpm-config` first.
- pyautogui: installation instructions [here](https://pyautogui.readthedocs.io/en/latest/install.html). Make sure you have installed pillow first.
  - For Linux, the instructions refer to `python3-tk`, which may be called `python3-tkinter` instead; and `python3-dev`, which may be called `python3-devel` instead. 
  - On Linux, if you get an Xlib error on the last step, type `xhost +` before you try to install it again. See [here](https://ubuntuforums.org/showthread.php?t=2290602).

You may have problems with GLUT errors on Windows. Try installing freeglut.

To use three, you need a game directory to work with. `gameDirTemplate` has a sample game directory layout with some useful materials. To start three, type `python3 three.py path/to/game/dir mapName`. `mapName` is relative to the `maps` folder in the game directory; if the map does not exist, it will be created. You can also specify a map number instead - this will look up names in `maps.txt` (starts at 1).

By default, three starts in Run Mode, which doesn't currently exist. To start the editor instead, use the `-edit` flag. The `-run` flag explicitly specifies run mode.

Try navigating to the root of this repository and typing `python3 three.py gameDirTemplate 1 -edit`. If a window appears with green and blue lines and some text at the bottom, it worked.

## Controls

### General
- `Esc` to cancel any operations
- `` ` `` to save
- Right click, then use the mouse and `WASDQE` keys to fly around. Use the mouse wheel to control fly speed.
- `nb` to create a New Box and enter translate-adjust mode to move it (see below)
- Left click to select objects; hold shift to select multiple.
- `a` to select none or All objects
- `Backspace` to delete objects
- `c` to duplicate ("Copy") selected objects and enter translate-adjust mode to move them (see below)
- `mv` to switch to Vertex select mode, `mf` for Face select and `mo` for Object select mode (default)
- `Enter` to edit the properties of selected objects using your default text editor. When you are finished editing properties and have saved the file, press `u` ("Update") with the same objects selected to update their properties. If nothing is selected world properties will be edited.
- `g` to enter translate ("Grab") adjust mode for the selected objects (see below)
- `r` to enter Rotate adjust mode
- `s Enter` to enter reSize adjust mode, which changes the dimensions of the selected object(s). Before pressing Enter you can type any of the letters `nsewtb` (North South East West Top Bottom). With these you can choose to resize in just one direction along an axis.
- `Shift-s Enter` to enter Scale adjust mode. You can use the same direction letters as in Resize.
- `o` to adjust the Origins of selected objects in adjust mode.

### Mesh Editing
- With the two vertices of an edge selected, `d` to Divide the edge
- With two vertices selected, `Shift-d` to merge the second with the first ("undivide")
- With two non-edge vertices on the same face selected, `e` to divide that face with an Edge connecting them
- With two vertices of an edge selected that divides two coplanar polygons, `Shift-e` to merge the polygons and remove the edge.
- `h` to enter adjust mode to extrude the selected faces. If objects are selected, all faces will be extruded and the original object will be deleted afterwards ("Hollow").
- `k` with meshes selected to "clip" the selected meshes, using a plane to slice off part of them. Adjust mode is used to set a point on the clip plane, followed by the normal of the plane. The normal points in the direction of the half that is removed. 
- `Shift-k` to use the selected meshes to "carve" into all other meshes.

### Material
- `Shift-p path/to/texture Enter` to choose the current material. The texture must be in the the `materials` subdirectory of the game directory. Even if you are on Windows you must use `/` as a path separator and match the case of the file name. Textures can sometimes take a while to transfer to OpenGL, during which the editor will be unresponsive.
- `p` to "Paint" the current material on the selected faces or objects.
- `Shift-p Enter` to reload the current material's texture. Everything with that material will be updated.

### Adjust Mode

Adjust mode is used to translate, rotate, and scale objects. It has a completely different set of keyboard commands.

- Move the mouse to move, rotate, or scale objects
- `x` `y` and `z` to select the x, y, and z axes for adjusting. The mouse only has two axes so you can only be adjusting two at a time. The last two letters you type are the axes you are adjusting - if you type the same letter twice, you only adjust one axis.
- Left click or `Enter` to confirm and exit adjust mode
- `Esc` to cancel
- `[` and `]` to increase / decrease the grid size. The grid is different for translating, rotating, and scaling.
- `g` followed by a number and `Enter` to manually set the grid size.
- `s` to toggle Snap to grid. The grid is relative, so if you are already off the grid you will continue to be off the grid, but you will still move in grid size increments.
- `a` to move to the nearest, Absolute grid point for the selected axes
- `o` to jump to the Origin
- A number, terminated by an `x` `y` or `z`, to set the value of a certain axis.
- `r` to toggle Relative / absolute coordinates when entering axis values. Relative coordinates are relative to the starting position. Absolute is relative to the origin.
