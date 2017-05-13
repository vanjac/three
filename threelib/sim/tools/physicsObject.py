__author__ = "jacobvanthoog"

import math
from threelib.sim.base import Entity
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib import vectorMath

class PhysicsObject(Entity):
    GRAVITY = -80.0

    def __init__(self, world, width, height, originHeight=None):
        super().__init__()
        self.world = world

        self.xyVelocity = Vector(0.0, 0.0)
        self.zVelocity = 0.0
        self.currentFloor = None
        self.currentVolumes = [ ]
        self.wallCollisions = [ ] # walls the object is currently colliding with
        self.previousWallCollisions = [ ]
        self.ceilingCollisions = [ ]
        self.previousCeilingCollisions = [ ]

        if originHeight == None:
            originHeight = height / 2
        self.originHeight = originHeight
        self.height = height
        self.width = width

    def scanStart(self):
        self.positionChange = Vector(0, 0, 0)
        self.newZVelocity = self.zVelocity
        self.newXYVelocity = self.xyVelocity
        self.newCurrentFloor = self.currentFloor

    def scanEnd(self, timeElapsed, totalTime):
        if self.newCurrentFloor is None:
            # gravity
            self.newZVelocity += PhysicsObject.GRAVITY * timeElapsed

        self.previousWallCollisions = self.wallCollisions
        self.wallCollisions = list()
        self.previousCeilingCollisions = self.ceilingCollisions
        self.ceilingCollisions = list()

        if self.newCurrentFloor is not None:
            # A more complete check of the current floor height is below.
            # This just exists so the ceiling collision check will have the
            # correct current Z position - so collision with a ceiling while
            # walking up a slope works
            point = self._topPoint(self.newCurrentFloor,
                                   self.position + self.positionChange)
            if point is not None:
                z = point.height + self.originHeight
                self.positionChange = \
                    self.positionChange.setZ(z - self.position.z)

        for collision in self.world.collisionMeshes:
            if collision.isEnabled() and collision != self.newCurrentFloor:

                if collision.isSolid():
                    if self._inBounds(collision,
                                      self.position + self.positionChange):
                        self._checkSolidMeshCollision(collision)
                else: # collision is volume
                    topPoint = self._topPoint(collision,
                        self.position + self.positionChange)
                    bottomPoint = \
                        self._bottomPoint(collision,
                                          self.position + self.positionChange)
                    if self._inBounds(collision,
                                self.position + self.positionChange) \
                            and vectorMath.rangesIntersect(
                                self._objectBottom(
                                    self.position + self.positionChange).z,
                                self._objectTop(
                                    self.position + self.positionChange).z,
                                bottomPoint.height, topPoint.height):
                        if not collision in self.currentVolumes:
                            self.currentVolumes.append(collision)
                            collision.doFloorStartTouchAction()
                    else:
                        if collision in self.currentVolumes:
                            self.currentVolumes.remove(collision)
                            collision.doFloorEndTouchAction()
        # end for each collision mesh

        if self.newCurrentFloor is not None:
            point = self._topPoint(self.newCurrentFloor,
                                   self.position + self.positionChange)
            if point is None:
                # set z velocity to z movement up/down slope
                point = self._topPoint(self.newCurrentFloor,
                                       self.position)
                slope = -(point.normal.setZ(0).magnitude() / point.normal.z)
                self.newZVelocity = self.xyVelocity.project(point.normal.setZ(0)) * slope

                self.newCurrentFloor.doFloorEndTouchAction()
                self.newCurrentFloor = None
            else:
                z = point.height + self.originHeight
                self.positionChange = \
                    self.positionChange.setZ(z - self.position.z)

        def do(toUpdateList):
            self.translate(self.positionChange)
            self.zVelocity = self.newZVelocity
            self.xyVelocity = self.newXYVelocity
            self.currentFloor = self.newCurrentFloor
            toUpdateList.append(self)
        self.actions.addAction(do)


    # end def scan

    def _checkSolidMeshCollision(self, collision):
        topPoint = self._topPoint(collision,
                                  self.position + self.positionChange)
        bottomPoint = self._bottomPoint(collision,
                                        self.position + self.positionChange)

        # check wall collision
        if (not self._inBounds(collision, self.position)) \
            and vectorMath.rangesIntersect(
                self._objectBottom(self.position + self.positionChange).z,
                self._objectTop(self.position + self.positionChange).z,
                bottomPoint.height, topPoint.height):
            # slide along wall
            wallNormal = collision.nearestBoundsNormal(
                self.position + self.positionChange)
            slideDirection = wallNormal.setZ(0).rotate2(math.pi / 2).normalize()

            self.positionChange = (slideDirection *
                self.positionChange.setZ(0).project(slideDirection)) \
                .setZ(self.positionChange.z)
            self.newXYVelocity = slideDirection \
                                 * self.newXYVelocity.project(slideDirection)

            if self._inBounds(collision,
                              self.position + self.positionChange):
                self.positionChange = Vector(0, 0, self.positionChange.z)
                self.newXYVelocity = Vector(0, 0)

            if not collision in self.previousWallCollisions:
                collision.doWallCollideAction()
            self.wallCollisions.append(collision)
            return


        # check floor collision
        if topPoint is not None:
            if self.newCurrentFloor is None:
                # TODO: cleanup!
                currentZ = self._objectBottom(
                    self.position + self.positionChange).z
                previousZ = self._objectBottom(self.position).z

                # if object just hit this floor
                if currentZ <= topPoint.height < previousZ:
                    self.newZVelocity = 0.0
                    self.newCurrentFloor = collision
                    collision.doFloorStartTouchAction()
                else:
                    # what if the floor height has changed as the object moves?
                    nextFloorPreviousPoint = self._topPoint(
                        collision, self.position)

                    if nextFloorPreviousPoint is not None:
                        if vectorMath.lessOrClose(currentZ, topPoint.height) \
                                and vectorMath.greaterOrClose(
                                    previousZ, nextFloorPreviousPoint.height) \
                                and not (
                                    vectorMath.isclose(
                                        currentZ, topPoint.height)
                                    and vectorMath.isclose(previousZ,
                                        nextFloorPreviousPoint.height)):
                            self.newZVelocity = 0.0
                            self.newCurrentFloor = collision
                            collision.doFloorStartTouchAction()

            # already on a floor
            elif self._inBounds(collision, self.position):
                floorCollision = False
                # these checks are required
                currentFloorPreviousPoint = self._topPoint(
                    self.newCurrentFloor, self.position)
                currentFloorCurrentPoint = self._topPoint(
                    self.newCurrentFloor, self.position + self.positionChange)
                nextFloorPreviousPoint = self._topPoint(
                    collision, self.position)
                if currentFloorPreviousPoint is not None \
                        and currentFloorCurrentPoint is not None \
                        and nextFloorPreviousPoint is not None:
                    currentFloorPreviousZ = currentFloorPreviousPoint.height
                    currentFloorCurrentZ = currentFloorCurrentPoint.height
                    nextFloorPreviousZ = nextFloorPreviousPoint.height
                    nextFloorCurrentZ = topPoint.height
                    # allow walking from one floor onto another
                    if (vectorMath.greaterOrClose(
                                currentFloorPreviousZ, nextFloorPreviousZ)
                            and vectorMath.lessOrClose(
                                currentFloorCurrentZ, nextFloorCurrentZ)
                            # prevent alternating between floors
                            # and getting stuck between a steep floor and a flat
                            # one
                            and not (
                                vectorMath.isclose(
                                    currentFloorPreviousZ, nextFloorPreviousZ)
                                and vectorMath.isclose(
                                    currentFloorCurrentZ, nextFloorCurrentZ))):
                        floorCollision = True
                # allow walking off the edge of one floor, immediately onto
                # another
                if currentFloorPreviousPoint is not None \
                        and currentFloorCurrentPoint is None:
                    currentFloorPreviousZ = currentFloorPreviousPoint.height
                    nextFloorCurrentZ = topPoint.height
                    if vectorMath.isclose(currentFloorPreviousZ,
                                          nextFloorCurrentZ):
                        floorCollision = True
                if floorCollision:
                    self.newZVelocity = 0.0
                    self.newCurrentFloor.doFloorEndTouchAction()
                    self.newCurrentFloor = collision
                    collision.doFloorStartTouchAction()
        # end check floor collision

        # check ceiling collision
        if bottomPoint is not None:
            currentZ = self._objectTop(
                self.position + self.positionChange).z
            previousZ = self._objectTop(self.position).z
            ceilingCollision = False
            # if object just hit this ceiling
            if currentZ >= bottomPoint.height > previousZ:
                ceilingCollision = True
            else:
                # what if the ceiling height has changed as the
                # object moves?
                ceilingPreviousPoint = self._bottomPoint(
                    collision, self.position)

                if ceilingPreviousPoint is not None:
                    if currentZ >= bottomPoint.height \
                            and previousZ < ceilingPreviousPoint.height:
                        ceilingCollision = True
            if ceilingCollision:
                if self.newCurrentFloor is None:
                    if self.currentFloor is not None:
                        # just jumped
                        self.newCurrentFloor = self.currentFloor
                        self.newCurrentFloor.doFloorStartTouchAction()
                        self.newZVelocity = 0
                        self.newXYVelocity = Vector(0, 0)
                        self.positionChange = Vector(0, 0, 0)
                    else:
                        self.newZVelocity = -abs(self.newZVelocity)
                        self.positionChange = \
                            Vector(0, 0, bottomPoint.height - previousZ)
                else:
                    self.newXYVelocity = Vector(0, 0)
                    self.positionChange = Vector(0, 0, 0)
                if not collision in self.previousCeilingCollisions:
                    collision.doCeilingCollideAction()
                self.ceilingCollisions.append(collision)
            # end check ceiling collision
    # end def _checkSolidMeshCollision


    # return a vector that is in bounds, or None
    def _inBounds(self, collision, point):
        if collision.isInBounds(point):
            return point
        else:
            return collision.nearestBoundsPoint(point,
                                                maxDistance=self.width / 2.0)

    def _topPoint(self, collision, point):
        pointInBounds = self._inBounds(collision, point)
        if pointInBounds is None:
            return None
        else:
            return collision.topPointAt(pointInBounds)

    def _bottomPoint(self, collision, point):
        pointInBounds = self._inBounds(collision, point)
        if pointInBounds is None:
            return None
        else:
            return collision.bottomPointAt(pointInBounds)

    def _objectTop(self, objectPosition):
        return self._objectBottom(objectPosition) \
            + Vector(0, 0, self.height)

    def _objectBottom(self, objectPosition):
        return objectPosition - Vector(0, 0, self.originHeight)

