__author__ = "jacobvanthoog"

from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib.mesh import *
import threelib.files
import threelib.script

# for ast.literal_eval, used for parsing properties
import ast


# utilities for parsing properties
def stringToTripleTuple(s):
    return ast.literal_eval(s)
    
def stringToBoolean(s):
    s = s.lower().strip()
    return not (s == 'false' or s == '0' or s == '')

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
    
    def __repr__(self):
        if name == "":
            return "[Unnamed object]"
        else:
            return self.getName()
    
    def getName(self):
        """
        Return the name of the EditorObject as a string. Names usually have no
        meaning and are for organization only, but for ScriptPointObjects they
        are the variable name of the Entity.
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
        
    def getTranslatedBounds(self):
        """
        Similar to ``getBounds``, but bounds are in absolute coordinates and not
        relative to object position.
        """
        bounds = self.getBounds()
        pos = self.getPosition()
        return (bounds[0] + pos, bounds[1] + pos)

    def getCenter(self):
        """
        Calculate the center of the bounds of the object, in absolute
        coordinates.
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
                self.setPosition(Vector.fromTuple(stringToTripleTuple(value)))
            if key == "rotation":
                self.setRotation(Rotate.fromDegreesTuple(
                    stringToTripleTuple(value)))

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
            self.parent.removeChild(self)
    
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
        Override this.
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
        Add a representation to the world. Return a SimObject that represents
        this EditorObject.
        """
        pass


class WorldObject(EditorObject):
    
    def __init__(self):
        super().__init__()
        
        # properties
        self.script = "\n\n"
        self.externalScripts = ['default'] # list of script names
    
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
        
    def addToWorld(self, world):
        for scriptName in self.externalScripts:
            path = threelib.files.getScript(scriptName)
            if path == None:
                print("Script file", scriptName, "not found!")
                continue
            script = threelib.files.loadScript(path)
            threelib.script.runScript(script)
        
        threelib.script.runScript(self.script)
    
    def getProperties(self):
        properties = { "name": self.getName(),
                       "script": self.script,
                       "externalScripts": ','.join(self.externalScripts) }
        return properties

    def setProperties(self, properties):
        for key, value in properties.items():
            if key == "name":
                self.setName(value)
            if key == "script":
                self.script = value
            if key == "externalScripts":
                self.externalScripts = value.split(',')
    
    def clone(self):
        clone = WorldObject()
        self.addToClone(clone)
        return clone
    
    def addToClone(self, clone):
        clone.setName(self.getName())
        

class PointObject(EditorObject):
    
    def __init__(self):
        EditorObject.__init__(self)
        self.position = Vector(0, 0, 0)
        self.rotation = Rotate(0, 0, 0)
        self.baseRotation = Rotate(0, 0, 0)
        
    def getType(self):
        return "Point"

    def getPosition(self):
        return self.position
    
    def getRotation(self):
        return self.rotation
    
    def getBounds(self):
        return (Vector(0, 0, 0), Vector(0, 0, 0))

    def setPosition(self, position):
        self.position = position

    def setRotation(self, rotation):
        self.rotation = rotation

    def applyRotation(self):
        self.baseRotation.rotate(self.rotation)
        self.rotation = Rotate(0, 0, 0)

    def scale(self, factor):
        pass

    def getMesh(self):
        return None
    
    def drawObject(self, graphicsTools):
        if self.isSelected():
            graphicsTools.drawPoint(Vector(0,0,0), (0.0, 1.0, 1.0), 12)
        else:
            graphicsTools.drawPoint(Vector(0,0,0), (1.0, 1.0, 1.0), 12)
    
    def drawSelectHull(self, color, graphicsTools):
        graphicsTools.drawPoint(Vector(0,0,0), color, 10)
    
    def getProperties(self):
        return super().getProperties()

    def setProperties(self, properties):
        super().setProperties(properties)

    def clone(self):
        clone = PointObject()
        self.addToClone(clone)
        return clone
    
    def addToClone(self, clone):
        super().addToClone(clone)
        clone.setRotation(self.baseRotation)
        clone.applyRotation()
        clone.setRotation(self.rotation)


class MeshObject(EditorObject):

    # starts as a cube
    # scale is the size of the cube / 2
    def __init__(self, scale=1):
        EditorObject.__init__(self)
        self.position = Vector(0, 0, 0)
        self.rotation = Rotate(0, 0, 0)
        self.mesh = Mesh()
        a = self.mesh.addVertex(MeshVertex(Vector(-scale, -scale, -scale)))
        b = self.mesh.addVertex(MeshVertex(Vector( scale, -scale, -scale)))
        c = self.mesh.addVertex(MeshVertex(Vector(-scale,  scale, -scale)))
        d = self.mesh.addVertex(MeshVertex(Vector( scale,  scale, -scale)))
        e = self.mesh.addVertex(MeshVertex(Vector(-scale, -scale,  scale)))
        f = self.mesh.addVertex(MeshVertex(Vector( scale, -scale,  scale)))
        g = self.mesh.addVertex(MeshVertex(Vector(-scale,  scale,  scale)))
        h = self.mesh.addVertex(MeshVertex(Vector( scale,  scale,  scale)))
        top = self.mesh.addFace(MeshFace())
        front = self.mesh.addFace(MeshFace())
        right = self.mesh.addFace(MeshFace())
        bottom = self.mesh.addFace(MeshFace())
        back = self.mesh.addFace(MeshFace())
        left = self.mesh.addFace(MeshFace())
        top.addVertex(e).addVertex(f).addVertex(h).addVertex(g)
        front.addVertex(f).addVertex(b).addVertex(d).addVertex(h)
        right.addVertex(g).addVertex(h).addVertex(d).addVertex(c)
        bottom.addVertex(a).addVertex(c).addVertex(d).addVertex(b)
        back.addVertex(e).addVertex(g).addVertex(c).addVertex(a)
        left.addVertex(f).addVertex(e).addVertex(a).addVertex(b)
        
    def getType(self):
        return "Mesh"

    def getPosition(self):
        return self.position
    
    def getRotation(self):
        return self.rotation
    
    def getBounds(self):
        if len(self.mesh.getVertices()) == 0:
            return (Vector(0, 0, 0), Vector(0, 0, 0))
        firstVertexPos = self.mesh.getVertices()[0].getPosition()
        lowX = firstVertexPos.x
        lowY = firstVertexPos.y
        lowZ = firstVertexPos.z
        highX = firstVertexPos.x
        highY = firstVertexPos.y
        highZ = firstVertexPos.z
        for v in self.mesh.getVertices():
            pos = v.getPosition()
            if pos.x < lowX:
                lowX = pos.x
            if pos.x > highX:
                highX = pos.x
            if pos.y < lowY:
                lowY = pos.y
            if pos.y > highY:
                highY = pos.y
            if pos.z < lowZ:
                lowZ = pos.z
            if pos.z > highZ:
                highZ = pos.z
        return ( Vector(lowX, lowY, lowZ), Vector(highX, highY, highZ) )

    def setPosition(self, position):
        self.position = position

    def setRotation(self, rotation):
        self.rotation = rotation

    def applyRotation(self):
        for v in self.mesh.getVertices():
            v.setPosition(v.getPosition().rotate(self.rotation))
        self.rotation = Rotate(0, 0, 0)

    def scale(self, factor):
        for v in self.mesh.getVertices():
            v.setPosition(v.getPosition() * factor)

    def getMesh(self):
        return self.mesh

    def setMesh(self, mesh):
        self.mesh = mesh
    
    def drawObject(self, graphicsTools):
        graphicsTools.drawMesh(self.mesh)
    
    def drawSelectHull(self, color, graphicsTools):
        graphicsTools.drawMeshSelectHull(self.mesh, color)
    
    def getProperties(self):
        return super().getProperties()

    def setProperties(self, properties):
        super().setProperties(properties)

    def clone(self):
        clone = MeshObject()
        self.addToClone(clone)
        return clone
    
    def addToClone(self, clone):
        super().addToClone(clone)
        clone.setMesh(self.mesh.clone())

