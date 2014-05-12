#==============================================================================
# This file is part of The AI Sandbox.
# Copyright (c) 2007-2013, AiGameDev.com
#==============================================================================

"""Utility class that models a 2D vector.
"""

import random
import math


class Vector2(object):
    """A 2D Vector class.
    """

    def __init__(self, x, y):
        """Initialize the Vector2 from two floats.

        Args:
            x: The value to set for X
            y: The value to set for Y
        """
        super(Vector2, self).__init__()
        self.x = float(x)                      #: The x parameter
        self.y = float(y)                      #: The y parameter

    def __str__(self):
        """Return a string representation of the Vector2.
        """
        return "({}, {})".format(self.x, self.y)

    def __repr__(self):
        """Return a string representation of the Vector2.
        """
        return "Vector2({}, {})".format(self.x, self.y)

    def __iter__(self):
        return iter([self.x, self.y])

    def __eq__(self, other):
        """Return True if two Vector2 objects are equivalent (exact floating point comparisons).

        Args:
            other: The other Vector2 object
        """
        return other and isinstance(other, Vector2) and (self.x == other.x) and (self.y == other.y)

    def __ne__(self, other):
        """Return True if two Vector2 objects are not equivalent (exact floating point comparisons).

        Args:
            other: The other Vector2 object
        """
        return not other or not isinstance(other, Vector2) or (self.x != other.x) or (self.y != other.y)

    def __add__(self, other):
        """Return the result from adding one Vector2 to another Vector2.
        This also supports adding a float to a Vector2.

        Args:
            other: Either another Vector2 object, or a numerical value
        """
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        else:
            return Vector2(self.x + other, self.y + other)
 
    def __sub__(self, other):
        """Return the result from subtracting one Vector2 from another Vector2.
        This also supports adding a float to a Vector2.

        Args:
            other: Either another Vector2 object, or a numerical value
        """
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        else:
            return Vector2(self.x - other, self.y - other)

    def __mul__(self, other):
        """Return the result from multiplying a Vector2 by a scalar.

        Args:
            other: The value to multiple this vector's X and Y with
        """
        return Vector2(self.x * float(other), self.y * float(other))

    def __rmul__(self, other):
        """Return the result from multiplying a Vector2 by a scalar.

        Args:
            other: The value to multiple this vector's X and Y with
        """
        return Vector2(self.x * float(other), self.y * float(other))

    def __truediv__(self, other):
        """Return the result from dividing a Vector2 by a scalar.

        Args:
            other: The value by which this vector is divided by
        """
        return Vector2(self.x / float(other), self.y / float(other))
    __div__ = __truediv__

    def __pos__(self):
        """Return the result of the unary + operator.
        """
        return Vector2(self.x, self.y)

    def __neg__(self):
        """Return the result of the unary negate operator.
        """
        return Vector2(-self.x, -self.y)


    def length(self):
        """Return the length of the Vector2.
        """
        return math.sqrt(self.x * self.x + self.y * self.y)

    def squaredLength(self):
        """Return the square of the length of the Vector2.
        """
        return self.x * self.x + self.y * self.y

    def distance(self, other):
        """Return the distance between two vectors. E.g. `d = u.distance(v);`

        Args:
            other: The position to which we want to calculate the distance
        """
        return (other - self).length()

    def squaredDistance(self, other):
        """Return the square of the distance between two vectors.

        Args:
            other: The position to which we want to calculate the square distance
        """
        return (other - self).squaredLength()

    def dotProduct(self, other):
        """Return the dot product of two vectors.

        Args:
            other: The other vector used to calculate the dot product
        """
        return self.x * other.x + self.y * other.y

    def normalize(self):
        """Normalize a Vector2 in place. The Vector2 cannot be the zero vector.
        """
        d = self.length()
        assert d != 0
        self.x /= d
        self.y /= d

    def normalized(self):
        """Return a normalized copy of the Vector2. The Vector2 cannot be the zero vector.
        """
        d = self.length()
        assert d != 0
        return self / d

    def midPoint(self, other):
        """Return a midpoint between two vectors.

        Args:
            other: The other vector used for the mid point calculation
        """
        return 0.5 * (self + other)

    def perpendicular(self):
        """Return a vector perpendicular to the current vector.
        """
        return Vector2(-self.y, self.x)

    def crossProduct(self, other):
        """Return the cross product of two vectors.

        Args:
            other: The other vector used to calculate the crossproduct
        """
        return self.x * other.y - self.y * other.x

    def isZeroLength(self):
        """Return True if the Vector2 is zero length.
        """
        return self.squaredLength() < 0.001


    @staticmethod
    def random():
        """Generate a random vector within in [(0, 0), (1, 1)) 
        """
        return Vector2(random.random(), random.random())

    @staticmethod
    def randomVectorInBox(min, max):
        """Generate a random vector within a box region. This uses the python random module as the random generator.
        """
        return Vector2(random.random() * (max.x - min.x) + min.x, random.random() * (max.y - min.y) + min.y)
    
    @staticmethod
    def randomUnitVector():
        """Generate a random unit vector with within a box region. This uses the python random module as the random generator. 
        """
        angle = 2 * math.pi * random.random()
        return Vector2(math.cos(angle), math.sin(angle))


Vector2.ZERO            = Vector2( 0.0,  0.0)  #: The Zero vector.
Vector2.UNIT_X          = Vector2( 1.0,  0.0)  #: The unit X vector.
Vector2.UNIT_Y          = Vector2( 0.0,  1.0)  #: The unit Y vector.
Vector2.NEGATIVE_UNIT_X = Vector2(-1.0,  0.0)  #: The negative unit X vector.
Vector2.NEGATIVE_UNIT_Y = Vector2( 0.0, -1.0)  #: The negative unit Y vector.
Vector2.UNIT_SCALE      = Vector2( 1.0,  1.0)  #: The unit scale vector.

