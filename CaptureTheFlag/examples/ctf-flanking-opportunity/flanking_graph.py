
import time
import random
import networkx as nx

from api import orders
from api.color import Color
from api.vector2 import Vector2
from api.commander import Commander

import itertools
import corridormap
import scipy.spatial

MAX_CURSOR_SELECTION_DISTANCE = 1.0
MAX_ALT_PATH_LENGTH_MOD = 5.0
NUMBER_ALT_PATHS = 10

PARAM_MAX_PATH_LENGTH = "Max. Path Length"
PARAM_MAX_INTERSECTION_SHORTEST = "Max. Intersection Shortest"
PARAM_MAX_INTERSECTION_OTHERS = "Max. Intersection Others"
PARAM_MAX_EQUAL_SHORTEST_START = "Max. Equal Shortest Start"
PARAM_MAX_EQUAL_SHORTEST_END = "Max. Equal Shortest End"

NODE_COLOR_RED = Color(198, 28, 28, 255)
NODE_COLOR_BLUE = Color(63, 69, 152, 255)
NODE_COLOR_GREEN = Color(10, 122, 18, 255)
NODE_COLOR_ORANGE = Color(229, 122, 41, 255)
NODE_COLOR_BLUE_BRIGHT = Color(63, 69, 152, 100)
NODE_COLOR_ORANGE_BRIGHT = Color(229, 122, 41, 100)


