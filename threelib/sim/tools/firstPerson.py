__author__ = "jacobvanthoog"

import math
from threelib.sim.base import Entity
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib import vectorMath
from threelib.sim.input import ButtonInput

class FirstPersonPlayer(Entity):
    GRAVITY = -80.0

    def __init__(self, world, xLookAxis, yLookAxis, xWalkAxis, yWalkAxis,
                 jumpButton,
                 cameraHeight=17.0, playerHeight=18.0, playerWidth=8.0,
                 walkSpeed = 14.0, fallMoveSpeed=7.0, maxWalkAngle=45.0,
                 jumpVelocity=30.0, walkDeceleration=0.001,
                 fallDeceleration=0.7):
        super().__init__()
        self.world = world
        self.xLookAxis = xLookAxis
        self.yLookAxis = yLookAxis
        self.xWalkAxis = xWalkAxis
        self.yWalkAxis = yWalkAxis
        self.jumpButton = jumpButton

        self.xyVelocity = Vector(0.0, 0.0)
        self.zVelocity = 0.0
        self.currentFloor = None
        self.currentVolumes = [ ]
        self.wallCollisions = [ ] # walls the player is currently colliding with
        self.previousWallCollisions = [ ]
        self.sliding = False

        self.cameraHeight = cameraHeight
        self.playerHeight = playerHeight
        self.playerWidth = playerWidth
        self.walkSpeed = walkSpeed
        self.fallMoveSpeed = fallMoveSpeed
        self.walkDeceleration = walkDeceleration
        self.fallDeceleration = fallDeceleration
        self.maxWalkAngle = maxWalkAngle # in degrees
        self.minWalkNormalZ = Vector(1.0, 0.0)\
            .rotate2(math.radians(self.maxWalkAngle)).x
        self.jumpVelocity = jumpVelocity

    def scan(self, timeElapsed, totalTime):
        self.positionChange = Vector(0, 0, 0)
        self.newZVelocity = self.zVelocity
        self.newXYVelocity = self.xyVelocity
        self.newCurrentFloor = self.currentFloor

        # look
        self.rotationChange = Rotate(0, -float(self.yLookAxis.getChange()),
                                   -float(self.xLookAxis.getChange()))

        inputTranslation = Vector( self.yWalkAxis.getValue(),
            -self.xWalkAxis.getValue()).limitMagnitude(1.0) * self.walkSpeed

        if self.newCurrentFloor is None:
            # gravity
            self.newZVelocity += FirstPersonPlayer.GRAVITY * timeElapsed

        # before applying input or deceleration
        prevNewXYVelocity = self.newXYVelocity

        # orient walking direction to look direction
        inputTranslation = inputTranslation.rotate2(self.rotation.z)
        if self.newCurrentFloor is None:
            # slower movement while in the air
            inputTranslation *= float(self.fallMoveSpeed) / self.walkSpeed
        if self.newXYVelocity.magnitude() < inputTranslation.magnitude():
            self.newXYVelocity = inputTranslation
        else:
            # when not moving, gradually slow down x-y velocity
            if self.newCurrentFloor is None:
                self.newXYVelocity *= (self.fallDeceleration ** timeElapsed)
            else:
                self.newXYVelocity *= (self.walkDeceleration ** timeElapsed)

        movement = self.newXYVelocity * timeElapsed
        self.newSliding = False

        # uphill slopes should slow down movement
        # downhill slopes should speed up movement
        slopeFactor = 1.0
        if self.newCurrentFloor is not None:
            point = self._topPoint(self.newCurrentFloor,
                                   self.position + self.positionChange)
            if point is not None:
                # if slope is too steep, slide down it
                if point.normal.z < self.minWalkNormalZ:
                    self.newSliding = True

                    movementDirection = point.normal.setZ(0).setMagnitude(1.0)
                    # slope of surface in movement direction (always positive)
                    slope = point.normal.setZ(0).magnitude() / point.normal.z
                    if not self.sliding:
                        self.newXYVelocity = self.newXYVelocity / slope
                    else:
                        self.newXYVelocity = prevNewXYVelocity
                    self.newXYVelocity += movementDirection \
                        * -FirstPersonPlayer.GRAVITY * timeElapsed / slope \
                        * (point.normal.setZ(0).magnitude())
                    movement = self.newXYVelocity * timeElapsed
                else:
                    slopeFactorOffset = \
                        movement.setMagnitude(1.0).project(point.normal)
                    if slopeFactorOffset > 0:
                        slopeFactorOffset = 0
                    slopeFactor = 1.0 + slopeFactorOffset

        jumpEvent = self.jumpButton.getEvent()
        if self.newCurrentFloor is not None \
                and jumpEvent == ButtonInput.PRESSED_EVENT \
                and self.newSliding == False:
            self.newZVelocity = self.jumpVelocity
            self.newCurrentFloor.doFloorEndTouchAction()
            self.newCurrentFloor = None

        # walk
        self.positionChange += movement * slopeFactor
        if self.newCurrentFloor is None:
            # z velocity
            self.positionChange += Vector(0, 0, self.newZVelocity * timeElapsed)

        self.previousWallCollisions = self.wallCollisions
        self.wallCollisions = list()

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
                                self._playerBottom(
                                    self.position + self.positionChange).z,
                                self._playerTop(
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
                self.newZVelocity = 0.0
                self.newCurrentFloor.doFloorEndTouchAction()
                self.newCurrentFloor = None
            else:
                z = point.height + self.cameraHeight
                self.positionChange = \
                    self.positionChange.setZ(z - self.position.z)

        def do(toUpdateList):
            self.translate(self.positionChange)
            self.rotation += self.rotationChange
            self.zVelocity = self.newZVelocity
            self.xyVelocity = self.newXYVelocity
            self.currentFloor = self.newCurrentFloor
            self.sliding = self.newSliding

            # prevent from looking too far up or down
            yRot = self.rotation.y
            if math.pi/2 < yRot < math.pi:
                self.rotation = self.rotation.setY(math.pi/2)
            if math.pi < yRot < math.pi*3/2:
                self.rotation = self.rotation.setY(math.pi*3/2)

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
                self._playerBottom(self.position + self.positionChange).z,
                self._playerTop(self.position + self.positionChange).z,
                bottomPoint.height, topPoint.height):
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
                currentZ = self._playerBottom(
                    self.position + self.positionChange).z
                previousZ = self._playerBottom(self.position).z

                # if player just hit this floor
                if currentZ <= topPoint.height < previousZ:
                    self.newZVelocity = 0.0
                    self.newCurrentFloor = collision
                    collision.doFloorStartTouchAction()
                else:
                    # what if the floor height has changed as the player moves?
                    nextFloorPreviousPoint = self._topPoint(
                        collision, self.position)

                    if nextFloorPreviousPoint is not None:
                        if currentZ <= topPoint.height \
                          and previousZ > nextFloorPreviousPoint.height:
                            self.newZVelocity = 0.0
                            self.newCurrentFloor = collision
                            collision.doFloorStartTouchAction()

            # already on a floor
            elif self._inBounds(collision, self.position):
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
                    if vectorMath.greaterOrClose(
                                currentFloorPreviousZ, nextFloorPreviousZ) \
                            and vectorMath.lessOrClose(
                                currentFloorCurrentZ, nextFloorCurrentZ):
                        # if the new floor's slope is too steep,
                        # don't walk onto it
                        if topPoint.normal.z < self.minWalkNormalZ:
                            self.positionChange = \
                                Vector(0, 0, self.positionChange.z)
                            self.newXYVelocity = Vector(0, 0)
                        else:
                            self.newZVelocity = 0.0
                            self.newCurrentFloor.doFloorEndTouchAction()
                            self.newCurrentFloor = collision
                            collision.doFloorStartTouchAction()
                # allow walking off the edge of one floor, immediately onto
                # another
                if currentFloorPreviousPoint is not None \
                        and currentFloorCurrentPoint is None:
                    currentFloorPreviousZ = currentFloorPreviousPoint.height
                    nextFloorCurrentZ = topPoint.height
                    if vectorMath.isclose(currentFloorPreviousZ,
                                          nextFloorCurrentZ):
                        # if the new floor's slope is too steep,
                        # don't walk onto it
                        if topPoint.normal.z < self.minWalkNormalZ:
                            self.positionChange = \
                                Vector(0, 0, self.positionChange.z)
                        else:
                            self.newZVelocity = 0.0
                            self.newCurrentFloor.doFloorEndTouchAction()
                            self.newCurrentFloor = collision
                            collision.doFloorStartTouchAction()
        # end check floor collision

        # check ceiling collision
        if bottomPoint is not None:
            if self.newCurrentFloor is None:
                # TODO: cleanup!
                currentZ = self._playerTop(
                    self.position + self.positionChange).z
                previousZ = self._playerTop(self.position).z

                # if player just hit this ceiling
                if currentZ >= bottomPoint.height > previousZ:
                    self.newZVelocity = 0.0
                    collision.doCeilingCollideAction()
                else:
                    # what if the ceiling height has changed as the
                    # player moves?
                    ceilingPreviousPoint = self._bottomPoint(
                        collision, self.position)

                    if ceilingPreviousPoint is not None:
                        if currentZ >= bottomPoint.height \
                                and previousZ < ceilingPreviousPoint.height:
                            self.newZVelocity = 0.0
                            collision.doCeilingCollideAction()
        # end check ceiling collision
    # end def _checkSolidMeshCollision


    # return a vector that is in bounds, or None
    def _inBounds(self, collision, point):
        if collision.isInBounds(point):
            return point
        else:
            return collision.nearestBoundsPoint(point,
                maxDistance=self.playerWidth/2.0)

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

    def _playerTop(self, playerPosition):
        return self._playerBottom(playerPosition) \
            + Vector(0, 0, self.playerHeight)

    def _playerBottom(self, playerPosition):
        return playerPosition - Vector(0, 0, self.cameraHeight)

