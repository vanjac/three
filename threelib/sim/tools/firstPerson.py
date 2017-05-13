__author__ = "jacobvanthoog"

import math
from threelib.sim.tools.physicsObject import PhysicsObject
from threelib.vectorMath import Vector
from threelib.vectorMath import Rotate
from threelib import vectorMath
from threelib.sim.input import ButtonInput

class FirstPersonPlayer(PhysicsObject):

    def __init__(self, world, xLookAxis, yLookAxis, xWalkAxis, yWalkAxis,
                 jumpButton,
                 cameraHeight=17.0, playerHeight=18.0, playerWidth=8.0,
                 walkSpeed = 14.0, fallMoveSpeed=7.0, maxWalkAngle=45.0,
                 jumpVelocity=30.0, walkDeceleration=0.001,
                 fallDeceleration=0.7):
        super().__init__(world, width=playerWidth, height=playerHeight,
                         originHeight=cameraHeight)
        self.world = world
        self.xLookAxis = xLookAxis
        self.yLookAxis = yLookAxis
        self.xWalkAxis = xWalkAxis
        self.yWalkAxis = yWalkAxis
        self.jumpButton = jumpButton

        self.sliding = False

        self.walkSpeed = walkSpeed
        self.fallMoveSpeed = fallMoveSpeed
        self.walkDeceleration = walkDeceleration
        self.fallDeceleration = fallDeceleration
        self.maxWalkAngle = maxWalkAngle # in degrees
        self.minWalkNormalZ = Vector(1.0, 0.0)\
            .rotate2(math.radians(self.maxWalkAngle)).x
        self.jumpVelocity = jumpVelocity

    def scan(self, timeElapsed, totalTime):
        self.scanStart()

        # look
        self.rotationChange = Rotate(0, -float(self.yLookAxis.getChange()),
                                   -float(self.xLookAxis.getChange()))

        inputTranslation = Vector( self.yWalkAxis.getValue(),
            -self.xWalkAxis.getValue()).limitMagnitude(1.0) * self.walkSpeed

        # orient walking direction to look direction
        inputTranslation = inputTranslation.rotate2(self.rotation.z)
        if self.newCurrentFloor is None:
            # slower movement while in the air
            inputTranslation *= float(self.fallMoveSpeed) / self.walkSpeed
        if self.newXYVelocity.magnitude() < inputTranslation.magnitude() \
                and not self.sliding:
            walking = True
            self.newXYVelocity = inputTranslation
        else:
            walking = False
        if ((not walking) and (not self.sliding)):
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
                    if walking or not self.sliding:
                        velocity = self.newXYVelocity.setZ(self.newZVelocity)
                        # project onto plane
                        velocity = velocity - \
                            (velocity.project(point.normal) * point.normal)

                        self.newXYVelocity = velocity.setZ(0)
                    self.newXYVelocity += movementDirection \
                        * -PhysicsObject.GRAVITY \
                        * point.normal.project(Vector(0,0,1)) * timeElapsed \
                        * (point.normal.setZ(0).magnitude())
                else:
                    slopeFactorOffset = \
                        movement.setMagnitude(1.0).project(point.normal)
                    if slopeFactorOffset > 0:
                        slopeFactorOffset = 0
                    slopeFactor = 1.0 + slopeFactorOffset

        jumpEvent = self.jumpButton.getEvent()
        if self.newCurrentFloor is not None \
                and jumpEvent == ButtonInput.PRESSED_EVENT:
            # jump direction is floor normal
            floorNormal = self._topPoint(self.newCurrentFloor,
                self.position + self.positionChange).normal
            self.newZVelocity = self.jumpVelocity * floorNormal.z
            self.newXYVelocity += self.jumpVelocity * floorNormal.setZ(0)
            self.newCurrentFloor.doFloorEndTouchAction()
            self.newCurrentFloor = None

        # walk
        self.positionChange += movement * slopeFactor
        if self.newCurrentFloor is None:
            # z velocity
            self.positionChange += Vector(0, 0, self.newZVelocity * timeElapsed)

        self.scanEnd(timeElapsed, totalTime)

        def do(toUpdateList):
            prevRotation = self.rotation
            self.rotation += self.rotationChange
            self.sliding = self.newSliding

            # prevent from looking too far up or down
            yRot = self.rotation.y
            if math.pi/2 < yRot < math.pi:
                self.rotation = self.rotation.setY(math.pi/2)
            if math.pi < yRot < math.pi*3/2:
                self.rotation = self.rotation.setY(math.pi*3/2)

            # rotate children
            prevRotateZ = Rotate(0, 0, prevRotation.z)
            rotateZ = Rotate(0, 0, (self.rotation - prevRotation).z)
            rotateY = Rotate(0, (self.rotation - prevRotation).y, 0)
            for child in self.children:
                child.rotate(-prevRotateZ, True)
                child.rotate(rotateY, True)
                child.rotate(prevRotateZ, True)
                child.rotate(rotateZ, True)

                startPosition = child.getPosition()
                endPosition = startPosition

                endPosition = endPosition.rotateAround(-prevRotateZ,
                                                       self.getPosition())
                endPosition = endPosition.rotateAround(rotateY,
                                                       self.getPosition())
                endPosition = endPosition.rotateAround(prevRotateZ,
                                                       self.getPosition())
                endPosition = endPosition.rotateAround(rotateZ,
                                                       self.getPosition())

                child.translate(endPosition - startPosition)

                toUpdateList.append(child)

            toUpdateList.append(self)
        self.actions.addAction(do)


    # end def scan
