#==============================================================================
# This file is part of The AI Sandbox.
# Copyright (c) 2007-2013, AiGameDev.com
#==============================================================================


class Color(object):

    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


    def __eq__(self, other):
        return isinstance(other, Color) and (self.r, self.g, self.b, self.a) == (other.r, other.g, other.b, other.a)


    def __ne__(self, other):
        return isinstance(other, Color) and (self.r, self.g, self.b, self.a) != (other.r, other.g, other.b, other.a)
