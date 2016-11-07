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
                 cameraHeight=17.0, playerHeight=18.0, playerWidth=12.0,
                 walkSpeed = 50.0, fallMoveSpeed=30.0, maxWalkAngle=45.0,
                 jumpVelocity=40.0):
        super().__init__()
        self.world = world
        self.xLookAxis = xLookAxis
        self.yLookAxis = yLookAxis
        self.xWalkAxis = xWalkAxis
        self.yWalkAxis = yWalkAxis
        self.jumpButton = jumpButton

        self.zVelocity = 0.0
        self.currentFloor = None
        self.currentVolumes = [ ]
        self.wallCollisions = [ ] # walls the player is currently colliding with
        self.previousWallCollisions = [ ]

        self.cameraHeight = cameraHeight
        self.playerHeight = playerHeight
        self.playerWidth = playerWidth
        self.walkSpeed = walkSpeed
        self.fallMoveSpeed = fallMoveSpeed
        self.maxWalkAngle = maxWalkAngle # in degrees
        self.minWalkNormalZ = Vector(1.0, 0.0)\
            .rotate2(math.radians(self.maxWalkAngle)).x
        self.jumpVelocity = jumpVelocity

    def scan(self, timeElapsed, totalTime):
        rotation = Rotate(0, -float(self.yLookAxis.getChange()), \
                             -float(self.xLookAxis.getChange()))
        translation = Vector( self.yWalkAxis.getValue(),
                             -self.xWalkAxis.getValue()).limitMagnitude(1.0) \
                      *timeElapsed * self.walkSpeed

        def do(toUpdateList):
            # LOOK

            self.rotation += rotation

            # prevent from looking too far up or down
            yRot = self.rotation.y
            if yRot > math.pi/2 and yRot < math.pi:
                self.rotation = self.rotation.setY(math.pi/2)
            if yRot > math.pi and yRot < math.pi*3/2:
                self.rotation = self.rotation.setY(math.pi*3/2)

            # PHYSICS

            if self.currentFloor == None:
                # gravity
                self.zVelocity += FirstPersonPlayer.GRAVITY * timeElapsed

            movement = translation.rotate2(self.rotation.z)
            sliding = False

            # uphill slopes should slow down movement
            # downhill slopes should speed up movement
            slopeFactor = float(self.fallMoveSpeed) / self.walkSpeed
            if self.currentFloor != None:
                point = self._topPoint(self.currentFloor, self.position)
                if point != None:
                    # if slope is too steep, slide down it
                    if point.normal.z < self.minWalkNormalZ:
                        movement = point.normal.setZ(0).setMagnitude(1.0)
                        sliding = True

                    # this uses vector projection and magic
                    slopeFactor = 1.0 + movement.project(point.normal)

            jumpEvent = self.jumpButton.getEvent()
            if self.currentFloor != None:
                if jumpEvent == ButtonInput.PRESSED_EVENT and sliding == False:
                    self.zVelocity = self.jumpVelocity
                    self.currentFloor.doFloorEndTouchAction()
                    self.currentFloor = None

            previousPosition = self.position
            # walk
            self.position += movement * slopeFactor
            if self.currentFloor == None:
                # z velocity
                self.position += Vector(0, 0, self.zVelocity * timeElapsed)

            self.previousWallCollisions = self.wallCollisions
            self.wallCollisions = list()

            for collision in self.world.collisionMeshes:
                if collision.isEnabled() and collision != self.currentFloor:

                    if collision.isSolid():
                        if self._inBounds(collision, self.position):
                            self._checkSolidMeshCollision(collision,
                                previousPosition)
                    else: # collision is volume
                        topPoint = self._topPoint(collision, self.position)
                        bottomPoint = \
                            self._bottomPoint(collision, self.position)
                        if self._inBounds(collision, self.position) \
                                and vectorMath.rangesIntersect(
                                self._playerBottom(self.position).z,
                                self._playerTop(self.position).z,
                                bottomPoint.height, topPoint.height):
                            if not collision in self.currentVolumes:
                                self.currentVolumes.append(collision)
                                collision.doFloorStartTouchAction()
                        else:
                            if collision in self.currentVolumes:
                                self.currentVolumes.remove(collision)
                                collision.doFloorEndTouchAction()
            # end for each collision mesh

            if self.currentFloor != None:
                point = self._topPoint(self.currentFloor, self.position)
                if point == None:
                    self.zVelocity = 0.0
                    self.currentFloor.doFloorEndTouchAction()
                    self.currentFloor = None
                else:
                    z = point.height + self.cameraHeight
                    def do(toUpdateList):
                        self.position = self.position.setZ(z)
                    self.actions.addAction(do)

            toUpdateList.append(self)
        self.actions.addAction(do)
    # end def scan


    def _checkSolidMeshCollision(self, collision, previousPosition):
        topPoint = self._topPoint(collision, self.position)
        bottomPoint = self._bottomPoint(collision, self.position)

        # check wall collision
        if (not self._inBounds(collision, previousPosition)) \
            and vectorMath.rangesIntersect(
                self._playerBottom(self.position).z,
                self._playerTop(self.position).z,
                bottomPoint.height, topPoint.height):
            self.position = previousPosition.setZ(self.position.z)
            if not collision in self.previousWallCollisions:
                collision.doWallCollideAction()
            self.wallCollisions.append(collision)
            return


        # check floor collision
        if topPoint != None:
            if self.currentFloor == None:
                # TODO: cleanup!
                currentZ = self._playerBottom(self.position).z
                previousZ = self._playerBottom(previousPosition).z

                # if player just hit this floor
                if currentZ <= topPoint.height and previousZ > topPoint.height:
                    self.zVelocity = 0.0
                    self.currentFloor = collision
                    collision.doFloorStartTouchAction()
                else:
                    # what if the floor height has changed as the player moves?
                    nextFloorPreviousPoint = self._topPoint(
                        collision, previousPosition)

                    if nextFloorPreviousPoint != None:
                        if currentZ <= topPoint.height \
                          and previousZ > nextFloorPreviousPoint.height:
                            self.zVelocity = 0.0
                            self.currentFloor = collision
                            collision.doFloorStartTouchAction()

            # already on a floor
            elif self._inBounds(collision, previousPosition):
                # these checks are required
                currentFloorPreviousPoint = self._topPoint(
                    self.currentFloor, previousPosition)
                currentFloorCurrentPoint = self._topPoint(
                    self.currentFloor, self.position)
                nextFloorPreviousPoint = self._topPoint(
                    collision, previousPosition)
                if currentFloorPreviousPoint != None \
                        and currentFloorCurrentPoint != None \
                        and nextFloorPreviousPoint != None:
                    currentFloorPreviousZ = currentFloorPreviousPoint.height
                    currentFloorCurrentZ = currentFloorCurrentPoint.height
                    nextFloorPreviousZ = nextFloorPreviousPoint.height
                    nextFloorCurrentZ = topPoint.height
                    # allow walking from one floor onto another
                    if currentFloorPreviousZ >= nextFloorPreviousZ \
                            and currentFloorCurrentZ < nextFloorCurrentZ:
                        # if the new floor's slope is too steep,
                        # don't walk onto it
                        if topPoint.normal.z < self.minWalkNormalZ:
                            self.position = previousPosition \
                                .setZ(self.position.z)
                        else:
                            self.zVelocity = 0.0
                            self.currentFloor.doFloorEndTouchAction()
                            self.currentFloor = collision
                            collision.doFloorStartTouchAction()
        # end check floor collision

        # check ceiling collision
        if bottomPoint != None:
            if self.currentFloor == None:
                # TODO: cleanup!
                currentZ = self._playerTop(self.position).z
                previousZ = self._playerTop(previousPosition).z

                # if player just hit this ceiling
                if currentZ >= bottomPoint.height \
                        and previousZ < bottomPoint.height:
                    self.zVelocity = 0.0
                    collision.doCeilingCollideAction()
                else:
                    # what if the ceiling height has changed as the
                    # player moves?
                    ceilingPreviousPoint = self._bottomPoint(
                        collision, previousPosition)

                    if ceilingPreviousPoint != None:
                        if currentZ >= bottomPoint.height \
                                and previousZ < ceilingPreviousPoint.height:
                            self.zVelocity = 0.0
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
        if pointInBounds == None:
            return None
        else:
            return collision.topPointAt(pointInBounds)

    def _bottomPoint(self, collision, point):
        pointInBounds = self._inBounds(collision, point)
        if pointInBounds == None:
            return None
        else:
            return collision.bottomPointAt(pointInBounds)

    def _playerTop(self, playerPosition):
        return self._playerBottom(playerPosition) \
            + Vector(0, 0, self.playerHeight)

    def _playerBottom(self, playerPosition):
        return playerPosition - Vector(0, 0, self.cameraHeight)

