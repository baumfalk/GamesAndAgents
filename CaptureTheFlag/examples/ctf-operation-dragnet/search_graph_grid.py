import time
import math
import random
import colorsys
import networkx as nx
import functools
from sets import Set

from api import orders
from api.vector2 import Vector2
from api.color import Color
from api.commander import Commander

from tools import visibility

import itertools
import scipy.spatial
import corridormap

NORMALIZED_DISTANCE = "Bias Towards Closer Nodes"
SEEN_RATIO = "Bias Towards Most Seen Nodes"


class ExploreTask(object):

    def __init__(self, commander, bot, path):
        self.commander = commander
        self.bot = bot
        self.path = path
        self.waypointIndex = 0
        self.waypoints = [Vector2(*self.commander.graph.node[nodeIndex]["position"]) for nodeIndex in path]
        self.creationTime = time.time()
        self.startMove = False


    def issueMoveOrder(self):
        if self.commander.seenRatio(self.path[self.waypointIndex]) < 0.5:
            self.commander.issue(orders.Attack, self.bot, self.waypoints[self.waypointIndex])
        else:
            self.commander.issue(orders.Charge, self.bot, self.waypoints[self.waypointIndex])


    def tick(self):
        actualTime = time.time()
        #Wait 2 seconds before start to execute the new plan.
        if (self.creationTime + 2.0) < actualTime:
            if not self.startMove:
                self.issueMoveOrder()
                self.startMove = True

            if self.bot.position.distance(self.waypoints[self.waypointIndex]) < 2.0:
                self.waypointIndex += 1
                if self.waypointIndex == len(self.waypoints):
                    return True

                if all((self.commander.visibleRatio(node) > 0.8 for node in self.path[self.waypointIndex:])):
                    return True
                self.issueMoveOrder()

            return False

        return False


