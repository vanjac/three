from vectorMath import Vector
from vectorMath import Rotate
import math

# test constructors and basic operations

a = Vector(1, 2, 3)
assert str(a) == str(a.getTuple())
assert a.x == 1 and a.y == 2 and a.z == 3

b = Vector(1, 2)
assert b.x == 1 and b.y == 2 and b.z == 0

assert a != b
a = Vector(1, 2, 0)
assert a == b

a = Vector(0, 0)
assert a.isZero()

a = a.setX(4).setY(5).setZ(6)
assert a.x == 4 and a.y == 5 and a.z == 6

b = Vector(1, 2, 3)

c = 5 * (-a + b)
assert c.x == -15 and c.y == -15 and c.z == -15

c *= a
c /= b
assert c.x == -60 and c.y == -37.5 and c.z == -30

# test vector math

a = Vector(3, 5, 7)
b = Vector(2, 4, 6)
result = a.dot(b)
assert result == 68

a = Vector(1, 0, 0)
b = Vector(0, 5, 0)
assert a.orthogonal(b)

a = Vector(2, 0, 0)
b = Vector(0, 3, 0)
c = Vector(1, 0, 0)
d = Vector.normal(a, b, c)
assert d == Vector(0, 0, 1)

a = Vector(3, 5, 7)
b = Vector(5, 7, 9)
c = a.lerp(b, 0.5)
assert c == Vector(4, 6, 8)

a = Vector(3, 4, 12)
assert a.magnitude() == 13
assert a.magnitudeSquare() == 13**2
a = a.normalize()
assert a.magnitude() == 1

a = Vector(4, 6, 15)
b = Vector(1, 2, 3)
assert a.distanceTo(b) == 13
assert b.distanceTo(a) == 13

a = Vector(5, 0, 0)
b = Vector(0, 6, 0)
assert math.degrees(a.angleBetween(b)) == 90
assert math.degrees(b.angleBetween(a)) == 90

# test 2d directions / rotations

a = Vector(3**.5, 1)
assert round(math.degrees(a.direction2())) == 30
b = Vector(5, 7, 9)
a = a + b
assert round(math.degrees(b.direction2Towards(a))) == 30
assert round(math.degrees(a.direction2Towards(b))) == 30 + 180




print("Done.")
