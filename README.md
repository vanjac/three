# three

When three is finished, it will be a 3d game engine with a map editor, written in Python and with Python scripting. But right now it is nowhere near finished.

## Install

three requires at least Python 3.4.

### Windows installation
- Install pillow: instructions for Windows [here](https://pillow.readthedocs.io/en/3.0.0/installation.html#windows-installation).
- Install PyOpenGL and PyOpenGL_accelerate:
  - First install freeglut:
    - Download [here](http://www.transmissionzero.co.uk/software/freeglut-devel/) or somewhere else.
    - Extract, put somewhere where you won't move it.
    - Add it to the PATH environment variable. Go to: Control Panel > System and Security > System > Advanced system settings > Environment variables. Select PATH, click Edit, and click New in the resulting dialog. Copy in the path to the `bin` folder in the extracted freeglut archive.
    - Restart your computer.
  - Follow the instructions [here](http://pyopengl.sourceforge.net/documentation/installation.html).
    - PyOpenGL_accelerate seems to have installation problems on Windows. It is optional.
- Install pyautogui: 
  - Make sure you have installed pillow first.
  - Follow the Windows instructions [here](https://pyautogui.readthedocs.io/en/latest/install.html).

### Mac installation
- Install pillow:
  - Run `xcode-select --install` in a Terminal first.
  - Follow the Mac instructions [here](https://pillow.readthedocs.io/en/3.0.0/installation.html#os-x-installation).
- Install PyOpenGL and PyOpenGL_accelerate: instructions [here](http://pyopengl.sourceforge.net/documentation/installation.html).
- Install pyautogui: 
  - Make sure you have installed pillow first.
  - Follow the Mac instructions [here](https://pyautogui.readthedocs.io/en/latest/install.html).

### Linux installation
- Install pillow: instructions for Linux [here](https://pillow.readthedocs.io/en/3.0.0/installation.html#linux-installation).
- Install PyOpenGL and PyOpenGL_accelerate:
  - First use a package manager to install `python3-dev` (or `python3-devel`), and `freeglut` (or equivalent).
    - On Fedora, you might need to run `dnf install redhat-rpm-config` first.
  - Follow the instructions [here](http://pyopengl.sourceforge.net/documentation/installation.html).
- Install pyautogui: 
  - Make sure you have installed pillow first.
  - Follow the Linux instructions [here](https://pyautogui.readthedocs.io/en/latest/install.html).
    - The instructions refer to `python3-tk`, which may be called `python3-tkinter` instead; and `python3-dev`, which may be called `python3-devel` instead. 
    - If you get an Xlib error on the last step, type `xhost +` before you try to install it again. ([reference](https://ubuntuforums.org/showthread.php?t=2290602))

## Start

To use three, you need a game directory to work with. `gameDirTemplate` has a sample game directory layout with some useful materials. To start three, type `python3 three.py path/to/game/dir mapName`. `mapName` is relative to the `maps` folder in the game directory; if the map does not exist, it will be created. You can also specify a map number instead - this will look up names in `maps.txt` (starts at 1).

By default, three starts in Run Mode, which starts the game with the specified map. To start the map editor instead, use the `-edit` flag.

Try navigating to the root of this repository and typing `python3 three.py gameDirTemplate 1 -edit`. If a window appears with green and blue lines and some text at the bottom, it worked.

You should keep the terminal window that you used to start three open. It is used for messages and errors.

## HUD

On the screen you will see:
- A framerate count in the top left corner
- A status bar on the bottom (see below)
- Mini-axes in the bottom right corner. These show the direction you are currently looking, even when the real axes aren't visible. Red is X, green is Y, and blue is Z.

When you select an object some more indicators will appear:
- A green square, showing the origin of the object
- A green line, showing the forward vector of the object
- A pink line to the object's parent, if it exists
- Light-blue lines to the object's children, if any

### Status bar

By default, the status bar will show:
- The selection mode (Object/Face/Vertex) and the number of things selected
- Information about the selected object
  - For objects, the position (`Pos`), rotation (`Rot`), and dimensions (`Dim`) of the object
  - For faces, the material name, and its translation (`Shift`), rotation, and scale
  - For vertices, the position of the vertex
- The current material name (`Paint`)
- The current command being typed, if it is more than a single keystroke
- Occasionally additional instructions

When in adjust mode (see below), the status bar will show:
- A description of what is being adjusted
- The values of the X, Y, and Z axes. If in relative mode, these will be relative to the starting position; if in absolute mode, these will be absolute numbers.
- The two selected axes to adjust
- The grid size
- `Snap` if grid snapping is enabled, `Free` otherwise
- Whether axis lock is enabled

## Controls

### General
- `Esc` to cancel any operations
- `` ` `` to save
- Right click, then use the mouse and `WASDQE` keys to fly around. Use the mouse wheel to control fly speed.
- `nb` to create a New Box and enter translate-adjust mode to move it (see below)
- `np` to create a New Point and enter translate-adjust mode to move it. See the Scripting section for more information on Points.
- Left click to select objects; hold shift to select multiple.
- `mv` to switch to Vertex select mode, `mf` for Face select and `mo` for Object select mode (default)
- `a` to select none or All objects
- `Backspace` to delete objects
- `c` to duplicate ("Copy") selected objects and enter translate-adjust mode to move them (see below)
- `Enter` to edit the properties of selected objects using your default text editor. When you are finished editing properties and have saved the file, press `u` ("Update") with the same objects selected to update their properties. If nothing is selected world properties will be edited. See the Scripting section for more information on properties.
- `g` to enter translate ("Grab") adjust mode for the selected objects (see below)
- `r` to enter Rotate adjust mode
- `s Enter` to enter reSize adjust mode, which changes the dimensions of the selected object(s). Before pressing Enter you can type any of the letters `nsewtb` (North South East West Top Bottom). With these you can choose to resize in just one direction along an axis.
- `Shift-s Enter` to enter Scale adjust mode. You can use the same direction letters as in Resize.
- `o` to adjust the Origins of selected objects in adjust mode
- `t` to set the parent of selected objects ("Tie" them to a parent). The most recently selected object will become the parent for the rest. See the Scripting section for more information on parents and children.
- `Shift-t` to remove the parents for all of the selected objects
- `,` to select the parents of the selected objects. `Shift-,` to add to the existing selection.
- `.` to select the children of the selected objects. `Shift-.` to add to the existing selection.
 
### Mesh Editing

three is designed to work with only closed, "solid" meshes. This means that you can't delete faces or create a "hole" in the mesh. Using only the built-in editing tools it should be very difficult to create non-solid mesh, but if you do note that some of the mesh editing tools will not work properly with non-solid meshes.

- With the two vertices of an edge selected, `d` to Divide the edge with a new vertex
- With two vertices selected, `Shift-d` to merge the second with the first ("undivide")
- With two vertices selected that are on the same face but not the same edge, `e` to divide that face with an Edge connecting them
- With two vertices of an edge selected that divides two coplanar polygons, `Shift-e` to merge the polygons and remove the edge
- `h` to enter adjust mode to extrude the selected faces. If objects are selected, all faces will be extruded and the original object will be deleted afterwards ("Hollow").
- `k` with meshes selected to "clip" the selected meshes, using a plane to slice off part of them. Adjust mode is used to set a point on the clip plane, followed by the normal of the plane. The normal points in the direction of the half that is removed. 
- `Shift-k` to use the selected meshes to "carve" into all other meshes

### Materials
- `Shift-p path/to/texture Enter` to choose the current material. The texture must be in the the `materials` subdirectory of the game directory. Even if you are on Windows you must use `/` as a path separator and match the case of the file name. Textures can sometimes take a while to transfer to OpenGL, during which the editor will be unresponsive.
- `p` to "Paint" the current material on the selected faces or objects
- `Shift-p Enter` to reload the current material's texture. Everything with that material will be updated.
- `fg`, `fr`, or `fs` to enter translate, rotate, or scale adjust mode to align the face's material in 2 dimensions

### Adjust Mode

Adjust mode is used to translate, rotate, and scale objects. It has a completely different set of keyboard commands.

- Move the mouse to move, rotate, or scale objects
- `x` `y` and `z` to select the x, y, and z axes for adjusting. The mouse only has two axes so you can only be adjusting two at a time. The last two letters you type are the axes you are adjusting - if you type the same letter twice, you only adjust one axis.
- Left click or `Enter` to confirm and exit adjust mode
- `Esc` to cancel
- `[` and `]` to increase / decrease the grid size. The grid is different for translating, rotating, and scaling.
- `g` followed by a number and `Enter` to manually set the grid size
- `s` to toggle Snap to grid. The grid is relative, so if you are already off the grid you will continue to be off the grid, but you will still move in grid size increments.
- `a` to move to the nearest, Absolute grid point for the selected axes
- `o` to jump to the Origin
- A number, terminated by an `x` `y` or `z`, to set the value of a certain axis.
- `r` to toggle Relative / absolute coordinates when entering axis values. Relative coordinates are relative to the starting position. Absolute is relative to the origin.
- `l` to toggle Axis Lock. When this is enabled, adjustments are made using only horizontal movement of the mouse, and they change all axes at once.

## Scripting

Objects created in the editor correspond to objects that are added to the game world, represented by the `threelib.world.World` object. Most of the time these are Entities (`threelib.sim.base.Entity`), which represent objects in 3d space with a position and rotation. Entities can have a parent and children - when the parent moves, the children move along with it.

There are various tools availible in the editor to control the creation of Entities. Setting the parents and children of objects (using the `t` command and others, see above) will cause the same parent-child relationships to be set up in the game world.

There are 2 main types of objects in the editor: Meshes and Points. Points are normally invisible to the player, but through the parent-child system they can control other objects, and you can assign custom scripts to them. Meshes are automatically given a child RenderMesh object (`threelib.sim.graphics.RenderMesh`), which is a special entity that is drawn on the screen.

Through an object's properties (viewed by pressing `Enter` and updated with `u`, see above) you can control the behavior of Entities generated from the objects. A list of properties is below.

### Properties

#### For all types of objects

- `position`: The position of the object in 3d space
- `rotation`: The orientation of the object about the X, Y, and Z axes
- `name`: The name of the object. If you assign a constructor, this name will be available as a variable to all scripts.
- `script`: A script that will be run before the Entity is created
- `constructor`: If provided, this will be used to create the entity. This should be a expression that returns an Entity. If not provided, a default one may be used instead.

#### For mesh objects

- `visible`: Whether the RenderMesh should be drawn. This value can change.

There are some other properties but they are currently not implemented.

#### The camera

The camera is a special Entity in the game world - it points towards the view that is shown on the screen. You can create one by making a Point in the editor and giving it the name `cam`, optionally with extra scripts. By default, an Entity at the origin facing negative-X is used.

Note that if you set a custom `rotation` value for the camera, it will point the *opposite* direction of the green forward vector shown in the editor - it will be pointing backward.