class SeekCommander(Commander):

    def initialize(self):
        layer = self.visualizer.anonymousLayer(True)
        self.visualizer.addLabel("Initializing...", "centered-info-box", Color(222, 222, 222, 255), None)
        self.visualizer.endLayer()

        self.graph = corridormap.build_graph(self.level.blockHeights, self.level.width, self.level.height)
        self.kdtree = scipy.spatial.cKDTree([self.graph.node[n]["position"] for n in self.graph.nodes()])
        self.botPath = {}
        self.botPathColors = {}
        self.mouseLeftClicked = False
        self.debug = 0
        for n in self.graph.nodes():
            self.graph.node[n]["explored"] = False
            self.graph.node[n]["cell_count"] = 0
            self.graph.node[n]["visible_count"] = 0
            self.graph.node[n]["seen_count"] = 0

        self.lookup = [ [None for y in range(self.level.height)] for x in range(self.level.width)]
        node_count = len(self.graph.nodes())
        for x, y in itertools.product(range(self.level.width), range(self.level.height)):
            closest = None
            for d, i in zip(*self.kdtree.query((x, y), 2, distance_upper_bound=8.0)):
                if i >= node_count:
                    continue
                if closest is None or d < closest:
                    self.lookup[x][y] = i

                    if self.level.blockHeights[x][y] == 0:
                        self.graph.node[i]["cell_count"] += 1

                    closest = d

        self.seen = [ [-1 for y in range(self.level.height)] for x in range(self.level.width)]
        self.seen_dirty = []
        self.visibility = [ [False for y in range(self.level.height)] for x in range(self.level.width)]
        self.visibility_previous = None

        self.initVisualization()

        self.exploreTasks = { bot : None for bot in self.game.team.members }
        #set the colors for the graph path
        for bot in self.game.team.members:
            if bot.name == "Blue0":
                self.botPathColors[bot] = Color(200, 100, 50)
            if bot.name == "Blue3":
                self.botPathColors[bot] = Color(80, 10, 180)
            if bot.name == "Blue2":
                self.botPathColors[bot] = Color(0, 0, 255)
            if bot.name == "Blue1":
                self.botPathColors[bot] = Color(0, 0, 0)

        self.visualizer.hideLayer(layer)


    def explore(self, bot, goalNode):
        start = self.lookup[int(bot.position.x)][int(bot.position.y)]
        path = nx.shortest_path(self.graph, start, goalNode, weight="weight")
        nodesIndex = []
        for nodeIndex in path:
            self.graph.node[nodeIndex]["explored"] = True
            nodesIndex.append(nodeIndex)

        self.botPath[bot] = nodesIndex
        self.exploreTasks[bot] = ExploreTask(self, bot, path)


    def nodesInProximity(self, position, radius):
        return self.kdtree.query_ball_point((position.x, position.y), radius)

    def rasterizeVisibility(self, bot):
        if 'Blue' in bot.name:
            index = int(bot.name.replace('Blue', ''))
        else:
            index = int(bot.name.replace('Red', ''))

        for n in self.graph.nodes():
            self.graph.node[n]["visible_count"] = 0

        fov = math.pi * 0.5
        fov = fov * 0.9
        coshalffov = math.cos(fov * 0.5)

        def setVisible(x, y):
            d = (Vector2(x, y) - bot.position).normalized()
            dp = d.dotProduct(bot.facingDirection)

            if dp > coshalffov:
                node_index = self.lookup[x][y]

                if not self.visibility[x][y]:
                    self.graph.node[node_index]["visible_count"] += 1
                    self.visibility[x][y] = True

                if self.seen[x][y] != index:
                    self.seen_dirty.append((x,y))

                    if self.seen[x][y] < 0:
                        self.graph.node[node_index]["seen_count"] += 1

                    self.seen[x][y] = index

        wave = visibility.Wave((0, 0, self.level.width, self.level.height), isBlocked=lambda x, y: self.level.blockHeights[x][y] > 1, setVisible=setVisible)
        wave.compute(bot.position)

        for n in self.graph.nodes():
            if self.graph.node[n]["seen_count"] == self.graph.node[n]["cell_count"]:
                self.graph.node[n]["explored"] = True


    def seenRatio(self, node_index):
        return float(self.graph.node[node_index]["seen_count"])/float(self.graph.node[node_index]["cell_count"])


    def visibleRatio(self, node_index):
        return float(self.graph.node[node_index]["visible_count"])/float(self.graph.node[node_index]["cell_count"])

    def tick(self):
        self.updateSliders()

        for bot in self.game.bots_alive:
            self.rasterizeVisibility(bot)

        for bot, task in self.exploreTasks.iteritems():
            if task is not None:
                if task.tick():
                    self.exploreTasks[bot] = None
        for bot in self.exploreTasks.keys():
            if self.exploreTasks[bot] is not None:
                continue
            origin = bot.position
            radii = [8.0, 16.0, 32.0, 64.0, 128.0, 256.0]

            origin_node = self.lookup[int(origin.x)][int(origin.y)]
            path_lengths = nx.single_source_dijkstra_path_length(self.graph, origin_node, cutoff=radii[-1])

            for radius in radii:
                node_indices = self.nodesInProximity(origin, radius)
                node_indices = [n for n in node_indices if not self.graph.node[n]["explored"]]
                node_indices = [n for n in node_indices if self.seenRatio(n) < 1.0]

                if len(node_indices) == 0:
                    continue

                normalized_distances = [Vector2(*self.graph.node[n]["position"]).distance(origin) / radius for n in node_indices]
                dead_end_path_lengths = []

                for i, node_index in enumerate(node_indices):
                    if len(self.graph.neighbors(node_index)) == 1:
                        path_length = path_lengths.get(node_index, radius)
                        dead_end_path_lengths.append(path_length / radius)
                    else:
                        dead_end_path_lengths.append(0)

                seenRatios = [self.seenRatio(n) for n in node_indices]

                heuristic = []

                for i, node_index in enumerate(node_indices):
                    score = self.score(normalized_distances[i], dead_end_path_lengths[i], seenRatios[i])
                    heuristic.append(score)

                sorted_indices = sorted(zip(heuristic, node_indices), key=lambda x: x[0])
                node_indices = [n for h, n in sorted_indices]
                self.explore(bot, node_indices[len(node_indices) - 1])
                break


        def on_grid(v):
            return int(v.x) >= 0 and int(v.x) < self.level.width and int(v.y) >= 0 and int(v.y) < self.level.height

        dirty_set = set(self.seen_dirty)
        for event in self.visualizer.getMouseEvents(False):
            o = None
            if event.leftClick:
                if self.mouseLeftClicked == False:
                    self.visualizer.setColor(self.selectedMouseShape, Color(100, 100, 100))
                    self.mouseLeftClicked = True

                o = Vector2(event.x, event.y)
                for x_n in range(-5, 6):
                    for y_n in range(-5, 6):
                        v = o + Vector2(x_n, y_n)
                        if on_grid(v) and (v - o).length() < 5.0:
                            self.unseeCell(int(v.x), int(v.y))
                            dirty_set.add((int(v.x), int(v.y)))

            if o != None:
                floorPos = Vector2(o.x, o.y)
                botDic = {}
                for botAlive in self.game.bots_alive:
                    botDic[bot.position.distance(floorPos)] = botAlive
                #take the bot nearer to where the user have clicked
                botToReset = botDic.itervalues().next()
                self.exploreTasks[botToReset] = None

            if not event.leftClick and self.mouseLeftClicked:
                self.mouseLeftClicked = False
                self.visualizer.setColor(self.selectedMouseShape, self.initCircleColor)

        self.seen_dirty = list(dirty_set)

        self.updateVisibilityGrid()
        self.updateSeenGrid()
        self.updateGraphColors()
        self.updateBotPaths()


    def unseeCell(self, x, y):
        if self.seen[x][y] >= 0:
            node_index = self.lookup[x][y]
            self.graph.node[node_index]["seen_count"] -= 1
            self.graph.node[node_index]["explored"] = False
            self.seen[x][y] = -1


    def updateVisibilityGrid(self):
        pixelBatch = []

        for x in range(self.level.width):
            for y in range(self.level.height):
                visible = self.visibility[x][y]
                if self.visibility_previous is not None and visible == self.visibility_previous[x][y]:
                    continue

                if visible:
                    pixelBatch.append((x, y, Color(251, 151, 7, 255)))
                else:
                    pixelBatch.append((x, y, Color(102, 102, 102, 255)))

        if len(pixelBatch) > 0:
            self.visualizer.putPixelBatch(self.visibilityBitmapShape, pixelBatch)
        self.visibility_previous = self.visibility
        self.visibility = [ [False for y in range(self.level.height)] for x in range(self.level.width)]


    # Calculated based on random seed that's hashed based on the Bot name.
    SEEN_COLORS = [Color(*[v * 255 for v in colorsys.hsv_to_rgb(*hsv)]) for hsv in [
        (0.6969696283340454, 1.0000000000000000, 0.22935447831162442),
        (0.6969696283340454, 0.3623396234703635, 0.6123498342124517),
        (0.6969696283340454, 0.4539608149152492, 0.22546792316027325),
        (0.6969696283340454, 0.7610825087879753, 0.7127172091292207),
    ]]


    def updateSeenGrid(self):
        pixelBatch = []

        for x, y in self.seen_dirty:
            index = self.seen[x][y]
            if index >= 0:
                pixelBatch.append((x, y, self.SEEN_COLORS[(index - 1) % len(self.SEEN_COLORS)]))
            else:
                pixelBatch.append((x, y, Color(255, 255, 255, 0)))

        self.seen_dirty = []
        if len(pixelBatch) > 0:
            self.visualizer.putPixelBatch(self.seenBitmapShape, pixelBatch)


    def updateGraphColors(self):
        for n in self.graph.nodes():
            intensity = self.seenRatio(n)

            if self.graph.node[n]["explored"]:
                self.visualizer.setColor(self.graph.node[n]["border_shape"], Color(255, 0, 0, 255))
            else:
                self.visualizer.setColor(self.graph.node[n]["border_shape"], Color(127, 127, 127, 255))
            self.visualizer.setColor(self.graph.node[n]["shape"], Color(intensity * 255, intensity * 255, intensity * 255, 255))


    def updateBotPaths(self):
        botNodesOwned = []
        for key in self.botPath:
            color = self.botPathColors.get(key, Color(200, 100, 50))
            for node in self.botPath[key]:
                if node not in botNodesOwned:
                    self.visualizer.setColor(self.graph.node[node]["border_interactive"], color)
                    botNodesOwned.append(node)
        setNodesBot = set(botNodesOwned)
        for n in self.graph.nodes():
            intensity = self.seenRatio(n)
            if n not in setNodesBot:
                self.visualizer.setColor(self.graph.node[n]["border_interactive"], Color(127, 127, 127, 255))
            self.visualizer.setColor(self.graph.node[n]["shape_interactive"], Color(intensity * 255, intensity * 255, intensity * 255, 255))


    def updateSliders(self):
        changedValue = False
        eventMap = self.splitParameterEvents(self.visualizer.getParamChangeEvents())
        if SEEN_RATIO in eventMap:
            self.sawCellsWeight = float(eventMap[SEEN_RATIO][-1])
            changedValue = True
        if NORMALIZED_DISTANCE in eventMap:
            self.distanceWeight = float(eventMap[NORMALIZED_DISTANCE][-1])
            changedValue = True
        if changedValue:
            for bot in self.exploreTasks.keys():
                self.exploreTasks[bot] = None
                self.issue(orders.Move, bot, bot.position)


    def splitParameterEvents(self, events):
        eventMap = {}
        for event in events:
            if event.name in eventMap:
                eventMap[event.name].append(event.value)
            else:
                eventMap[event.name] = [event.value]
        return eventMap


    def score(self, normalized_distance, dead_end_path_length, seenRatio):
        currDistanceWeight = (32 * self.distanceWeight) * normalized_distance
        currSeenWeight = (128 * self.sawCellsWeight) * seenRatio
        currDeadEndWeight = 64 * dead_end_path_length
        return currDistanceWeight - currDeadEndWeight + currSeenWeight


    def initVisualization(self):
        self.initGridVisualization()
        self.initGraphVisualization()
        self.initSlidersVisualization()


    def initSlidersVisualization(self):
        self.distanceWeight = 1.0
        self.sawCellsWeight = 1.0

        self.visualizer.addParameter(NORMALIZED_DISTANCE, 0.0, 1.0, self.distanceWeight, 0.2)
        self.visualizer.addParameter(SEEN_RATIO, 0.0, 1.0, self.sawCellsWeight, 0.2)
        self.visualizer.setParameters()


    def initGridVisualization(self):
        self.seenGridLayer = self.visualizer.beginLayer("Seen Layer", "", visible=False)
        self.seenBitmapShape = self.visualizer.addBitmap(
            lowerCorner=Vector2(0, 0),
            upperCorner=Vector2(self.level.width, self.level.height),
            width=self.level.width,
            height=self.level.height)

        self.visualizer.fillBitmap(self.seenBitmapShape, Color(255, 255, 255, 0))
        self.initCircleColor = Color(100, 100, 100, 50)
        self.selectedMouseShape = self.visualizer.addCircle(Vector2(-10.0, -10.0), 4.5, False, 0.2, self.initCircleColor)
        self.visualizer.attachMouseShape(self.selectedMouseShape)
        self.visualizer.endLayer()


        self.visibilityGridLayer = self.visualizer.beginLayer("Visibility Layer", "", visible=False)
        self.visibilityBitmapShape = self.visualizer.addBitmap(
            lowerCorner=Vector2(0, 0),
            upperCorner=Vector2(self.level.width, self.level.height),
            width=self.level.width,
            height=self.level.height
        )

        self.visualizer.fillBitmap(self.visibilityBitmapShape, Color(102, 102, 102, 255))
        self.visualizer.endLayer()


    def initGraphVisualization(self):
        nodeRadius = 0.5
        thickness = 0.15

        self.graphLayer = self.visualizer.beginLayer("Graph: Bot Paths", "", visible=False)

        for s, f in self.graph.edges():
            sv = Vector2(*self.graph.node[s]["position"])
            fv = Vector2(*self.graph.node[f]["position"])
            l = (fv - sv).length()
            d = (fv - sv).normalized()
            b = sv + d * (l - nodeRadius)
            e = fv - d * (l - nodeRadius)
            self.graph[s][f]["shape_interactive"] = self.visualizer.addLine(b, e, 0.1, Color(255, 255, 255, 255))

        for n in self.graph.nodes():
            self.graph.node[n]["shape_interactive"] = self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius, True, thickness, Color(0, 0, 0, 255))
            self.graph.node[n]["border_interactive"] = self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius + thickness, False, thickness, Color(127, 127, 127, 255))

        self.visualizer.endLayer()

        self.graphLayer = self.visualizer.beginLayer("Graph Nodes Visibility", "", visible=False)

        for s, f in self.graph.edges():
            sv = Vector2(*self.graph.node[s]["position"])
            fv = Vector2(*self.graph.node[f]["position"])
            l = (fv - sv).length()
            d = (fv - sv).normalized()
            b = sv + d * (l - nodeRadius)
            e = fv - d * (l - nodeRadius)
            self.graph[s][f]["shape"] = self.visualizer.addLine(b, e, 0.1, Color(255, 255, 255, 204))

        for n in self.graph.nodes():
            self.graph.node[n]["shape"] = self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius, True, thickness, Color(0, 0, 0, 255))
            self.graph.node[n]["border_shape"] = self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius + thickness, False, thickness, Color(127, 127, 127, 255))

        self.visualizer.endLayer()
