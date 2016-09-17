__author__ = "vantjac"

import numbers
import math

# Based on JMath3d
    
CIRCLE = math.pi*2

def fixRotation(n):
    """
    Limit rotation to be between 0 and 2pi.
    """
    n = float(n)
    if n < 0:
        circles = math.ceil(-n / CIRCLE)
        n += circles * CIRCLE
    n = n % CIRCLE
    return n

def doubleTupleToString(t):
    """
    A tuple of 2 numbers as a string.
    """
    return numToStr(t[0]) + ',' + numToStr(t[1])

def tripleTupleToString(t):
    """
    A tuple of 3 numbers as a string.
    """
    return numToStr(t[0]) + ',' + \
        numToStr(t[1]) + ',' + \
        numToStr(t[2])

def numToStr(num):
    if num % 1.0 == 0.0:
        return str(int(num))
    else:
        return "{0:.3f}".format(num)

def isclose(a, b, rel_tol=1e-9, abs_tol=1e-9):
    """
    Based on https://www.python.org/dev/peps/pep-0485/
    
    Taken from https://github.com/PythonCHB/close_pep/blob/master/isclose.py
    
    Python 3.5 has this, but 3.4 doesn't.
    I changed the default value of abs_tol, and also removed some checking for
    special cases that will never appear here.
    """
    if a == b:
        return True
    if math.isinf(abs(a)) or math.isinf(abs(b)):
        return False
    
    diff = abs(b - a)
    return (((diff <= abs(rel_tol * b)) or
             (diff <= abs(rel_tol * a))) or
            (diff <= abs_tol))

def calculatePlaneConstants(point, normal):
    """
    Given a point on a plane and its normal, calculate the constants of the
    equation: ax + by + cz + d = 0. Return a tuple of 4 numbers: (a, b, c, d).
    """
    return (normal.x, normal.y, normal.z, -point.dot(normal))

def rotatePlane(point, normal, rotate):
    """
    Given a point on a plane, its normal, and a rotation about the origin,
    return the constants of the plane equation, like in
    ``calculatePlaneConstants``.
    """
    point = point.rotate(rotate)
    normal = normal.rotate(rotate)
    return calculatePlaneConstants(point, normal)

def boxesIntersect(boxA, boxB):
    """
    Check if 2 boxes intersect, each defined by a tuple of 2 Vectors describing
    2 opposite corners of the box. Having the sides, edges, or corners touch
    counts as NOT intersecting.
    """
    return rangesIntersect(boxA[0].x, boxA[1].x,
                           boxB[0].x, boxB[1].x) \
        and rangesIntersect(boxA[0].y, boxA[1].y,
                            boxB[0].y, boxB[1].y) \
        and rangesIntersect(boxA[0].z, boxA[1].z,
                            boxB[0].z, boxB[1].z)

def rangesIntersect(a1, a2, b1, b2):
    """
    Check if 2 ranges, from a1 to a2 and from b1 to b2, intersect. Having their
    edges touch counts as NOT intersecting.
    """
    if a1 > a2:
        a1 = temp
        a1 = a2
        a2 = temp
    if b1 > b2:
        b1 = temp
        b1 = b2
        b2 = temp
    return not (a2 <= b1 or a1 >= b2)

