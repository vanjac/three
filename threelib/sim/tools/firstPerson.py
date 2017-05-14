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

        self.walkSpeed = walkSpeed
        self.fallMoveSpeed = fallMoveSpeed
        self.walkDeceleration = walkDeceleration
        self.fallDeceleration = fallDeceleration
        self.maxWalkAngle = maxWalkAngle # in degrees
        if maxWalkAngle == None:
            self.minWalkNormalZ = None
        else:
            self.minWalkNormalZ = Vector(1.0, 0.0)\
                .rotate2(math.radians(self.maxWalkAngle)).x
        self.jumpVelocity = jumpVelocity

        self.floorXYVelocity = Vector(0, 0, 0)

    def scan(self, timeElapsed, totalTime):
        self.scanStart()
        self.newFloorXYVelocity = self.floorXYVelocity

        # look
        self.rotationChange = Rotate(0, -float(self.yLookAxis.getChange()),
                                   -float(self.xLookAxis.getChange()))

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

        if self.newCurrentFloor is not None:
            point = self._topPoint(self.newCurrentFloor,
                                   self.position + self.positionChange)
            if self.minWalkNormalZ == None:
                sliding = True
            else:
                sliding = point.normal.z < self.minWalkNormalZ
        else:
            point = None
            sliding = True

        inputTranslation = Vector( self.yWalkAxis.getValue(),
            -self.xWalkAxis.getValue()).limitMagnitude(1.0) * self.walkSpeed
        # orient walking direction to look direction
        inputTranslation = inputTranslation.rotate2(self.rotation.z)
        if self.newCurrentFloor is None:
            # slower movement while in the air
            inputTranslation *= float(self.fallMoveSpeed) / self.walkSpeed

        walking = False
        if not inputTranslation.isZero():
            walking = True

            velocity = (inputTranslation * timeElapsed).setZ(0)
            if self.newCurrentFloor is not None:
                if not sliding:
                    # walk; walking up slopes should be slower
                    project = inputTranslation.setMagnitude(1.0) \
                        .projectOnPlane(point.normal)
                    if project.z < 0:
                        slopeFactor = 1
                    else:
                        slopeFactor = project.magnitude()
                    self.newFloorXYVelocity = inputTranslation * slopeFactor
                elif self.minWalkNormalZ == None:
                    # only allow extra force while sliding if walking has been
                    # disabled
                    self.newFloorXYVelocity += velocity
            else:
                self.newXYVelocity += velocity

        if not walking:
            # when not moving, gradually slow down x-y velocity
            if self.newCurrentFloor is None:
                deceleration = (self.fallDeceleration ** timeElapsed)
                self.newXYVelocity *= deceleration
            else:
                if not sliding:
                    deceleration = (self.walkDeceleration ** timeElapsed)
                else:
                    deceleration = (self.fallDeceleration ** timeElapsed)
                self.newFloorXYVelocity *= deceleration

        if self.newCurrentFloor is not None:
            # gravity
            if sliding or walking:
                gravityVelocity = Vector(0, 0, PhysicsObject.GRAVITY) \
                    .projectOnPlane(point.normal)
                self.newFloorXYVelocity += gravityVelocity.setZ(0) \
                                               .setMagnitude(
                    gravityVelocity.magnitude()) * timeElapsed

            normalRot = point.normal.rotation()
            # orient the floor velocity onto the floor plane
            velocity = self.newFloorXYVelocity.setZ(0) \
                .rotate2(-normalRot.z) \
                .rotate(Rotate(0, normalRot.y - math.pi/2, 0)) \
                .rotate2(normalRot.z)
            self.newXYVelocity = velocity.setZ(0)

        self.positionChange += self.newXYVelocity * timeElapsed
        if self.newCurrentFloor is None:
            # z velocity
            self.positionChange += Vector(0, 0, self.newZVelocity * timeElapsed)

        prevNewXYVelocity = self.newXYVelocity
        self.scanEnd(timeElapsed, totalTime)

        if self.newCurrentFloor is not None:
            newPoint = self._topPoint(self.newCurrentFloor,
                                    self.position + self.positionChange)
            if (prevNewXYVelocity != self.newXYVelocity
                    or self.currentFloor is None):
                # use old Z velocity because new velocity has been set to 0
                velocity = self.newXYVelocity.setZ(self.zVelocity)
                velocity = velocity.projectOnPlane(newPoint.normal)
                normalRot = newPoint.normal.rotation()
                # convert velocity to floor velocity
                # opposite of floor orientation above
                velocity = velocity \
                    .rotate2(-normalRot.z) \
                    .rotate(Rotate(0, -normalRot.y + math.pi / 2, 0)) \
                    .rotate2(normalRot.z)
                self.newFloorXYVelocity = velocity.setZ(0)
            if point is not None:
                # positive is going down the slope
                # negative is going up the slope
                slope1 = self.newXYVelocity.project(point.normal)
                slope2 = self.newXYVelocity.project(newPoint.normal)
                if slope1 <= 0 and slope2 >= 0 \
                        and not (slope1 == 0 and slope2 == 0):
                    # jump over a hill
                    self.newCurrentFloor = None
                    # set z velocity to z movement up/down slope
                    slope = -(point.normal.setZ(0).magnitude() / point.normal.z)
                    self.newZVelocity = \
                        self.newXYVelocity.project(point.normal.setZ(0)) * slope

        def do(toUpdateList):
            self.floorXYVelocity = self.newFloorXYVelocity

            prevRotation = self.rotation
            self.rotation += self.rotationChange

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
