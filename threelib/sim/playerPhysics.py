__author__ = "jacobvanthoog"

from threelib.vectorMath import Vector
from threelib import vectorMath
import threelib.sim.base


def pointOnFace(point, facePoints):
    # the algorithm is sort of based on this:
    # demonstrations.wolfram.com/AnEfficientTestForAPointToBeInAConvexPolygon/    
    
    # triangles are made from adjacent vertices and the point
    # all of them should be counterclockwise
    # if any aren't, the point is outside the polygon
    for i in range(0, len(facePoints)):
        triOrientation = orientation(facePoints[i - 1],
                                     facePoints[i],
                                     point)
        if triOrientation == 1:
            return False
    return True
    
def pointOnMeshFace(point, meshFace, reverse=False):
    vertices = meshFace.getVertices()
    numVertices = len(vertices)
    for i in range(0, numVertices):
        if not reverse:
            v1 = vertices[i - 1]
            v2 = vertices[i]
        else: #reverse
            v1 = vertices[numVertices - i - 1]
            v2 = vertices[numVertices - i - 2]
        
        triOrientation = orientation(v1.vertex.getPosition(),
                                     v2.vertex.getPosition(),
                                     point)
        if triOrientation == 1:
            return False
    return True
                    
def orientation(p, q, r):
    # for 2d vectors (Z coordinate is ignored)
    # return 0 for colinear, 1 for clockwise, 2 for counterclockwise
    # geeksforgeeks.org/convex-hull-set-1-jarviss-algorithm-or-wrapping
    val = (q.y - p.y) * (r.x - q.x) - \
          (q.x - p.x) * (r.y - q.y)

    if vectorMath.isclose(val, 0):
        return 0
    return 1 if val > 0 else 2


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
                        triOrientation = orientation(
                            nextVertex.getPosition(), vertex.getPosition(),
                            nextVertexCandidate.getPosition())
                        if triOrientation == 2:
                            nextVertexCandidate = vertex
                for vertex in verticesToRemove:
                    vertices.remove(vertex)
                
                if nextVertexCandidate == self.mesh.getVertices()[0]:
                    # reached beginning again
                    break
                nextVertex = nextVertexCandidate
        
        
    def isInBounds(self, point):
        """
        Check if the 2d vector (z coordinate ignored) is in the convex bounds
        created by this object. The point should be in absolute world
        coordinates.
        """
        
        translatedPoint = self._translatePointForConvexHull(point)
        return pointOnFace(translatedPoint, self.convexHullPoints)
        
    def nearestBoundsPoint(self, point, maxDistance=None):
        """
        Return the closest point on the convex 2d boundary of this mesh to the
        given point. If ``maxDistance`` is specified, ``None`` will be returned
        if no point is found closer than ``maxDistance``.
        """
        point = self._translatePointForConvexHull(point).setZ(0)
        
        #based on code from:
        #stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
        minDistance = -1
        minDistancePoint = None
        for i in range(0, len(self.convexHullPoints)):
            p1 = self.convexHullPoints[i - 1]
            p2 = self.convexHullPoints[i]
        
            l2 = (p1 - p2).magnitudeSquare()
            if l2 == 0.0:
                nearestPoint = p1
            else:
                t = max(0, min(1, (point - p1).dot(p2 - p1) / l2))
                nearestPoint = p1 + t * (p2 - p1)
            
            distance = (point - nearestPoint).magnitude()
            if minDistance == -1 or distance < minDistance:
                minDistance = distance
                minDistancePoint = nearestPoint
        
        if maxDistance == None:
            return self._translateConvexHullPointToAbsolute(minDistancePoint)
        elif minDistance < maxDistance:
            return self._translateConvexHullPointToAbsolute(minDistancePoint)
        else:
            return None
    
    
    def topPointAt(self, point):
        """
        Get the z value (height) and normal at the specified 2d point on the top
        of this mesh. Return a CollisionPoint with that data, or None if there
        is nothing at that point. Instead of relying on this method returning
        None, you should first check ``isInBounds``, which is more efficient.
        """
        point = self._translatePointForConvexHull(point)
        for face in self.topFaces:
            if pointOnMeshFace(point, face):
                normal = face.getNormal().rotate2(self.getRotation().z)
                plane = face.getPlane()
                # ax + by + cz + d = 0
                # z = -(ax + by + d) / c
                height = -(plane[0] * point.x + plane[1] * point.y + plane[3]) \
                    / plane[2] + self.getPosition().z
                return CollisionPoint(height, normal)
        return None
        
    def bottomPointAt(self, point):
        """
        Get the z value and normal at the specified 2d point on the bottom of
        this mesh. See ``topPointAt``.
        """
        point = self._translatePointForConvexHull(point)
        for face in self.bottomFaces:
            if pointOnMeshFace(point, face, reverse=True):
                normal = face.getNormal().rotate2(self.getRotation().z)
                plane = face.getPlane()
                # ax + by + cz + d = 0
                # z = -(ax + by + d) / c
                height = -(plane[0] * point.x + plane[1] * point.y + plane[3]) \
                    / plane[2] + self.getPosition().z
                return CollisionPoint(height, normal)
        return None
        
    
    def _translatePointForConvexHull(self, point):
        # translate the point to factor in the translation and Z rotation of the
        # convex hull
        return (point - self.getPosition()).rotate2(-(self.getRotation().z))
        
    def _translateConvexHullPointToAbsolute(self, point):
        return point.rotate2(self.getRotation().z) + self.getPosition()
     
        
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


class CollisionPoint:

    def __init__(self, height, normal):
        self.height = height
        self.normal = normal

