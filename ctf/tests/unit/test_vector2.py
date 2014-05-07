import math
import unittest
from api.vector2 import Vector2

def isSimilar(a, b, e = 0.00001):
    if isinstance(a, Vector2):
        assert isinstance(b, Vector2)
        return (math.fabs(a.x - b.x) <= e) and (math.fabs(a.y - b.y) <= e)
    return math.fabs(a - b) <= e


class Vector2Tests(unittest.TestCase):

    def test_initialization(self):
        v = Vector2(2, 4)
        assert v.x == 2.0
        assert v.y == 4.0

    def test_equality(self):
        v = Vector2(-3.9, 2.2)
        assert v == Vector2(-3.9, 2.2)
        assert Vector2(-3.9, 2.2) == v
        u = Vector2(-3.9, 2.2)
        assert v == u
        assert v != Vector2(-3.8, 2.2)
        assert Vector2(-3.8, 2.2) != v
        assert v != Vector2(-3.9, 2.3)
        assert Vector2(-3.9, 2.3) != v
        r = Vector2(-3.8, 2.2)
        assert v != r
        s = Vector2(-3.9, 2.3)
        assert v != s

    def test_constants(self):
        assert Vector2.ZERO == Vector2(0.0, 0.0)
        assert Vector2.UNIT_X == Vector2(1.0, 0.0)
        assert Vector2.UNIT_Y == Vector2(0.0, 1.0)
        assert Vector2.NEGATIVE_UNIT_X == Vector2(-1.0, 0.0)
        assert Vector2.NEGATIVE_UNIT_Y == Vector2(0.0, -1.0)
        assert Vector2.UNIT_SCALE == Vector2(1.0, 1.0)

    def test_pos(self):
        v = Vector2(-3.9, 2.2)
        assert +v == Vector2(-3.9, 2.2)

    def test_neg(self):
        v = Vector2(-3.9, 2.2)
        assert -v == Vector2(3.9, -2.2)

    def test_add(self):
        assert isSimilar(Vector2(-3.9, 2.2) + Vector2(1, 4), Vector2(-2.9, 6.2))
        v = Vector2(-3.9, 2.2)
        v += Vector2(1, 4)
        assert isSimilar(v, Vector2(-2.9, 6.2))

    def test_add_float(self):
        assert isSimilar(Vector2(-3.9, 2.2) + 1.3, Vector2(-2.6, 3.5))
        # assert isSimilar(1.3 + Vector2(-3.9, 2.2), Vector2(-2.6, 3.5)) this isn't allowed

    def test_sub(self):
        assert isSimilar(Vector2(-2.9, 6.2) - Vector2(-3.9, 2.2), Vector2(1, 4))
        v = Vector2(-2.9, 6.2)
        v -= Vector2(-3.9, 2.2)
        assert isSimilar(v, Vector2(1, 4))

    def test_sub_float(self):
        assert isSimilar(Vector2(-3.9, 2.2) - 1.3, Vector2(-5.2, 0.9))
        # assert isSimilar(1.3 - Vector2(-3.9, 2.2), Vector2(5.2, -0.9)) this isn't allowed

    def test_mul(self):
        assert isSimilar(Vector2(-3.9, 2.2) * 1.1, Vector2(-4.29, 2.42))
        assert isSimilar(1.1 * Vector2(-3.9, 2.2), Vector2(-4.29, 2.42))
        v = Vector2(-3.9, 2.2)
        v *= 1.1
        assert isSimilar(v, Vector2(-4.29, 2.42))

    def test_div(self):
        assert isSimilar(Vector2(-4.29, 2.42) / 1.1, Vector2(-3.9, 2.2))
        v = Vector2(-4.29, 2.42)
        v /= 1.1
        assert isSimilar(v, Vector2(-3.9, 2.2))

    def test_length(self):
        assert Vector2(0, 0).length() == 0
        assert isSimilar(Vector2(1, 0).length(), 1)
        assert isSimilar(Vector2(0, 1).length(), 1)
        assert isSimilar(Vector2(0.3, -0.4).length(), 0.5)

    def test_squaredLength(self):
        assert Vector2(0, 0).squaredLength() == 0
        assert isSimilar(Vector2(1, 0).squaredLength(), 1)
        assert isSimilar(Vector2(0, 1).squaredLength(), 1)
        assert isSimilar(Vector2(0.3, -0.4).squaredLength(), 0.25)

    def test_distance(self):
        assert Vector2(0, 0).distance(Vector2(0, 0)) == 0
        assert Vector2(4, 3).distance(Vector2(4, 3)) == 0
        assert isSimilar(Vector2(3, 3).distance(Vector2(4, 3)), 1)
        assert isSimilar(Vector2(4, 4).distance(Vector2(4, 3)), 1)
        assert isSimilar(Vector2(4.3, 2.4).distance(Vector2(3.9, 2.1)), 0.5)

    def test_squaredDistance(self):
        assert Vector2(0, 0).squaredDistance(Vector2(0, 0)) == 0
        assert Vector2(4, 3).squaredDistance(Vector2(4, 3)) == 0
        assert isSimilar(Vector2(3, 3).squaredDistance(Vector2(4, 3)), 1)
        assert isSimilar(Vector2(4, 4).squaredDistance(Vector2(4, 3)), 1)
        assert isSimilar(Vector2(4.3, 2.4).squaredDistance(Vector2(3.9, 2.1)), 0.25)

    def test_dotProduct(self):
        assert Vector2(0, 0).dotProduct(Vector2(0, 0)) == 0
        assert Vector2(3, 9).dotProduct(Vector2(0, 0)) == 0
        assert Vector2(0, 0).dotProduct(Vector2(1, 2)) == 0
        assert Vector2(5, 4).dotProduct(Vector2(-4, 5)) == 0
        assert isSimilar(Vector2(2, 4).dotProduct(Vector2(3, -6)), -12) == 0

    def test_normalize(self):
        assert isSimilar(Vector2(3, 4).normalized(), Vector2(0.6, 0.8))
        v = Vector2(3, 4)
        v.normalize()
        assert isSimilar(v, Vector2(0.6, 0.8))

    def test_midPoint(self):
        assert isSimilar(Vector2(5, 2).midPoint(Vector2(-3, 4)), Vector2(1, 3))

    # def test_makeFloor(self):

    # def test_makeCeil(self):

    def test_perpendicular(self):
        assert isSimilar(Vector2(0, 0).perpendicular(), Vector2(0, 0))
        assert isSimilar(Vector2(3, 4).perpendicular(), Vector2(-4, 3))

    def test_crossProduct(self):
        assert Vector2(0, 0).crossProduct(Vector2(1, 2)) == 0
        assert Vector2(1, 2).crossProduct(Vector2(0, 0)) == 0
        assert Vector2(1, 2).crossProduct(Vector2(3, 4)) == -2

    # def test_randomDeviant(self):

    def test_isZeroLength(self):
        assert Vector2(0, 0).isZeroLength()
        assert not Vector2(1, 0).isZeroLength()

    # def test_reflect(self):

    def test_comparisons(self):
        assert not (Vector2(0,0) == None)
        assert Vector2(0,0) != "Hello world"
        assert Vector2(0,0) == Vector2(0,0) 
        assert Vector2(0,1) != Vector2(0,0)
        assert Vector2(1,0) != Vector2(0,0)

    def test_random(self):
        sum = Vector2.ZERO
        for i in range(1000):
            r = Vector2.random()
            assert r.x >= 0 and r.x <= 1
            assert r.y >= 0 and r.y <= 1
            sum += r
        assert isSimilar(sum / 1000, Vector2(0.5, 0.5), 0.1)

    def test_randomVectorInBox(self):
        sum = Vector2.ZERO
        for i in range(1000):
            r = Vector2.randomVectorInBox(Vector2(1, 2), Vector2(5, 10))
            assert r.x >= 1 and r.x <= 5
            assert r.y >= 2 and r.y <= 10
            sum += r
        assert isSimilar(sum / 1000, Vector2(3, 6), 0.25)

    def test_randomUnitVector(self):
        sum = Vector2.ZERO
        for i in range(1000):
            r = Vector2.randomUnitVector()
            assert isSimilar(r.length(), 1.0)
            sum += r
        assert isSimilar(sum / 1000, Vector2.ZERO, 0.1)

if __name__ == '__main__':
    unittest.main(verbosity = 2, failfast = False)