class FlankingGraphCommander(Commander):
    """This commander uses a corridor graph to navigate through the map.
    """

    def initialize(self):
        """Initialize the commander class.
        """

        self.lastClickTime = time.time()

        layer = self.visualizer.anonymousLayer(True)
        self.visualizer.addLabel("Initializing...", "centered-info-box", Color(222, 222, 222, 255), None)
        self.visualizer.endLayer()

        ## Parameter default values
        self.currMaxAltPathLengthMod = 2.0
        self.currMaxIntersectionShortest = 5.0
        self.currMaxIntersectionOthers = 10.0
        self.currMaxEqualShortestStart = 1
        self.currMaxEqualShortestEnd = 1

        ## Prepare the corridor map/graph and pathfinding.
        self._initCorridorMap()
        self._initPathfinding()

        ## Define the values that should be modifiable by the user (via the sidebar UI).
        if len(self.alternativePaths) > 1:
            self.visualizer.addParameter(PARAM_MAX_PATH_LENGTH, 1.0, MAX_ALT_PATH_LENGTH_MOD, 2.0, 1.0)
            self.visualizer.addParameter(PARAM_MAX_INTERSECTION_SHORTEST, 2.0, 10.0, self.currMaxIntersectionShortest, 1.0)
            self.visualizer.addParameter(PARAM_MAX_INTERSECTION_OTHERS, 2.0, 15.0, self.currMaxIntersectionOthers, 1.0)
            self.visualizer.addParameter(PARAM_MAX_EQUAL_SHORTEST_START, 1.0, 5.0, self.currMaxEqualShortestStart, 1.0)
            self.visualizer.addParameter(PARAM_MAX_EQUAL_SHORTEST_END, 1.0, 5.0, self.currMaxEqualShortestEnd, 1.0)
            self.visualizer.addParameterButton("Choose Different Path")
            self.visualizer.setParameters()

        self.visualizer.hideLayer(layer)


    def _initCorridorMap(self):
        self.graph = corridormap.build_graph(self.level.blockHeights, self.level.width, self.level.height)
        self.kdtree = scipy.spatial.cKDTree([self.graph.node[n]["position"] for n in self.graph.nodes()])

        self.lookup = [[None for y in range(self.level.height)] for x in range(self.level.width)]
        node_count = len(self.graph.nodes())
        for x, y in itertools.product(range(self.level.width), range(self.level.height)):
            closest = None
            for d, i in zip(*self.kdtree.query((x, y), 2, distance_upper_bound=8.0)):
                if i >= node_count:
                    continue
                if closest is None or d < closest:
                    self.lookup[x][y] = i
                    closest = d


    def _initPathfinding(self):
        """Initialize the pathfinding and related objects used during runtime.
        """

        ## Calculate the shortest path from our base to the enemy flag.
        base = (self.game.team.botSpawnArea[0] + self.game.team.botSpawnArea[1]) * 0.5
        self.baseNode = self.lookup[int(base.x)][int(base.y)]
        flag = self.game.enemyTeam.flag.position
        self.flagNode = self.lookup[int(flag.x)][int(flag.y)]

        ## Calculate distance between each neighbour nodes.
        for s, f in self.graph.edges():
            sv = Vector2(*self.graph.node[s]["position"])
            fv = Vector2(*self.graph.node[f]["position"])
            self.graph[s][f]["length"] = sv.distance(fv)

        ## Calculate the shortest path in the graph.
        self.shortestPath = nx.shortest_path(self.graph, self.baseNode, self.flagNode, weight="length")

        ## Calculate list of alternative paths.
        self.generateAlternativePaths(MAX_ALT_PATH_LENGTH_MOD)
        self.alternativePaths = self.selectAlternativePaths()
        if len(self.alternativePaths) > 0:
            self.flankPath = self.alternativePaths[0]
            self.currentAltPathIndex = 0
        else:
            self.flankPath = None
            self.currentAltPathIndex = -1

        ## And finally draw the graph.
        self.initGraphVisualization()


    def generateAlternativePaths(self, maxPathLengthMod):
        maxPathLength = int(len(self.shortestPath) * maxPathLengthMod)
        self.allAltPaths = list(nx.all_simple_paths(self.graph, self.baseNode, self.flagNode, cutoff=maxPathLength))
        random.shuffle(self.allAltPaths)


    def selectAlternativePaths(self):
        result = []
        maxPathLength = int(len(self.shortestPath) * self.currMaxAltPathLengthMod)

        for ap in self.allAltPaths:
            if len(ap) > maxPathLength:
                continue  # Path longer then allowed per UI parameter

            ## Check intersection with shortet path
            intersection = set(ap).intersection(set(self.shortestPath))
            if len(intersection) > self.currMaxIntersectionShortest:
                continue

            ## Check equal nodes: start of shortest path
            if ap[:self.currMaxEqualShortestStart + 1] == self.shortestPath[:self.currMaxEqualShortestStart + 1]:
                continue

            ## Check equal nodes: end of shortest path
            if ap[len(ap) - self.currMaxEqualShortestStart - 1:] == self.shortestPath[len(ap) - self.currMaxEqualShortestStart - 1:]:
                continue

            good = True
            for n, rp in enumerate(result):
                ## Check intersection with selected alternative paths
                intersection = set(ap).intersection(set(rp))
                if len(intersection) > self.currMaxIntersectionOthers:
                    good = False  # Too many intersection nodes in both the alternative and the result path
                    break
            if not good:
                continue

            result.append(ap)

        lenResult = len(result)
        print ">> Number of alternative Paths:", lenResult if lenResult < NUMBER_ALT_PATHS else NUMBER_ALT_PATHS
        return result if len(result) <= NUMBER_ALT_PATHS else random.sample(result, NUMBER_ALT_PATHS)


    def getClosest(self, botPosition, pathPositions):
        """Determine the node closest to the given bot position.
        """

        positions = [(i, p) for (i, p) in enumerate(pathPositions)]
        return min(positions, key=lambda e: e[1].squaredDistance(botPosition))[0]


    def tick(self):
        """Called at every frame to update the world.
        """

        flankPath = self.flankPath if self.flankPath else self.shortestPath
        flankPathPositions = [Vector2(*self.graph.node[node_index]["position"]) for node_index in flankPath]

        for bot in self.game.bots_available:
            closestNodeIndex = self.getClosest(bot.position, flankPathPositions)
            self.issue(orders.Charge, bot, flankPathPositions[closestNodeIndex:])

        ## Handle mouse events.
        allMouseEvents = self.visualizer.getMouseEvents(False)  # non-blocking mode
        leftClickEvents = [event for event in allMouseEvents if event.leftClick]
        rightClickEvents = [event for event in allMouseEvents if event.rightClick]
        self.handleMouseClicks(leftClickEvents, rightClickEvents)

        ## Handle parameter change events: max. path length
        eventMap, newPathBtn = self.splitParameterEvents(self.visualizer.getParamChangeEvents())
        if PARAM_MAX_PATH_LENGTH in eventMap:
            self.currMaxAltPathLengthMod = eventMap[PARAM_MAX_PATH_LENGTH][-1]

        ## Handle parameter change events: max. intersection (shortest)
        if PARAM_MAX_INTERSECTION_SHORTEST in eventMap:
            self.currMaxIntersectionShortest = int(eventMap[PARAM_MAX_INTERSECTION_SHORTEST][-1])

        ## Handle parameter change events: max. intersection (others)
        if PARAM_MAX_INTERSECTION_OTHERS in eventMap:
            self.currMaxIntersectionOthers = int(eventMap[PARAM_MAX_INTERSECTION_OTHERS][-1])

        ## Handle parameter change events: max. equal shortest (start)
        if PARAM_MAX_EQUAL_SHORTEST_START in eventMap:
            self.currMaxEqualShortestStart = int(eventMap[PARAM_MAX_EQUAL_SHORTEST_START][-1])

        ## Handle parameter change events: max. equal shortest (end)
        if PARAM_MAX_EQUAL_SHORTEST_END in eventMap:
            self.currMaxEqualShortestEnd = int(eventMap[PARAM_MAX_EQUAL_SHORTEST_END][-1])

        if len(eventMap) > 0:
            self.alternativePaths = self.selectAlternativePaths()
            if len(self.alternativePaths) > 0:
                self.flankPath = self.alternativePaths[0]
                self.currentAltPathIndex = 0
            else:
                self.flankPath = None
                self.currentAltPathIndex = -1

        ## Handle parameter change events: path selection (button press)
        if newPathBtn and len(self.alternativePaths) > 1:
            self.currentAltPathIndex = 0 if self.currentAltPathIndex == len(self.alternativePaths) else self.currentAltPathIndex + 1
            self.flankPath = self.alternativePaths[self.currentAltPathIndex]

        self.clearGraphColors()
        self.setPathColors()


    def splitParameterEvents(self, events):
        eventMap = {}
        buttonPressed = False
        for event in events:
            if event.buttonPressed:
                buttonPressed = True
            if event.name in eventMap:
                eventMap[event.name].append(event.value)
            else:
                eventMap[event.name] = [event.value]
        return eventMap, buttonPressed


    def handleMouseClicks(self, leftClickEvents, rightClickEvents):
        if time.time() - self.lastClickTime < 0.25:
            return

        self.lastClickTime = time.time()
        if len(leftClickEvents) > 0:
            pass

        if len(rightClickEvents) > 0:
            pass


    ## Determine which node the user is pointing at with the cursor
    def getClosestGraphNodeFromEvent(self, event):
        bestNode, minDist = None, float("inf")
        floorPos = Vector2(event.x, event.y)
        for n in self.graph.nodes():
            dist = Vector2(*self.graph.node[n]["position"]).distance(floorPos)
            if dist < minDist:
                minDist = dist
                bestNode = n

        return bestNode, minDist


    def clearGraphColors(self):
        for s, f in self.graph.edges():
            self.visualizer.setColor(self.graph[s][f]["shape"], Color(255, 255, 255, 204))

        for n in self.graph.nodes():
            self.visualizer.setColor(self.graph.node[n]["shape"], Color(255, 255, 255, 153))


    def setPathColors(self):
        ## Set color for nodes and edges of shortest path
        for u, v in zip(self.shortestPath, self.shortestPath[1:]):
            lineId = self.graph[u][v]["shape"]
            uId = self.graph.node[u]["shape"]
            vId = self.graph.node[v]["shape"]
            self.visualizer.setColor(lineId, NODE_COLOR_ORANGE_BRIGHT)
            self.visualizer.setColor(uId, NODE_COLOR_ORANGE)
            self.visualizer.setColor(vId, NODE_COLOR_ORANGE)

        ## Set color for nodes and edges of flanking path
        if self.flankPath is not None:
            for u, v in zip(self.flankPath, self.flankPath[1:]):
                lineId = self.graph[u][v]["shape"]
                uId = self.graph.node[u]["shape"]
                vId = self.graph.node[v]["shape"]
                self.visualizer.setColor(lineId, NODE_COLOR_BLUE_BRIGHT)
                self.visualizer.setColor(uId, NODE_COLOR_BLUE)
                self.visualizer.setColor(vId, NODE_COLOR_BLUE)


    def initGraphVisualization(self):
        nodeRadius = 0.5
        thickness = 0.15

        self.lid = self.visualizer.beginLayer("Graph", "Corridor Map", False)

        ## Create graph edges (lines)
        for s, f in self.graph.edges():
            sv = Vector2(*self.graph.node[s]["position"])
            fv = Vector2(*self.graph.node[f]["position"])
            l = (fv - sv).length()
            d = (fv - sv).normalized()
            b = sv + d * (l - nodeRadius)
            e = fv - d * (l - nodeRadius)
            self.graph[s][f]["shape"] = self.visualizer.addLine(b, e, 0.1, Color(255, 255, 255, 204))

        ## Create graph nodes (circles)
        for n in self.graph.nodes():
            self.graph.node[n]["shape"] = self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius, True, thickness, Color(255, 255, 255, 153))
            self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius + thickness, False, thickness, Color(178, 178, 178, 153))

        self.visualizer.endLayer()
        self.setPathColors()

