__author__ = "jacobvanthoog"


class AppInstance:
    """
    Represents an application window. Has utilities for getting information
    about the application state and inputs.
    """

    def getFps(self):
        """
        Get the average number of frames per second over a short timespan. This
        may be 0 initially.
        """
        return None

    def windowWidth(self):
        """
        Get the width of the window in pixels.
        """
        return None

    def windowHeight(self):
        """
        Get the height of the window in pixels.
        """
        return None

    def getAspect(self):
        """
        Get the aspect ratio of the window, as a ratio of width to height.
        """
        return None

    def getFOV(self):
        """
        Get the field of view of the perspective projection.
        """
        return None

    def getNearClip(self):
        """
        Get the near clipping plane of the perspective projection.
        """
        return None

    def getFarClip(self):
        """
        Get the far clipping plane of the perspective projection.
        """
        return None

    def buttonPressed(self, button=0):
        """
        Check if the specified mouse button is pressed. 0 is left, 1 is middle,
        2 is right.
        """
        return False

    def shiftPressed(self):
        """
        Check if a shift key is being held down.
        """
        return False

    def ctrlPressed(self):
        """
        Check if a control key is being held down.
        """
        return False

    def altPressed(self):
        """
        Check if an alt key is being held down.
        """
        return False

    def mouseX(self):
        """
        Get the current x position of the mouse relative to the window.
        """
        return None

    def mouseY(self):
        """
        Get the current y position of the mouse relative to the window.
        """
        return None

    def lockMouse(self):
        """
        Hide the mouse and allow it to move continuously in all directions. When
        the mouse is locked, its absolute position should be ignored, and only
        the mouse movement should be used.
        """
        pass

    def unlockMouse(self):
        """
        Unlock the mouse and show it at the position it was at when it was
        locked.
        """
        pass


class AppInterface:
    """
    An interface for an app that can be used with any AppInstance.
    """

    def setAppInstance(self, instance):
        """
        Set the AppInstance that is being used to show this AppInterface.
        """
        pass

    def init(self):
        """
        Called by the AppInstance once the drawing surface is ready.
        """
        pass

    def draw(self):
        """
        Called by the AppInstance every frame before the screen is refreshed.
        """
        pass

    def keyPressed(self, key):
        """
        Called by the AppInstance when a key is pressed.
        """
        pass

    def keyReleased(self, key):
        """
        Called by the AppInstance when a key is released.
        """
        pass

    def mousePressed(self, button, mouseX, mouseY):
        """
        Called by the AppInstance when a mouse button is pressed. 0 is left,
        1 is middle, 2 is right. 3 - 6 are special "buttons" when the scroll
        wheel moves up, down, left, or right.
        """
        pass

    def mouseReleased(self, button, mouseX, mouseY):
        """
        Called by the AppInstance when a mouse button is released.
        """
        pass

    def mouseMoved(self, mouseX, mouseY, pmouseX, pmouseY):
        """
        Called by the AppInstance when the mouse is moved. Mouse positions are
        relative to the window. ``pmouseX`` and ``pmouseY`` are the mouse
        positions from the last time this method was called. The exception to
        this rule is if the mouse is locked, but in any case the difference
        between the previous and current positions can always be used to
        determine mouse movement.
        """
        pass

