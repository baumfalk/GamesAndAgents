from itertools import izip
from math import floor, copysign
from api.vector2 import Vector2

sign = lambda x: int(copysign(1, x))


class line(object):
    def __init__(self, A, B, finite = True, covering = True):
        self.finite = finite
        self.covering = covering
        self.A = A
        self.B = B
        self.D = B - A                  # Total delta of the line.
        self.G = self.generate()

    def __iter__(self):
        return self.G

    def __eq__(self, other):
        return self.D.normalized().distance(other.D.normalized()) < 1E-9

    def next(self):
        self.G.next()

    def generate(self):
        """
            This function is a generator that returns grid coordinates along a line
        between points A and B.  It uses a floating-point version of the Bresenham
        algorithm, which is designed to be sub-pixel accurate rather than assuming
        the middle of each pixel.  This could most likely be optimized further using
        Bresenham's integer techniques.

        @param finite   You can specify a line that goes only between A or B, or
                        infinitely from A beyond B.
        @param covering Should all touched pixels be returned in the generator or
                        only one per major axis coordinate?
        """
        A = self.A
        B = self.B
        finite = self.finite
        covering = self.covering

        d = self.D
        if d.x == 0 and d.y == 0:
            yield (floor(A.x), floor(A.y))
            raise StopIteration

        if abs(d.x) >= abs(d.y):
            sy = d.y / abs(d.x)     # Slope along Y that was chosen.
            sx = sign(d.x)          # Step in the correct X direction.

            y = int(floor(A.y))     # Starting pixel, rounded.
            x = int(floor(A.x))
            e = A.y - float(y)      # Exact error calculated.

            while True:
                if finite and x == int(floor(B.x)):
                    break
                yield (x, y)

                p = e           # Store current error for reference.
                e += sy         # Accumulate error from slope.

                if e >= 1.0:    # Reached the next row yet?
                    e -= 1.0        # Re-adjust the error accordingly.

                    if covering:
                        if p+e < 1.0:   # Did the line go below the corner?
                            yield (x+sx, y)
                        elif p+e > 1.0:
                            yield (x, y+1)

                    y += 1          # Step the coordinate to next row.

                elif e < 0.0:   # Reached the previous row?
                    e += 1.0        # Re-adjust error accordingly.

                    if covering:
                        if p+e < 1.0:   # Did the line go below the corner?
                            yield (x, y-1)
                        elif p+e > 1.0:
                            yield (x+sx, y)

                    y -= 1          # Step the coordinate to previous row.

                x += sx         # Take then next step with x.

        else: # abs(d.x) < abs(d.y)

            sx = d.x / abs(d.y)     # Slope along Y that was chosen.
            sy = sign(d.y)          # Step in the correct X direction.

            x = int(floor(A.x))     # Starting pixel, rounded.
            y = int(floor(A.y))
            e = A.x - float(x)      # Exact error calculated.

            while True:
                if finite and y == int(floor(B.y)):
                    break
                yield (x, y)

                p = e           # Store current error for reference.
                e += sx         # Accumulate error from slope.

                if e >= 1.0:    # Reached the next row yet?
                    e -= 1.0        # Re-adjust the error accordingly.

                    if covering:
                        if p+e < 1.0:   # Did the line go below the corner?
                            yield (x, y+sy)
                        elif p+e > 1.0:
                            yield (x+1, y)

                    x += 1          # Step the coordinate to next column.

                elif e < 0.0:   # Reached the previous row?
                    e += 1.0        # Re-adjust error accordingly.

                    if covering:
                        if p+e < 1.0:   # Did the line go below the corner?
                            yield (x-1, y)
                        elif p+e > 1.0:
                            yield (x, y+sy)

                    x -= 1          # Step coordinate to the previous column.

                y += sy         # Go for another iteration with next Y.



