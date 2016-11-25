__author__ = "jacobvanthoog"

from threelib.sim.base import Simulator
from threelib.sim.base import Entity
import threelib.script
from threelib.mesh import *

class World:
    """
    The game world.
    """
    def __init__(self):
        self.simulator = None

        self.camera = None # special Entity

        self.materials = [ ] # list of MaterialReference's
        self.addedMaterials = [ ]
        self.removedMaterials = [ ]
        self.updatedMaterials = [ ]

        self.renderMeshes = [ ]
        self.rayCollisionMeshes = [ ]
        self.collisionMeshes = [ ]

        self.renderMeshSubdivideSize = 144

        self.directionalLights = [ ] # list of Lights
        self.positionalLights = [ ]
        self.spotLights = [ ]

        self.buttonInputs = { }
        self.axisInputs = { }

        self.rayCollisionRequests = [ ]

    def onLoad(self):
        """
        Internal method. Called when the world is first loaded.
        """
        for mat in self.materials:
            self.addedMaterials.append(mat)
            mat.setLoaded(False)

    def addMaterial(self, materialReference):
        """
        Add a material to the world.
        """
        self.materials.append(materialReference)
        self.addedMaterials.append(materialReference)

    def removeMaterialReference(self, material):
        """
        Remove a reference from the given material. If the material now has no
        references, it is removed from the world.
        """
        material.removeReference()

        if material.hasNoReferences():
            self.removeMaterial(material)
            print("Removing unused material", material.getName())

    def removeMaterial(self, material):
        """
        Remove a material from the world.
        """
        self.materials.remove(material)
        self.removedMaterials.append(material)

    def updateMaterial(self, materialReference):
        """
        Update an existing material (add it to the list of materials to update).
        """
        self.updatedMaterials.append(materialReference)

    def removeUnusedMaterials(self):
        """
        Scan through the list of materials and remove any that have no
        references.
        """
        materialsToRemove = [ ]
        for material in self.materials:
            if material.hasNoReferences():
                materialsToRemove.append(material)
        for material in materialsToRemove:
            self.removeMaterial(material)
            print("Removing unused material", material.getName())


    def getAddedMaterials(self):
        """
        Get the materials that have been added since the last check.
        """
        added = self.addedMaterials
        self.addedMaterials = [ ]
        return added

    def getUpdatedMaterials(self):
        """
        Get the materials that have been added to the update list since the last
        check.
        """
        updated = self.updatedMaterials
        self.updatedMaterials = [ ]
        return updated

    def getRemovedMaterials(self):
        """
        Get the materials that have been removed since the last check.
        """
        removed = self.removedMaterials
        self.removedMaterials = [ ]
        return removed

    def findMaterial(self, name):
        """
        Find a material in the world with the given name. Return None if not
        found.
        """
        for matRef in self.materials:
            if matRef.getName() == name:
                return matRef

        return None

    # ray collision

    def getFaceAtRay(self, callback, start, direction,
                     nearClip=None, farClip=None):
        """
        Find the first enabled RayCollisionMesh that the ray at the given
        starting point in the given direction, hits. nearClip and farClip
        are the minimum and maximum distances the object can be at. By default,
        the camera near-clip and far-clip is used. The callback function will
        be called when a RayCollisionMesh is found, or if no collision occurs.
        It should take 2 arguments - the RayCollisionMesh and the MeshFace, or
        None for both.
        """
        self.rayCollisionRequests.append(
            RayCollisionRequest(RayCollisionRequest.GET_FACE, callback,
                                start, direction, nearClip, farClip) )

    def getDepthAtRay(self, callback, start, direction,
                     nearClip=None, farClip=None):
        """
        See ``getFaceAtRay``. Callback function should take 1 argument - the
        distance from the start point to the collision point, or None.
        """
        self.rayCollisionRequests.append(
            RayCollisionRequest(RayCollisionRequest.GET_DEPTH, callback,
                                start, direction, nearClip, farClip) )

    def getFaceDepthAtRay(self, callback, start, direction,
                     nearClip=None, farClip=None):
        """
        See ``getFaceAtRay``. Callback function should take 3 argument - the
        RayCollisionMesh, the MeshFace, and the distance from the start point to
        the collision point, or None for all.
        """
        self.rayCollisionRequests.append(
            RayCollisionRequest(RayCollisionRequest.GET_FACE_DEPTH, callback,
                                start, direction, nearClip, farClip) )

    # ray collision requests to be accessed by the game runner AppInterface

    def nextRayCollisionRequest(self):
        """
        Get the next pending ray collision request and remove it from the list.
        """
        return self.rayCollisionRequests.pop(0)

    def hasRayCollisionRequest(self):
        """
        Internal method: check if there are any pending ray collision requests.
        """
        return len(self.rayCollisionRequests) > 0


class Resource:

    def __init__(self):
        self.references = 0

    def numReferences(self):
        return self.references

    def addReference(self):
        self.references += 1

    def removeReference(self):
        self.references -= 1

    def hasNoReferences(self):
        return self.references == 0


class RayCollisionRequest:

    GET_FACE = "face"
    GET_DEPTH = "depth"
    GET_FACE_DEPTH = "face-depth"

    def __init__(self, mode, callback, start, direction, nearClip, farClip):
        self.mode = mode
        self.callback = callback
        self.start = start
        self.direction = direction
        self.nearClip = nearClip
        self.farClip = farClip


