__author__ = "vantjac"

import numbers
import math

# Based on JMath3d
    
CIRCLE = math.pi*2

# limit rotation to be between 0 and 2pi
def fixRotation(n):
    n = float(n)
    if n < 0:
        circles = math.ceil(-n / CIRCLE)
        n += circles * CIRCLE
    n = n % CIRCLE
    return n

def tripleTupleToString(t):
    return numToStr(t[0]) + ',' + \
        numToStr(t[1]) + ',' + \
        numToStr(t[2])

def numToStr(num):
    if num % 1.0 == 0.0:
        return str(int(num))
    else:
        return str(num)

class Vector:
        
    # computes the normal unit-vector of a triangle, with vertices in
    # counter-clockwise order
    @staticmethod
    def normal(v1, v2, v3):
        a = v2 - v1
        b = v3 - v1
        unit = a.cross(b)
        unit = unit.normalize()
        return unit

    @staticmethod
    def fromTuple(t):
        return Vector(t[0], t[1], t[2])
    

    def __init__(self, x, y, z = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        
    def __repr__(self):
        return tripleTupleToString(self.getTuple())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y and self.z == other.z
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def getTuple(self):
        return (self.x, self.y, self.z)
    
    def isZero(self):
        return self.x == 0 and self.y == 0 and self.z == 0
    
    def setX(self, newX):
        return Vector(newX, self.y, self.z)
        
    def setY(self, newY):
        return Vector(self.x, newY, self.z)
        
    def setZ(self, newZ):
        return Vector(self.x, self.y, newZ)
        
    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)
    
    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z)
    
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
    
    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)
    
    def __mul__(self, v):
        if isinstance(v, numbers.Number):
            return Vector(self.x * v, self.y * v, self.z * v)
        else:
            return Vector(self.x * v.x, self.y * v.y, self.z * v.z)
            
    def __rmul__(self, v):
        return self.__mul__(v)
        
    def __truediv__(self, v):
        if isinstance(v, numbers.Number):
            return Vector(self.x / v, self.y / v, self.z / v)
        else:
            return Vector(self.x / v.x, self.y / v.y, self.z / v.z)
    
    def __rtruediv__(self, v):
        if isinstance(v, numbers.Number):
            return Vector(v / self.x, v / self.y, v / self.z)
        else:
            return Vector(v.x / self.x, v.y / self.y, v.z / self.z / v.z)
        
    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z
    
    # Return true if this vector is orthogonal (at a right angle) to another
    # vector
    def orthogonal(self, v):
        return self.dot(v) == 0

    def cross(self, v):
        newX = self.y * v.z - self.z * v.y;
        newY = self.z * v.x - self.x * v.z;
        newZ = self.x * v.y - self.y * v.x;
        return Vector(newX, newY, newZ)
    
    # with amount = 0, returns this vector
    # with amount = 1, returns the other vector
    # with amount = 0.5, returns the halfway point
    # with other values in that range, returns interpolated values
    # with values outside of that range, returns extrapolated values
    def lerp(self, v, amount):
        difference = v - self
        return self + (difference * amount)

    def magnitude(self):
        return math.sqrt(self.magnitudeSquare())

    def magnitudeSquare(self):
        return self.x ** 2.0 + self.y ** 2.0 + self.z ** 2.0
    
    def setMagnitude(self, newMag):
        currentMag = self.magnitude()
        if currentMag == 0:
            return self
        return self * (newMag / currentMag)
    
    # only set magnitude if current magnitude is greater than max
    def limitMagnitude(self, maxMag):
        if self.magnitudeSquare() > maxMag**2:
            return self.setMagnitude(maxMag)
        else:
            return self

    def normalize(self):
        return self.setMagnitude(1.0)
    
    def distanceTo(self, v):
        return (self - v).magnitude()

    def angleBetween(self, v):
        try:
            return fixRotation(
                math.acos( self.dot(v) / (self.magnitude() * v.magnitude()) ) )
        except ValueError:
            # vectors are in opposite directions
            return math.pi
    
    def direction2(self):
        n = math.atan2(self.y, self.x)
        return fixRotation(n)
        
    def direction2Towards(self, v):
        return (v - self).direction2()
    
    def rotate2(self, amount):
        sinX = math.sin(amount)
        cosX = math.cos(amount)
        return Vector( self.x * cosX - self.y * sinX,
                       self.y * cosX + self.x * sinX )
    
    def rotate2Around(self, amount, center):
        return (self - center).rotate2(amount) + center
    
    # amount is a 2d vector describing movement
    def move2(self, direction, amount):
        amount = amount.rotate2(direction)
        return self + amount

    # convert the homogeneous coordinates of a 2d vector to a regular 2d vector 
    def homogeneousTo2d(self):
        return Vector(self.x / self.z, self.y / self.z)

    # get the direction of this 3d vector as a Rotation
    # the rotation will not have a "roll" or x-rotation component
    def rotation(self):
        xy = Vector(self.x, self.y)
        xyz = Vector(xy.magnitude(), self.z)
        yRot = xyz.direction2()
        zRot = xy.direction2()
        return Rotate(0, yRot, zRot);

    # return the direction towards another vector, as a unit-vector
    def directionTowards(self, v):
        return (v - self).normalize()

    def rotate(self, amount):
        v = self

        # roll (x)
        xRot = Vector(v.y, v.z)
        xRot = xRot.rotate2(amount.x)
        v = Vector(v.x, xRot.x, xRot.y)

        # pitch (y)
        yRot = Vector(v.x, v.z)
        yRot = yRot.rotate2(amount.y)
        v = Vector(yRot.x, v.y, yRot.y)

        # yaw (z)
        zRot = Vector(v.x, v.y)
        zRot = zRot.rotate2(amount.z)
        v = Vector(zRot.x, zRot.y, v.z)

        return v

    def inverseRotate(self, amount):
        v = self

        # yaw (z)
        zRot = Vector(v.x, v.y)
        zRot = zRot.rotate2(amount.z)
        v = Vector(zRot.x, zRot.y, v.z)

        # pitch (y)
        yRot = Vector(v.x, v.z)
        yRot = yRot.rotate2(amount.y)
        v = Vector(yRot.x, v.y, yRot.y)

        # roll (x)
        xRot = Vector(v.y, v.z)
        xRot = xRot.rotate2(amount.x)
        v = Vector(v.x, xRot.x, xRot.y)
        
        return v
        
    def rotateAround(self, amount, center):
        return (self - center).rotate(amount) + center
    
    # amount is a 3d vector describing movement
    def move(self, direction, amount):
        amount = amount.rotate(direction)
        return self + amount

