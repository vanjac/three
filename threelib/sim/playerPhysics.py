__author__ = "jacobvanthoog"

import math
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
        self.unrotatedMesh = mesh
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

    def rotate(self, rotate, moveChildren=True):
        super().rotate(rotate, moveChildren)

        if not rotate.setZ(0).isCloseToZero():
            def do(toUpdateList):
                self._generateHull()
            self.actions.addAction(do)

    def _generateHull(self):
        # rotate mesh with X/Y rotation only
        self.mesh = self.unrotatedMesh.clone()
        meshRotation = self.getRotation().setZ(0)
        for vertex in self.mesh.getVertices():
            vertex.setPosition(vertex.getPosition().rotate(meshRotation))

        # split mesh faces into "top" and "bottom" based on normal
        self.topFaces = [ ]
        self.bottomFaces = [ ]
        for face in self.mesh.getFaces():
            normal = face.getNormal()
            if normal is not None:
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

            # set nextVertex to the leftmost vertex
            firstVertex = vertices[0]
            for vertex in vertices:
                if vertex.getPosition().x < firstVertex.getPosition().x:
                    firstVertex = vertex
            nextVertex = firstVertex

            while len(vertices) != 0:
                vertices.remove(nextVertex)
                self.convexHullPoints.append(nextVertex.getPosition().setZ(0))

                if len(vertices) == 0:
                    break

                if nextVertex != firstVertex:
                    # to potentially complete the polygon
                    nextVertexCandidate = firstVertex
                else:
                    nextVertexCandidate = None

                verticesToRemove = [ ]
                for vertex in vertices:
                    pos = vertex.getPosition().setZ(0)

                    if vertex.getPosition().setZ(0) \
                            .isClose(nextVertex.getPosition().setZ(0)):
                        verticesToRemove.append(vertex)
                    elif nextVertexCandidate is None:
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

                if nextVertexCandidate == firstVertex:
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

        if maxDistance is None:
            return self._translateConvexHullPointToAbsolute(minDistancePoint)
        elif minDistance < maxDistance:
            return self._translateConvexHullPointToAbsolute(minDistancePoint)
        else:
            return None

    def nearestBoundsNormal(self, point):
        """
        Return the 2d normal of the nearest point on the convex 2d boundary of
        this mesh to the given point.
        """
        point = self._translatePointForConvexHull(point).setZ(0)

        # copied / modified from nearestBoundsPoint
        minDistance = -1
        minDistancePointNormal = None
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
                if nearestPoint.isClose(p1):
                    dir1 = (p2 - p1).normalize()
                    dir2 = (self.convexHullPoints[i - 2] - p1).normalize()
                    angle = dir2.direction2() - dir1.direction2()
                    minDistancePointNormal = dir2.rotate2((math.pi * 2 - angle) / 2)
                elif nearestPoint.isClose(p2):
                    dir1 = (p1 - p2).normalize()
                    dir2 = (self.convexHullPoints[(i + 1) % len(self.convexHullPoints)] - p2).normalize()
                    angle = dir2.direction2() - dir1.direction2()
                    minDistancePointNormal = dir2.rotate2((math.pi * 2 - angle) / 2)
                else:
                    minDistancePointNormal = \
                        (p2 - p1).normalize().rotate2(-math.pi/2)

        return minDistancePointNormal


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
        return (point - self.getPosition()).rotate2(-self.getRotation().z)

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

    def doWallCollideAction(self):
        if self.wallCollideAction is not None:
            self.wallCollideAction()

    def getFloorStartTouchAction(self):
        return self.floorStartTouchAction

    def setFloorStartTouchAction(self, action):
        def do(toUpdateList):
            self.floorStartTouchAction = action
        self.actions.addAction(do)

    def doFloorStartTouchAction(self):
        if self.floorStartTouchAction is not None:
            self.floorStartTouchAction()

    def getFloorEndTouchAction(self):
        return self.floorEndTouchAction

    def setFloorEndTouchAction(self, action):
        def do(toUpdateList):
            self.floorEndTouchAction = action
        self.actions.addAction(do)

    def doFloorEndTouchAction(self):
        if self.floorEndTouchAction is not None:
            self.floorEndTouchAction()

    def getCeilingCollideAction(self):
        return self.ceilingCollideAction

    def setCeilingCollideAction(self, action):
        def do(toUpdateList):
            self.ceilingCollideAction = action
        self.actions.addAction(do)

    def doCeilingCollideAction(self):
        if self.ceilingCollideAction is not None:
            self.ceilingCollideAction()


class CollisionPoint:

    def __init__(self, height, normal):
        self.height = height
        self.normal = normal