class Vector:
    """
    An immutable 2-dimensional or 3-dimensional vector.
    """
    
    @staticmethod
    def normal(v1, v2, v3):
        """
        Compute the normal unit-vector of a triangle, with vertices in
        counter-clockwise order.
        """
        a = v2 - v1
        b = v3 - v1
        unit = a.cross(b)
        unit = unit.normalize()
        return unit

    @staticmethod
    def fromTuple(t):
        """
        Create a Vector from a tuple of 3 numbers.
        """
        return Vector(t[0], t[1], t[2])
    

    def __init__(self, x, y, z = 0):
        """
        Create a vector from 2 or 3 numbers, which are automatically converted
        to floats.
        """
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

    def isClose(self, other):
        """
        Return True if the Vectors are close enough that any differences are
        probably a floating point math error.
        """
        return isclose(self.x, other.x) \
            and isclose(self.y, other.y) \
            and isclose(self.z, other.z)

    def getTuple(self):
        """
        Return a tuple of 3 numbers for the Vector.
        """
        return (self.x, self.y, self.z)
    
    def isZero(self):
        """
        Check if the vector is at (0, 0, 0). Same as:
        ``vector == Vector(0, 0, 0)``.
        """
        return self.x == 0 and self.y == 0 and self.z == 0

    def isCloseToZero(self):
        """
        Check if the vector is close to (0, 0, 0). Same as:
        ``vector.isClose( Vector(0, 0, 0) )``.
        """
        return self.isClose(ZERO_V)
    
    def setX(self, newX):
        """
        Return a copy of this vector with a new x value.
        """
        return Vector(newX, self.y, self.z)
        
    def setY(self, newY):
        """
        Return a copy of this vector with a new y value.
        """
        return Vector(self.x, newY, self.z)
        
    def setZ(self, newZ):
        """
        Return a copy of this vector with a new z value.
        """
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
        """
        Return the dot product of the two vectors.
        """
        return self.x * v.x + self.y * v.y + self.z * v.z
    
    def orthogonal(self, v):
        """
        Return true if this vector is orthogonal (at a right angle) to another
        vector.
        """
        return self.dot(v) == 0

    def cross(self, v):
        """
        Return the cross product of the two vectors.
        """
        newX = self.y * v.z - self.z * v.y;
        newY = self.z * v.x - self.x * v.z;
        newZ = self.x * v.y - self.y * v.x;
        return Vector(newX, newY, newZ)
    
    def lerp(self, v, amount):
        """
        With amount = 0, returns this vector.
        With amount = 1, returns the other vector.
        With amount = 0.5, returns the halfway point.
        With other values in that range, returns interpolated values.
        With values outside of that range, returns extrapolated values.
        """
        difference = v - self
        return self + (difference * amount)

    def magnitude(self):
        """
        Get the magnitude of the vector (distance from (0, 0, 0).
        """
        return math.sqrt(self.magnitudeSquare())

    def magnitudeSquare(self):
        """
        Get the square of the magnitude of the vector. This is faster to
        calculate than ``magnitude()`` and is preferred for comparisons.
        """
        return self.x ** 2.0 + self.y ** 2.0 + self.z ** 2.0
    
    def setMagnitude(self, newMag):
        """
        Return a new vector with the same direction as this one but a different
        magnitude.
        """
        currentMag = self.magnitude()
        if currentMag == 0:
            return self
        return self * (newMag / currentMag)
    
    def limitMagnitude(self, maxMag):
        """
        If the magnitude of this vector is greater than ``maxMax``, return a new
        vector with the same direction as this one and a magnitude of
        ``maxMag``. Otherwise return this vector.
        """
        if self.magnitudeSquare() > maxMag**2:
            return self.setMagnitude(maxMag)
        else:
            return self

    def normalize(self):
        """
        Return a new vector with the same direction as this one and a magnitude
        of 1. Same as ``vector.setMagnitude(1.0)``.
        """
        return self.setMagnitude(1.0)
    
    def distanceTo(self, v):
        """
        Return the distance from the end of one vector to another.
        """
        return (self - v).magnitude()

    def angleBetween(self, v):
        """
        Return the angle at the origin between 2 vectors.
        """
        try:
            return abs(
                math.acos( self.dot(v) / (self.magnitude() * v.magnitude()) ) )
        except ValueError as err:
            # vectors are in opposite directions or same direction
            v1Normal = self.normalize()
            v2Normal = v.normalize()
            if v1Normal.isClose(v2Normal):
                return 0 # same direction
            elif v1Normal.isClose(-v2Normal):
                return math.pi # opposite direction
            else:
                # something went wrong
                raise err

    def direction2(self):
        """
        Return the 2 dimensional direction of the vector as a rotation
        counter-clockwise from positive-x.
        """
        n = math.atan2(self.y, self.x)
        return fixRotation(n)
        
    def direction2Towards(self, v):
        """
        Return the 2-dimensional direction from the end of this vector towards
        another.
        """
        return (v - self).direction2()
    
    def rotate2(self, amount):
        """
        Return a copy of this vector rotated in 2 dimensions by a specified
        angle.
        """
        sinX = math.sin(amount)
        cosX = math.cos(amount)
        return Vector( self.x * cosX - self.y * sinX,
                       self.y * cosX + self.x * sinX,
                       self.z )
    
    def rotate2Around(self, amount, center):
        """
        Return a copy of this vector rotated in 2 dimensions around a specified
        point.
        """
        return (self - center).rotate2(amount) + center
    
    def move2(self, direction, amount):
        """
        ``amount`` is a 2d vector describing movement, which is rotated by
        ``direction`` and added to this vector.
        """
        amount = amount.rotate2(direction)
        return self + amount
    
    def homogeneousTo2d(self):
        """
        Convert the homogeneous coordinates of a 2d vector (in the form of a 3d
        vector) to a regular 2d vector.
        """
        return Vector(self.x / self.z, self.y / self.z)
    
    def rotation(self):
        """
        Get the direction of this 3d vector as a Rotation.
        The rotation will not have a "roll" or x-rotation component.
        """
        xy = Vector(self.x, self.y)
        xyz = Vector(xy.magnitude(), self.z)
        yRot = xyz.direction2()
        zRot = xy.direction2()
        return Rotate(0, yRot, zRot);
    
    def directionTowards(self, v):
        """
        Return the direction from the end of this vector towards another, as a
        unit-vector.
        """
        return (v - self).normalize()

    def rotate(self, amount):
        """
        Return a copy of this vector rotated by the specified Rotate.
        """
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
        """
        Similar to ``rotate()``, but rotations on individual axes are done in
        a different order. For ``rotate()``, the x axis is rotated first,
        followed by the y axis and the z axis. ``inverseRotate()`` has the
        opposite order. This is useful for undoing rotations;
        ``vector.rotate(r).inverseRotate(-r)`` returns the original vector.
        """
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
        """
        Rotate the vector around a specified center point.
        """
        return (self - center).rotate(amount) + center
    
    def move(self, direction, amount):
        """
        ``amount`` is a 2d vector describing movement, which is rotated by
        ``direction`` and added to this vector.
        """
        amount = amount.rotate(direction)
        return self + amount

class Rotate:
    """
    An immutable rotation in 3d space.
    """
    
    @staticmethod
    def fromTuple(t):
        return Rotate(t[0], t[1], t[2])

    def __init__(self, x, y, z):
        """
        Create a Rotate by specifying rotation around the x, y, and z axes
        (applied in that order).
        """
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
        """
        Return a tuple of 3 numbers for the Rotate - the rotations around the
        x, y, and z axes.
        """
        return (self.x, self.y, self.z)
    
    def isZero(self):
        """
        Check if this is a zero rotation.
        """
        return self.x == 0 and self.y == 0 and self.z == 0
    
    def setX(self, newX):
        """
        Return a copy of this Rotate with a new x value.
        """
        return Rotate(newX, self.y, self.z)
        
    def setY(self, newY):
        """
        Return a copy of this Rotate with a new y value.
        """
        return Rotate(self.x, newY, self.z)
        
    def setZ(self, newZ):
        """
        Return a copy of this Rotate with a new z value.
        """
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
        """
        Return a copy of this Rotate, rotated by a specified rotation.
        """
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
