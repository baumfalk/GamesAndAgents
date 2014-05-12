import math
import itertools

from api.commander import Commander
from api.vector2 import Vector2

from PySide import QtGui, QtCore

DEFAULT_SCALE = 15


def square(x):
    return x * x


class VisualizerWindow(QtGui.QMainWindow):

    def __init__(self, commander, vertical = False):

        ## first initialise the QCoreApplication if there is no instance
        self.qtApp = None

        if not QtCore.QCoreApplication.instance():
            self.qtApp = VisualizerApplication()
        super(VisualizerWindow, self).__init__()

        if self.qtApp is None:
            self.moveToThread(QtCore.QCoreApplication.instance().thread())

        self.commander = commander
        self.vertical = vertical
        self.drawBots = True

        self.levelWidth = self.commander.level.width
        self.levelHeight = self.commander.level.height

        if not self.vertical:
            # Always use a size multiple of 16 for video encoding purposes.
            self.width = math.ceil(self.levelWidth * DEFAULT_SCALE / 16.0) * 16
            self.height = math.ceil(self.levelHeight * DEFAULT_SCALE / 16.0) * 16
            self.resize(self.width, self.height)
        else:
            self.resize(self.levelHeight * DEFAULT_SCALE, self.levelWidth * DEFAULT_SCALE)

        self.settings = QtCore.QSettings("visualizer.cfg", QtCore.QSettings.IniFormat)
        if self.settings.contains("window/geometry") and self.settings.contains("window/state"):
            self.setWindowFlags(QtCore.Qt.WindowFlags(int(self.settings.value("window/flags"))))
            self.restoreGeometry(QtCore.QByteArray.fromHex(self.settings.value("window/geometry")))
            self.restoreState(QtCore.QByteArray.fromHex(self.settings.value("window/state")))

        # self.center()
        self.setWindowTitle('Capture The Flag')
        self.createRenderTarget()
        self.show()

        if not self.qtApp:
            self.updateTimer = QtCore.QTimer()
            self.updateTimer.timeout.connect(self.update)
            self.updateTimer.start(100)


    def createRenderTarget(self):
        self.target = QtGui.QPixmap(self.width, self.height)
        self.dirty = True


    def update(self):
        super(VisualizerWindow, self).update()
        if self.qtApp:
            self.qtApp.processEvents()


    def getMouseCoordinates(self):
        cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        inverse, ok = self.paint.transform().inverted()
        x, y = inverse.map(cursor.x(), cursor.y())
        return Vector2(x, y)


    def keyPressEvent(self, e):
        super(VisualizerWindow, self).keyPressEvent(e)

        if hasattr(self.commander, 'keyPressHook'):
            self.commander.keyPressHook(self, e)
            self.dirty = True
            self.update()


    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def resizeEvent(self, event):
        super(VisualizerWindow, self).resizeEvent(event)
        newSize = self.size()
        if newSize.width() == self.width and newSize.height() == self.height:
            return

        if newSize.width() != self.width:
            self.width = newSize.width()
        if newSize.height() != self.height:
            self.height = newSize.height()

        self.createRenderTarget()


    def paintEvent(self, e):
        super(VisualizerWindow, self).paintEvent(e)

        self.paint = QtGui.QPainter()

        if self.dirty is True:
            self.dirty = False
            self.target.fill(QtCore.Qt.black)
            self.paint.begin(self.target)
            self.setupPainter()
            self.drawWorld()
            self.paint.end()

        self.paint.begin(self)
        self.paint.drawPixmap(0, 0, self.target)
        self.setupPainter()
        self.drawGame()
        self.paint.end()
        self.paint = None


    def saveSettings(self):
        self.settings.setValue("window/geometry", self.saveGeometry().toHex())
        self.settings.setValue("window/state", self.saveState().toHex())
        self.settings.setValue("window/flags", int(self.windowFlags()))


    def setupPainter(self):
        self.paint.setRenderHint(QtGui.QPainter.Antialiasing, True)
        # self.paint.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        # self.paint.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        if self.vertical:
            self.paint.translate(50.0, 0.0)
            self.paint.rotate(90.0)
            # May need to stretch the canvas if the window was resized.
        else:
            self.paint.scale(float(self.width) / float(self.levelWidth),
                             float(self.height) / float(self.levelHeight))


    def drawWorld(self):
        if hasattr(self.commander, 'preWorldHook'):
            self.commander.preWorldHook(self)

        for i, j in itertools.product(range(self.levelWidth), range(self.levelHeight)):
            if self.commander.level.blockHeights[i][j] == 1:
                self.drawPixel((i, j), QtGui.qRgb(101, 91, 80))
            elif self.commander.level.blockHeights[i][j] >= 2:
                self.drawPixel((i, j), QtGui.qRgb(47, 44, 32))

        if hasattr(self.commander, 'postWorldHook'):
            self.commander.postWorldHook(self)


    def drawGame(self):
        if hasattr(self.commander, 'preGameHook'):
            self.commander.preGameHook(self)

        if self.drawBots:
            for name, bot in self.commander.game.bots.items():
                if bot.position is None:
                    continue

                if 'Red' in name:
                    if bot.seenlast > 0.0:
                        color = QtGui.qRgb(140,0,0)
                    else:
                        color = QtGui.qRgb(255,32,32)
                    if bot.health <= 0.0:
                        color = QtGui.qRgb(48,0,0)
                else:
                    if bot.seenlast > 0.0:
                        color = QtGui.qRgb(0,32,140)
                    else:
                        color = QtGui.qRgb(0,64,255)
                    if bot.health <= 0.0:
                        color = QtGui.qRgb(0,0,48)

                self.drawCircle(bot.position, color)
                self.drawRay(bot.position, bot.facingDirection, color)

        if hasattr(self.commander, 'postGameHook'):
            self.commander.postGameHook(self)


    def drawLine(self, (x1, y1), (x2, y2), color):
        self.paint.setBrush(QtGui.QColor(color))
        self.paint.setPen(QtGui.QPen(QtGui.QColor(color), 0.075, QtCore.Qt.SolidLine))
        self.paint.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x2, y2))


    def drawRay(self, (x, y), (u, v), color, scale = 1.5):
        self.drawLine((x, y), (x+u*scale, y+v*scale), color)


    def drawText(self, pos, color, text):
        self.paint.setPen(QtGui.QPen(QtGui.QColor(color), 0.075, QtCore.Qt.SolidLine))
        self.paint.setBrush(QtGui.QColor(color))
        f = QtGui.QFont("Consolas", 10)
        f.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.paint.setFont(f)
        self.paint.save()
        self.paint.scale(0.1, 0.1)
        self.paint.drawText(pos.x * 10.0, pos.y * 10.0, text)
        self.paint.restore()


    def drawCircle(self, (x, y), color, scale = 1.0):
        self.paint.setPen(QtGui.QPen(QtGui.QColor(color).darker(), 0.075, QtCore.Qt.SolidLine))
        self.paint.setBrush(QtGui.QColor(color))
        rectangle = QtCore.QRectF(x-scale*0.5, y-scale*0.5, scale, scale)
        self.paint.drawEllipse(rectangle)


    def drawPixel(self, (x, y), color):
        self.paint.setPen(QtGui.QPen(QtGui.QColor(QtGui.qRgb(64,64,64)), 0.075, QtCore.Qt.SolidLine))
        self.paint.setBrush(QtGui.QColor(color))
        self.paint.drawRect(x, y, 1, 1)


class VisualizerApplication(QtGui.QApplication):

    def __init__(self):
        super(VisualizerApplication, self).__init__([])