class Wave(object):
    """
        Visibility "wave" helper that can calculate all visible cells from a
    single cell.  It starts from a specified point and "flood fills" cells that
    are visible in four different directions.  Each direction of the visibility
    wave is bounded by two lines, which are then rasterized in between.  If
    obstacles are encountered, the wave is split into sub-waves as necessary.
    """

    def __init__(self, (left, top, right, bottom), isBlocked, setVisible, usingLine = None):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

        self.isBlocked = isBlocked
        self.setVisible = setVisible
        self.usingLine = usingLine

    def calculateStartPointX(self, p, w):
        step = 0.0 if (w[0] - p.x) > 0.0 else 1.0
        if int(p.y) < w[1]:
            corner = Vector2(w[0]+step, w[1]+0.0)
        else:
            corner = Vector2(w[0]+1.0-step, w[1]+0.0)

        slope = (corner-p).normalized()
        scale = (w[0]+0.5 - p.x) / slope.x
        return p + slope * scale, corner

    def calculateFinishPointX(self, p, w):
        step = 1.0 if (w[0] - p.x) > 0.0 else 0.0
        if int(p.y) <= w[1]:
            corner = Vector2(w[0]+step, w[1]+1.0)
        else:
            corner = Vector2(w[0]+1.0-step, w[1]+1.0)

        slope = (corner-p).normalized()
        scale = (w[0]+0.5 - p.x) / slope.x
        return p + slope * scale, corner

    def calculateStartPointY(self, p, w):
        step = 0.0 if (w[1] - p.y) > 0.0 else 1.0
        if int(p.x) < w[0]:
            corner = Vector2(w[0]+0.0, w[1]+step)
        else:
            corner = Vector2(w[0]+0.0, w[1]+1.0-step)

        slope = (corner-p).normalized()
        scale = (w[1]+0.5 - p.y) / slope.y
        return p + slope * scale, corner

    def calculateFinishPointY(self, p, w):
        step = 1.0 if (w[1] - p.y) > 0.0 else 0.0
        if int(p.x) <= w[0]:
            corner = Vector2(w[0]+1.0, w[1]+step)
        else:
            corner = Vector2(w[0]+1.0, w[1]+1.0-step)

        slope = (corner-p).normalized()
        scale = (w[1]+0.5 - p.y) / slope.y
        return p + slope * scale, corner

    def xwave_internal(self, p, upper, lower, direction):
        """Propagate a visibility wave along one direction with X-major axis."""

        for (ux, uy), (lx, ly) in izip(upper, lower):
            assert ux == lx, "{} != {}".format(ux, lx)
            x = ux
            # If the upper and lower bounds are switched, just swap them.
            if uy > ly: uy, ly = ly, uy

            # Check if the wave has stepped out of bounds.
            if x < self.left: break
            if x >= self.right: break

            waves = []
            visible = []
            blocks = False

            # Now iterate through all the pixels in this column.
            for y in range(max(uy, self.top), min(ly+1, self.bottom)):

                # If a free cell is encountered, store it for later.
                if not self.isBlocked(x, y):
                    visible.append((x, y))
                # If the cell is blocked, then we keep track of the entire span of cells.
                else:
                    blocks = True
                    if visible:
                        waves.append(visible)
                        visible = []
                    else:
                        pass

            # Now we have a list of all the visible spans of cells, for sub-waves.
            if visible:
                waves.append(visible)

            # Split the wave into sub-waves if there were blocks.
            if blocks:
                for i, w in enumerate(waves):
                    # Calculate the coordinates of the start and end of the new wave.
                    w0, d0 = self.calculateStartPointX(p, w[0])
                    wn, dn = self.calculateFinishPointX(p, w[-1])
                    u = w0 - p
                    l = wn - p
                    u = u / abs(u.x)
                    l = l / abs(l.x)

                    w0 += u
                    wn += l

                    # Sub-pixel drift may cause the new lines to diverge.
                    if u.y > lower.D.y: continue
                    if l.y < upper.D.y: continue

                    # If this wave cell is the first or last, we use the exact same line equation.
                    if i>0 or w[0][1] > max(uy, self.top):
                        uppr = line(w0, w0+u, finite = False, covering = False)
                        if self.usingLine: self.usingLine(d0, u)
                    else:
                        uppr = upper
                    if i<len(waves)-1 or w[-1][1] < min(ly+1, self.bottom)-1:
                        lowr = line(wn, wn+l, finite = False, covering = False)
                        if self.usingLine: self.usingLine(dn, l)
                    else:
                        lowr = lower

                    # Now recursively handle this case, propagating the sub-wave further.
                    if not (uppr == lowr):
                        for x, y in w:
                            self.setVisible(x, y)
                        self.xwave_internal(p, uppr, lowr, direction)
                return

            # No blockages for this column, mark all cells visible.
            else:
                for x, y in visible:
                    self.setVisible(x, y)

    def ywave_internal(self, p, upper, lower, direction):
        for (ux, uy), (lx, ly) in izip(upper, lower):
            assert uy == ly, "{} != {}".format(uy, ly)
            y = uy

            if ux > lx: ux, lx = lx, ux

            if y < self.top: break
            if y >= self.bottom: break

            waves = []
            visible = []
            blocks = False
            for x in range(max(ux, self.left), min(lx+1, self.right)):
                if self.isBlocked(x, y):
                    blocks = True
                    if visible:
                        waves.append(visible)
                        visible = []
                    else:
                        pass
                else:
                    visible.append((x,y))

            if visible:
                waves.append(visible)

            if blocks:
                for i, w in enumerate(waves):
                    w0, d0 = self.calculateStartPointY(p, w[0])
                    wn, dn = self.calculateFinishPointY(p, w[-1])
                    u = w0 - p
                    l = wn - p
                    u = u / abs(u.y)
                    l = l / abs(l.y)

                    # Sub-pixel drift may cause the new lines to diverge.
                    if u.x > lower.D.x: continue
                    if l.x < upper.D.x: continue

                    w0 += u
                    wn += l
                    if i>0 or w[0][0] > max(ux, self.left):
                        uppr = line(w0, w0+u, finite = False, covering = False)
                        if self.usingLine: self.usingLine(d0, u)
                    else:
                        uppr = upper
                    if i<len(waves)-1 or w[-1][0] < min(lx+1, self.right)-1:
                        lowr = line(wn, wn+l, finite = False, covering = False)
                        if self.usingLine: self.usingLine(dn, l)
                    else:
                        lowr = lower

                    if not (uppr == lowr):
                        for x, y in w:
                            self.setVisible(x, y)
                        self.ywave_internal(p, uppr, lowr, direction)
                return

            # No blockages in this row, just mark all visible.
            else:
                for x, y in visible:
                    self.setVisible(x, y)

    def compute(self, p):
        """Propagate four visibility waves, along X and Y both positive and negative."""

        if self.isBlocked(int(p.x), int(p.y)):
            return

        upper = line(p, p+Vector2(+1.0, -1.0), finite = False, covering = False)
        lower = line(p, p+Vector2(+1.0, +1.0), finite = False, covering = False)
        self.xwave_internal(p, upper, lower, Vector2(+1.0, 0.0))

        upper = line(p, p+Vector2(-1.0, -1.0), finite = False, covering = False)
        lower = line(p, p+Vector2(-1.0, +1.0), finite = False, covering = False)

        upper.next(), lower.next()
        self.xwave_internal(p, upper, lower, Vector2(-1.0, 0.0))

        upper = line(p+Vector2(-1.0, -1.0), p+Vector2(-2.0, -2.0), finite = False, covering = False)
        lower = line(p+Vector2(+1.0, -1.0), p+Vector2(+2.0, -2.0), finite = False, covering = False)
        self.ywave_internal(p, upper, lower, Vector2(0.0, -1.0))

        upper = line(p+Vector2(-1.0, +1.0), p+Vector2(-2.0, +2.0), finite = False, covering = False)
        lower = line(p+Vector2(+1.0, +1.0), p+Vector2(+2.0, +2.0), finite = False, covering = False)
        self.ywave_internal(p, upper, lower, Vector2(0.0, +1.0))

