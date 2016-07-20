__author__ = "vantjac"

from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate

# for ast.literal_eval, used for parsing properties
import ast

# abstract class
class EditorObject:
    
    def __init__(self):
        self.name = ""
        self.children = [ ]
        self.parent = None
        self.selected = False

    # return a string
    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    # string describing the EditorObject
    def getType(self):
        pass

    # return a Vector
    def getPosition(self):
        pass

    # return a Rotation
    def getRotation(self):
        pass

    # return a tuple of 2 vectors (minCoords, maxCoords). Bounds are relative to
    # the object position
    def getBounds(self):
        pass

    def getCenter(self):
        b1, b2 = self.getBounds()
        return (b1 + b2) / 2 + self.getPosition()

    def getDimensions(self):
        b1, b2 = self.getBounds()
        return b2 - b1

    def setPosition(self, position):
        pass

    def setRotation(self, rotation):
        pass

    # apply the current rotation so it becomes 0
    def applyRotation(self):
        pass

    # factor is a vector
    def scale(self, factor):
        pass

    def getMesh(self):
        pass

    # Draw the object with the GraphicsTools.
    # Draw it at the origin with no rotation (but with scaling) -- it is the
    # editor's responsibility to position and rotate
    # it.
    def drawObject(self, graphicsTools):
        pass

    # color is a tuple of (r, g, b). Draw with OpenGL.
    def drawSelectHull(self, color, graphicsTools):
        pass

    # a dictionary mapping strings to strings
    def getProperties(self):
        properties = { "name": self.getName(),
                       "position": str(self.getPosition()),
                       "rotation": str(self.getRotation()),
                       }
        return properties

    def setProperties(self, properties):
        for key, value in properties.items():
            if key == "name":
                self.setName(value)
            if key == "position":
                self.setPosition(Vector.fromTuple(ast.literal_eval(value)))
            if key == "rotation":
                self.setRotation(Rotate.fromTuple(ast.literal_eval(value)))

    # return another EditorObject
    def getParent(self):
        return self.parent

    # should only be called by other EditorObjects
    def setParent(self, parent):
        self.parent = parent

    # return a list of EditorObjects
    def getChildren(self):
        return self.children

    def addChild(self, child):
        child.removeFromParent()
        child.setParent(self)
        self.children.append(child)

    def removeChild(self, child):
        child.setParent(None)
        self.children.remove(child)

    def removeFromParent(self):
        if self.parent != None:
            self.parent().removeChild(self)
    
    def isSelected(self):
        return self.selected

    def setSelected(self, selected):
        self.selected = selected

    # clone this object
    # the new object will NOT have any parent or children.
    def clone(self):
        clone = EditorObject()
        self.addToClone(clone)
        return clone
        
    # internal method to add this objects properties to a newly created clone
    # extending classes should call super().addToClone(clone) first
    def addToClone(self, clone):
        clone.setName(self.getName())
        clone.setPosition(self.getPosition())
        clone.setRotation(self.getRotation())


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