def buildWorld(editorState):
    threelib.script.runScript("from threelib.vectorMath import *")
    threelib.script.runScript("from threelib.mesh import *")
    threelib.script.runScript("from threelib.sim.base import *")
    threelib.script.runScript("from threelib.sim.graphics import *")
    threelib.script.runScript("from threelib.sim.input import *")
    threelib.script.runScript("from threelib.sim.lighting import *")
    threelib.script.runScript("from threelib.sim.playerPhysics import *")
    threelib.script.runScript("from threelib.sim.tools.firstPerson import *")
    threelib.script.runScript(
        "from threelib.sim.tools.firstPersonDebug import *")

    threelib.script.setVariableValue("world", editorState.world)

    world = editorState.world
    world.simulator = Simulator()

    editorState.worldObject.addToWorld(world)

    objectEntities = { }

    for o in editorState.objects:
        objectEntities[o] = o.addToWorld(world)

    # add children
    for editorObject, entity in objectEntities.items():
        if entity is not None:
            for child in editorObject.getChildren():
                try:
                    childEntity = objectEntities[child]
                except KeyError:
                    childEntity = None
                if childEntity is None:
                    print("WARNING: Cannot add", child, "as a child of",
                          editorObject, "- No corresponding entity")
                else:
                    entity.addChild(childEntity)

    if world.camera is None:
        world.camera = Entity()
        world.simulator.addObject(world.camera)

    if len(world.directionalLights) > 0 or \
       len(world.positionalLights) > 0 or \
       len(world.spotLights) > 0:
        # subdivide renderMesh faces
        print("Subdividing faces...")
        for renderMesh in world.renderMeshes:
            mesh = renderMesh.getMesh().clone()
            renderMesh.setMesh(mesh)
            faces = list(mesh.getFaces()) # prevent problems as new faces are added
            for face in faces:
                subdivideMeshFace(mesh, face, world.renderMeshSubdivideSize)

def subdivideMeshFace(mesh, face, maxSize):
    area = face.getArea()
    if area > maxSize:
        if len(face.getVertices()) > 3:
            # split into triangles
            newFaces = [ ]
            v1 = face.getVertices()[0]
            for i in range(1, len(face.getVertices()) - 1):
                v2 = face.getVertices()[i]
                v3 = face.getVertices()[i + 1]
                newFace = MeshFace().addVertex(v1.vertex, v1.textureVertex)\
                                    .addVertex(v2.vertex, v2.textureVertex)\
                                    .addVertex(v3.vertex, v3.textureVertex)
                newFaces.append(newFace)

            for newFace in newFaces:
                newFace.copyMaterialInfo(face)
                mesh.addFace(newFace)
            mesh.removeFace(face)

            for newFace in newFaces:
                subdivideMeshFace(mesh, newFace, maxSize)
        else:
            # find the longest edge...
            v1 = face.getVertices()[0]
            v2 = face.getVertices()[1]
            v3 = face.getVertices()[2]
            dist1 = v2.vertex.getPosition().distanceTo(v3.vertex.getPosition())
            dist2 = v1.vertex.getPosition().distanceTo(v3.vertex.getPosition())
            dist3 = v1.vertex.getPosition().distanceTo(v2.vertex.getPosition())

            # divide the face along the longest edge
            newFaces = [ ]
            if dist1 >= dist2 and dist1 >= dist3:
                midpoint = v2.vertex.getPosition().lerp(
                    v3.vertex.getPosition(), .5)
                v4 = mesh.addVertex(MeshVertex(midpoint))
                newFace = MeshFace().addVertex(v1.vertex, v1.textureVertex)\
                                    .addVertex(v2.vertex, v2.textureVertex)\
                                    .addVertex(v4)
                newFaces.append(newFace)
                newFace = MeshFace().addVertex(v1.vertex, v1.textureVertex)\
                                    .addVertex(v4)\
                                    .addVertex(v3.vertex, v3.textureVertex)
                newFaces.append(newFace)
            elif dist2 >= dist1 and dist2 >= dist3:
                midpoint = v1.vertex.getPosition().lerp(
                    v3.vertex.getPosition(), .5)
                v4 = mesh.addVertex(MeshVertex(midpoint))
                newFace = MeshFace().addVertex(v1.vertex, v1.textureVertex)\
                                    .addVertex(v2.vertex, v2.textureVertex)\
                                    .addVertex(v4)
                newFaces.append(newFace)
                newFace = MeshFace().addVertex(v4)\
                                    .addVertex(v2.vertex, v2.textureVertex)\
                                    .addVertex(v3.vertex, v3.textureVertex)
                newFaces.append(newFace)
            else:
                midpoint = v1.vertex.getPosition().lerp(
                    v2.vertex.getPosition(), .5)
                v4 = mesh.addVertex(MeshVertex(midpoint))
                newFace = MeshFace().addVertex(v1.vertex, v1.textureVertex)\
                                    .addVertex(v4)\
                                    .addVertex(v3.vertex, v3.textureVertex)
                newFaces.append(newFace)
                newFace = MeshFace().addVertex(v4)\
                                    .addVertex(v2.vertex, v2.textureVertex)\
                                    .addVertex(v3.vertex, v3.textureVertex)
                newFaces.append(newFace)

            for newFace in newFaces:
                newFace.copyMaterialInfo(face)
                mesh.addFace(newFace)
            mesh.removeFace(face)

            for newFace in newFaces:
                subdivideMeshFace(mesh, newFace, maxSize)

