__author__ = "jacobvanthoog"

from threelib.vectorMath import Vector
from threelib import vectorMath
import threelib.sim.base

class CollisionMesh(threelib.sim.base.Entity):
    """
    A mesh that the player can walk on or collide with
    """
    
    def __init__(self, mesh):
        super().__init__()
        self.mesh = mesh
        self.enabled = True
        self.solid = True
        self.wallCollideAction = None
        self.floorStartTouchAction = None
        self.floorEndTouchAction = None
        self.ceilingCollideAction = None
        
        # Info about the hull of the object
        # This information assumes the object is at the origin, with a Z
        # rotation of 0. However, it DOES factor in the X and Y rotations.
        # So the object can move and rotate around the Z axis without having to
        # regenerate the hull, but as soon as it rotates any other way it will
        # have to recalculate.
        
        # a series of 2d vectors in a counterclockwise order that describe the
        # 2d convex hull of the object on the XY plane
        self.convexHullPoints = [ ]
        
        # lists of MeshFaces
        self.topFaces = [ ]
        self.bottomFaces = [ ]
        
        self._generateHull()
        
    def _generateHull(self):
        print("Generate hull")
        # TODO: These algorithms ignore the X and Y rotation of the object!
        
        # split mesh faces into "top" and "bottom" based on normal
        for face in self.mesh.getFaces():
            normal = face.getNormal()
            if normal != None:
                normalZ = normal.z
                if vectorMath.isclose(normalZ, 0):
                    pass # not top or bottom
                elif normalZ > 0:
                    self.topFaces.append(face)
                else:
                    self.bottomFaces.append(face)
        print(len(self.topFaces), "top faces")
        print(len(self.bottomFaces), "bottom faces")
    
        # find the 2d convex hull with Jarvis's algorithm
        # geeksforgeeks.org/convex-hull-set-1-jarviss-algorithm-or-wrapping
        
        self.convexHullPoints = [ ]
        if len(self.mesh.getVertices()) > 0:
            vertices = list(self.mesh.getVertices())
            nextVertex = vertices[0]
            
            while len(vertices) != 0:
                vertices.remove(nextVertex)
                self.convexHullPoints.append(nextVertex.getPosition().setZ(0))
                
                if len(vertices) == 0:
                    break
                
                verticesToRemove = [ ]
                if nextVertex != self.mesh.getVertices()[0]:
                    # to potentially complete the polygon
                    nextVertexCandidate = self.mesh.getVertices()[0]
                else:
                    nextVertexCandidate = None
                for vertex in vertices:
                    pos = vertex.getPosition().setZ(0)
                    
                    if vertex.getPosition().setZ(0) \
                            .isClose(nextVertex.getPosition().setZ(0)):
                        verticesToRemove.append(vertex)
                    elif nextVertexCandidate == None:
                        nextVertexCandidate = vertex
                    else:
                        # find the 2d orientation of the vectors
                        orientation = self._orientation(
                            nextVertex.getPosition(), vertex.getPosition(),
                            nextVertexCandidate.getPosition())
                        if orientation == 2:
                            nextVertexCandidate = vertex
                for vertex in verticesToRemove:
                    vertices.remove(vertex)
                
                if nextVertexCandidate == self.mesh.getVertices()[0]:
                    # reached beginning again
                    break
                nextVertex = nextVertexCandidate
        
        print("Convex hull points:", self.convexHullPoints)
        
        
    def isInBounds(self, point):
        """
        Check if the 2d vector (z coordinate ignored) is in the convex bounds
        created by this object. The point should be in absolute world
        coordinates.
        """
        # the algorithm is sort of based on this:
        # demonstrations.wolfram.com/AnEfficientTestForAPointToBeInAConvexPolygon/
    
        # first translate all the points of the convex hull, to factor in the
        # translation and Z rotation of this object
        
        point = self._translatePointForConvexHull(point)
        return self._pointOnFace(point, self.convexHullPoints)
        
    
    def topNormalAt(self, point):
        """
        Get the normal at the specified 2d point on the top of this mesh. Return
        None if there is nothing at that point. Instead of relying on this
        method returning None, you should first check ``isInBounds``, which is
        more efficient.
        """
        point = self._translatePointForConvexHull(point)
        for face in self.topFaces:
            if self._pointOnMeshFace(point, face):
                return face.getNormal().rotate2(self.getRotation().z)
        return None
        
    def _translatePointForConvexHull(self, point):
        # translate the point to factor in the translation and Z rotation of the
        # convex hull
        return (point - self.getPosition()).rotate2(-(self.getRotation().z))
    
    def _pointOnFace(self, point, facePoints):
        # triangles are made from adjacent vertices and the point
        # all of them should be counterclockwise
        # if any aren't, the point is outside the polygon
        for i in range(0, len(facePoints)):
            orientation = self._orientation(facePoints[i - 1],
                                            facePoints[i],
                                            point)
            if orientation == 1:
                return False
        return True
        
    def _pointOnMeshFace(self, point, meshFace):
        vertices = meshFace.getVertices()
        for i in range(0, len(vertices)):
            orientation = self._orientation(
                vertices[i - 1].vertex.getPosition(),
                vertices[i].vertex.getPosition(),
                point)
            if orientation == 1:
                return False
        return True
                        
    def _orientation(self, p, q, r):
        # for 2d vectors (Z coordinate is ignored)
        # return 0 for colinear, 1 for clockwise, 2 for counterclockwise
        # geeksforgeeks.org/convex-hull-set-1-jarviss-algorithm-or-wrapping
        val = (q.y - p.y) * (r.x - q.x) - \
              (q.x - p.x) * (r.y - q.y)
 
        if vectorMath.isclose(val, 0):
            return 0
        return 1 if val > 0 else 2
        
        
    def getMesh(self):
        """
        The collision mesh.
        """
        return self.mesh
        
    def setMesh(self, mesh):
        """
        Set the mesh. No effect until update().
        """
        def do(toUpdateList):
            self.mesh = mesh
        self.actions.addAction(do)

    def isEnabled(self):
        return self.enabled
        
    def setEnabled(self, enabled):
        def do(toUpdateList):
            self.enabled = enabled
        self.actions.addAction(do)
        
    def isSolid(self):
        return self.solid
    
    def setSolid(self, solid):
        def do(toUpdateList):
            self.solid = solid
        self.actions.addAction(do)

    def getWallCollideAction(self):
        return self.wallCollideAction
    
    def setWallCollideAction(self, action):
        def do(toUpdateList):
            self.wallCollideAction = action
        self.actions.addAction(do)
        
    def getFloorStartTouchAction(self):
        return self.floorStartTouchAction
    
    def setFloorStartTouchAction(self, action):
        def do(toUpdateList):
            self.floorStartTouchAction = action
        self.actions.addAction(do)
        
    def getFloorEndTouchAction(self):
        return self.floorEndTouchAction
    
    def setFloorEndTouchAction(self, action):
        def do(toUpdateList):
            self.floorEndTouchAction = action
        self.actions.addAction(do)
        
    def getCeilingCollideAction(self):
        return self.ceilingCollideAction
    
    def setCeilingCollideAction(self, action):
        def do(toUpdateList):
            self.ceilingCollideAction = action
        self.actions.addAction(do)