class Rotate:
    
    @staticmethod
    def fromTuple(t):
        return Rotate(t[0], t[1], t[2])

    def __init__(self, x, y, z):
        self.x = fixRotation(x)
        self.y = fixRotation(y)
        self.z = fixRotation(z)
    
    def __repr__(self):
        return tripleTupleToString(self.getTuple())
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y and self.z == other.z
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def getTuple(self):
        return (self.x, self.y, self.z)
    
    def isZero(self):
        return self.x == 0 and self.y == 0 and self.z == 0
    
    def setX(self, newX):
        return Rotate(newX, self.y, self.z)
        
    def setY(self, newY):
        return Rotate(self.x, newY, self.z)
        
    def setZ(self, newZ):
        return Rotate(self.x, self.y, newZ)
    
    def __neg__(self):
        return Rotate(-self.x, -self.y, -self.z)
    
    def __add__(self, v):
        return Rotate(self.x + v.x, self.y + v.y, self.z + v.z)
    
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
    
    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)
            
    def __mul__(self, v):
        if isinstance(v, numbers.Number):
            return Rotate(self.x * v, self.y * v, self.z * v)
        else:
            return Rotate(self.x * v.x, self.y * v.y, self.z * v.z)

    def __rmul__(self, v):
        return self.__mul__(v)
        
    def __truediv__(self, v):
        if isinstance(v, numbers.Number):
            return Rotate(self.x / v, self.y / v, self.z / v)
        else:
            return Rotate(self.x / v.x, self.y / v.y, self.z / v.z)
    
    def __rtruediv__(self, v):
        if isinstance(v, numbers.Number):
            return Rotate(v / self.x, v / self.y, v / self.z)
        else:
            return Rotate(v.x / self.x, v.y / self.y, v.z / self.z / v.z)

    def rotate(self, amount):
        vector = BASE_ROTATION_V.rotate(self).rotate(amount)
        roll = self.x + amount.x
        return vector.rotation().setX(roll)

    
ZERO_V = Vector(0, 0, 0)

FORWARD_V = Vector(-1, 0, 0)
BACK_V = Vector(1, 0, 0)
LEFT_V = Vector(0, -1, 0)
RIGHT_V = Vector(0, 1, 0)
DOWN_V = Vector(0, 0, -1)
UP_V = Vector(0, 0, 1)

BASE_ROTATION_V = Vector(1, 0, 0)

ZERO_R = Rotate(0, 0, 0)
