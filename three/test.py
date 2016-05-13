from vectorMath import Vector

a = Vector(1, 2, 3)
assert str(a) == str(a.getTuple())
assert a.getX() == 1 and a.getY() == 2 and a.getZ() == 3

b = Vector(1, 2)
assert b.getX() == 1 and b.getY() == 2 and b.getZ() == 0

assert a != b
a = Vector(1, 2, 0)
assert a == b


a = Vector(0, 0)
assert a.isZero()

a = a.setX(4).setY(5).setZ(6)
assert a.getX() == 4 and a.getY() == 5 and a.getZ() == 6

b = Vector(1, 2, 3)

c = 5 * (-a + b)
assert c.getX() == -15 and c.getY() == -15 and c.getZ() == -15

c *= a
c /= b
assert c.getX() == -60 and c.getY() == -37.5 and c.getZ() == -30





print("Done.")
