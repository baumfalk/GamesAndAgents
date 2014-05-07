
import math
import svgwrite

from api.vector2 import Vector2


class Drawing(svgwrite.Drawing):

    def __init__(self, filename, width, height):
        super(Drawing, self).__init__(filename=filename, width='100%', height='100%')
        self.viewbox(0, 0, width, height)

        s = self.script(content="""
            function trace(str) {
                console.log(str);
            }
        """)
        self.add(s)

        c = self.style(content="""
            rect:hover { fill: red; }
        """)
        self.add(c)


    def pixel(self, (x,y), color, margin=0):
        d = self.rect(insert=(x+margin,y+margin), size=(1-margin*2, 1-margin*2), fill=color)
        # d['onmouseover'] = 'trace("(%i,%i)")' % (x,y)
        self.add(d)


    def blob(self, (x,y), color, size=0.2):
        s = self.circle(center=(x, y), r=size, fill=color)
        self.add(s)


    def arrow(self, (x,y), (z,w), color, width=0.5, shrink=3.5):
        ## create arrow head
        marker = self.marker(orient='auto', markerUnits='strokeWidth', insert=(1.4, 2.0), size=(4.0, 4.0), fill=color)
        marker.add(self.polyline([(0.0, 0.0), (4.0, 2.0), (0.0, 4.0), (1.4, 2.0)]))
        self.defs.add(marker)

        ## make the arrow a little bit shorter
        v1 = Vector2(x, y)
        v2 = Vector2(z, w)
        v2 -= (v2 - v1).normalized() * shrink * width

        ## create arrow and add to this Drawing
        g = self.g(stroke=color, fill=color)
        l = self.line(v1, v2, stroke_width=width)
        l['marker-end'] = marker.get_funciri()
        g.add(l)
        self.add(g)


    def ray(self, (x,y), (z,w), color, width=0.5):
        l = self.line((x, y), (z, w), stroke=color, stroke_width=width)
        self.add(l)


    def gradient(self, v):
        colors = [
              (250, 238, 188),
              (245, 148,   8),
              (136, 177, 255),
              ( 27,   7, 115),

            # ( 100,  95,  75),
            # (  98,  59,   3),
            # (  25,  50,  75),
            # (   0,   0,   0),
        ]

        v *= len(colors) - 1
        i = math.floor(v)
        k = v - i
        return 'rgb(%i, %i, %i)' % tuple([a*(1.0-k)+b*(0.0+k) for a, b in zip(colors[int(i)], colors[int(i)+1])])
