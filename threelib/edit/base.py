__author__ = "vantjac"

from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

# for ast.literal_eval, used for parsing properties
import ast


class EditorObject:
    """
    An abstract class for objects that can be manipulated in the editor, and
    that tie to SimObjects in the World.
    """
    
    def __init__(self):
        self.name = ""
        self.children = [ ]
        self.parent = None
        self.selected = False
    
    def getName(self):
        """
        Return the name of the EditorObject as a string. Names have no meaning
        and are for organization only.
        """
        return self.name

    def setName(self, name):
        """
        Set the name of the EditorObject.
        """
        self.name = name
    
    def getType(self):
        """
        Return a string describing the EditorObject. Override this.
        """
        return "EditorObject"
    
    def getPosition(self):
        """
        Return a Vector. Override this.
        """
        pass
    
    def getRotation(self):
        """
        Return a Rotation. Override this.
        """
        pass
    
    def getBounds(self):
        """
        Return a tuple of 2 Vectors: (min_coordinates, max_coordinates). Bounds
        are relative to the object position. Override this.
        """
        pass

    def getCenter(self):
        """
        Calculate the center of the bounds of the object.
        """
        b1, b2 = self.getBounds()
        return (b1 + b2) / 2 + self.getPosition()

    def getDimensions(self):
        """
        Calculate the dimensions of the object based on the bounds, as a Vector.
        """
        b1, b2 = self.getBounds()
        return b2 - b1

    def setPosition(self, position):
        """
        Set the position. Override this.
        """
        pass

    def setRotation(self, rotation):
        """
        Set the rotation. Override this.
        """
        pass
    
    def applyRotation(self):
        """
        Apply the current rotation so that it becomes 0. Override this.
        """
        pass
    
    def scale(self, factor):
        """
        Apply a scale factor to the object. ``factor`` is a Vector. Override
        this.
        """
        pass

    def getMesh(self):
        """
        Return the object's mesh if it exists, or None. Override this.
        """
        return None

    def drawObject(self, graphicsTools):
        """
        Using the GraphicsTools object, draw this EditorObject at the origin
        with no rotation (but with scaling) -- it is the editor's responsibility
        to position and rotate it. Override this.
        """
        pass

    def drawSelectHull(self, color, graphicsTools):
        """
        Similar to ``drawObject()``, draw the select hull of the object in the
        specified color. This is the area on screen that the user can click to
        select the object. ``color`` is a tuple of (r, g, b). Override this.
        """
        pass

    def getProperties(self):
        """
        Get the user-editable properties of this object. Return a dictionary
        mapping strings to strings. If you override this, join the new
        properties list with ``super().getProperties()``.
        """
        properties = { "name": self.getName(),
                       "position": str(self.getPosition()),
                       "rotation": str(self.getRotation()),
                       }
        return properties

    def setProperties(self, properties):
        """
        Set the properties of this object. If you override this, send
        unrecognized properties to ``super().setProperties()``.
        """
        for key, value in properties.items():
            if key == "name":
                self.setName(value)
            if key == "position":
                self.setPosition(Vector.fromTuple(ast.literal_eval(value)))
            if key == "rotation":
                self.setRotation(Rotate.fromTuple(ast.literal_eval(value)))

    def getParent(self):
        """
        Return the EditorObject that has this object as a child. Set
        automatically.
        """
        return self.parent

    def setParent(self, parent):
        """
        Internal method, only called by other EditorObjects.
        """
        self.parent = parent

    def getChildren(self):
        """
        Return a list of other EditorObjects. Children are user-editable.
        """
        return self.children

    def addChild(self, child):
        """
        Add a child EditorObject.
        """
        child.removeFromParent()
        child.setParent(self)
        self.children.append(child)

    def removeChild(self, child):
        """
        Remove a child EditorObject.
        """
        child.setParent(None)
        self.children.remove(child)

    def removeFromParent(self):
        """
        Remove this object as a child from its parent. 
        """
        if self.parent != None:
            self.parent().removeChild(self)
    
    def isSelected(self):
        """
        This ``isSelected`` flag is set automatically.
        """
        return self.selected

    def setSelected(self, selected):
        """
        Called by the editor.
        """
        self.selected = selected

    def clone(self):
        """
        Clone this object. The new object will NOT have a parent or children.
        Don't override this to add functionality. Instead override
        ``addToClone``.
        """
        clone = EditorObject()
        self.addToClone(clone)
        return clone
    
    def addToClone(self, clone):
        """
        Internal method to add this objects properties to a newly created clone.
        If you override this, call super().addToClone(clone) first, then add
        your own properties. This implementation sets the name, position, and
        rotation of the object.
        """
        clone.setName(self.getName())
        clone.setPosition(self.getPosition())
        clone.setRotation(self.getRotation())
        
    def addToWorld(self, world):
        """
        Add a representation to the world.
        """
        pass


class WorldObject(EditorObject):
    
    def __init__(self):
        super().__init__()
    
    def getType(self):
        return "World"
    
    def getPosition(self):
        return Vector(0, 0, 0)
    
    def getRotation(self):
        return Rotate(0, 0, 0)
    
    def getBounds(self):
        return (Vector(0, 0, 0), Vector(0, 0, 0))

    def getMesh(self):
        return None
    
    def getProperties(self):
        properties = { "name": self.getName(),
                       }
        return properties

    def setProperties(self, properties):
        for key, value in properties.items():
            if key == "name":
                self.setName(value)
    
    def clone(self):
        clone = WorldObject()
        self.addToClone(clone)
        return clone
    
    def addToClone(self, clone):
        clone.setName(self.getName())
