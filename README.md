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

To use three, you need a game directory to work with. Game directories contain all the data needed for a complete game, including maps, textures, materials, and scripts. A sample game directory with some useful materials has been included in the `gameDirTemplate` directory.

To start three, type `python3 three.py path/to/game/dir mapName`. `mapName` is relative to the `maps` folder in the game directory; if the map does not exist, it will be created. You can also specify a map number instead - this will look up names in `maps.txt` (starts at 1).

By default, three starts in Run Mode, which starts the game with the specified map. To start the map editor instead, use the `-edit` flag.

Try navigating to the root of this repository and typing `python3 three.py gameDirTemplate 1 -edit`. If a window appears with green and blue lines and some text at the bottom, it worked.

You should keep the terminal window that you used to start three open. It is used for messages and errors.


## More Information

The [wiki](https://github.com/vanjac/three/wiki) has information about how to use three. For example, see the [Editor Interface](https://github.com/vanjac/three/wiki/Editor-Interface) page for the user interface and keyboard shortcuts of the map editor, and the [Scripting](https://github.com/vanjac/three/wiki/Scripting) page for how to use Python for game scripts.

