
import time
import random
import colorsys
import networkx as nx

from api import orders
from api.vector2 import Vector2
from api.commander import Commander
from api.color import Color

import itertools
import scipy.spatial
import corridormap

MAX_CURSOR_SELECTION_DISTANCE = 2


class TacticalSearchExploreCommander(Commander):

    def initialize(self):
        layer = self.visualizer.anonymousLayer(True)
        self.visualizer.addLabel("Initializing...", "centered-info-box", Color(222, 222, 222, 255), None)
        self.visualizer.endLayer()

        self.bestBotShapeId = -1
        self.selectedBot = None
        self.selectedBotShapeId = -1
        self.lastClickTime = time.time()
        self.botWaypoints = {}
        self.graph = corridormap.build_graph(self.level.blockHeights, self.level.width, self.level.height)
        self.kdtree = scipy.spatial.cKDTree([self.graph.node[node]["position"] for node in self.graph.nodes()])

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

        for node in self.graph.nodes():
            self.graph.node[node]["distances"] = nx.single_source_dijkstra_path_length(self.graph, node, weight="weight")
            self.graph.node[node]["explored"] = False
        self.initGraphVisualization()

        self.visualizer.hideLayer(layer)


    ## This method is called every time a bot needs to choose a new target node.
    ## Here you can choose from either getClosestUnexploredNode() or getFurthestUnexploredNode().
    def selectNextTargetNode(self, current):
        return self.getFurthestUnexploredNode(current)


    ## Select that unexplored node that is furthest from the current node.
    ## --> Use within method selectNextTargetNode().
    def getFurthestUnexploredNode(self, current):
        maxDist = 0
        maxNode = None
        for node in self.graph.nodes():
            if node == current: continue
            if self.graph.node[node]["explored"]: continue
            if self.graph.node[current]["distances"][node] > maxDist:
                maxDist = self.graph.node[current]["distances"][node]
                maxNode = node

        return maxNode


    ## Select that unexplored node that is closest to the current node.
    ## --> Use within method selectNextTargetNode().
    def getClosestUnexploredNode(self, current):
        minDist = float("inf")
        minNode = None
        for node in self.graph.nodes():
            if node == current: continue
            if self.graph.node[node]["explored"]: continue
            if self.graph.node[current]["distances"][node] < minDist:
                minDist = self.graph.node[current]["distances"][node]
                minNode = node

        return minNode


    ## Generate the path for the given bot to the desired target node.
    ## Here you can choose from either getFreePathToTarget() or getShortestPathToTarget().
    def getPathToTarget(self, bot, target):
        start = self.lookup[int(bot.position.x)][int(bot.position.y)]
        return self.getFreePathToTarget(bot, start, target)


    ## Get a path that is furthest from another path of a randomly chosen bot.
    ## --> Use within method getPathToTarget().
    def getFreePathToTarget(self, bot, current, target):
        ## tmp: get one of the current active paths
        if len(self.botWaypoints) == 0 or (len(self.botWaypoints) == 1 and bot in self.botWaypoints):
            return nx.shortest_path(self.graph, current, target, weight="weight")
        rndKey = random.choice([key for key in self.botWaypoints.keys() if key != bot])
        otherPath = self.botWaypoints[rndKey][0]

        ## Create a dummy graph node and connect it to each nodes of the shortest path.
        u = "startNode"
        self.graph.add_node(u)
        for v in otherPath:
            self.graph.add_edge(u, v, weight=1)

        ## Now calculate the path lengths of all graph nodes to the shortest path nodes.
        distances = nx.single_source_dijkstra_path_length(self.graph, u, weight="weight")
        self.graph.remove_node(u)  # we don't need the dummy graph node any more
        del distances[u]

        ## Create weight heuristics based on path lengths.
        for node_index, length in distances.iteritems():
            self.graph.node[node_index]["weight"] = length
        for u, v in self.graph.edges():
            w = (self.graph.node[u]["weight"] + self.graph.node[v]["weight"]) * 0.5
            self.graph[u][v]["weight"] = 1 / w ** 2

        ## And finally calculate the path to the flanking position.
        return nx.shortest_path(self.graph, current, target, weight="weight")


    ## Get simply the shortest path to the given target node.
    ## --> Use within method getPathToTarget().
    def getShortestPathToTarget(self, bot, current, target):
        return nx.shortest_path(self.graph, current, target, weight="weight")


    def getBotColor(self, bot):
        botColors = [Color(*[v * 255 for v in colorsys.hsv_to_rgb(*hsv)]) for hsv in [
            (0.6969696283340454, 1.0000000000000000, 0.22935447831162442),
            (0.6969696283340454, 0.3623396234703635, 0.6123498342124517),
            (0.6969696283340454, 0.4539608149152492, 0.22546792316027325),
            (0.6969696283340454, 0.7610825087879753, 0.7127172091292207),
        ]]

        if bot.name.startswith('Blue'):
            index = int(bot.name.replace('Blue', ''))
        else:
            index = int(bot.name.replace('Red', ''))

        return botColors[index % len(botColors)]


    def explore(self, bot, goalNode):
        path = self.getPathToTarget(bot, goalNode)

        if bot in self.botWaypoints:
            self.botWaypoints[bot] = (path, self.botWaypoints[bot][1])
        else:
            self.botWaypoints[bot] = (path, self.getBotColor(bot))

        for nodeIndex in path:
            self.graph.node[nodeIndex]["explored"] = True

        waypoints = [Vector2(*self.graph.node[nodeIndex]["position"]) for nodeIndex in path]
        self.issue(orders.Charge, bot, waypoints)


    ## determine which bot the user is pointing at with the cursor
    def getClosestBotFromEvents(self, events):
        floorPos = Vector2(events[-1].x, events[-1].y)
        return min([(bot, bot.position.distance(floorPos)) for bot in self.game.bots_alive], key=lambda p: p[1])


    def handleMouseClicks(self, clickEvents):
        if time.time() - self.lastClickTime < 0.25:
            self.lastClickTime = time.time()
            return

        self.lastClickTime = time.time()
        bestBot, dist = self.getClosestBotFromEvents(clickEvents)
        if dist > MAX_CURSOR_SELECTION_DISTANCE:
            return

        if bestBot == self.selectedBot:
            ## Clicked on the selected bot again -> deselect.
            self.visualizer.removeShape(self.selectedBotShapeId)
            self.selectedBotShapeId = None
            self.selectedBot = None
        else:
            ## Another bot selected.
            if self.selectedBot is not None:
                self.visualizer.removeShape(self.selectedBotShapeId)
            self.visualizer.addToLayer(self.lid)
            color = Color(227, 223, 28)  # bright yellow
            self.selectedBotShapeId = self.visualizer.addCircle(bestBot.position, 1.5, False, 0.5, color)
            self.visualizer.attachShape(self.selectedBotShapeId, bestBot.name)
            self.selectedBot = bestBot
            self.visualizer.endLayer()

    def tick(self):
        for bot in self.game.bots_available:
            target = self.selectNextTargetNode(self.lookup[int(bot.position.x)][int(bot.position.y)])
            if target is None:
                return
            self.explore(bot, target)

        ## Get mouse click events
        allMouseEvents = self.visualizer.getMouseEvents(False)  # non-blocking mode
        clickEvents = [event for event in allMouseEvents if event.leftClick]
        if len(clickEvents) > 0:
            self.handleMouseClicks(clickEvents)

        ## Get mouse move events
        # moveEvents = [event for event in allMouseEvents if not event.leftClick and not event.rightClick]
        # if len(moveEvents) > 0:
        #     ## determine which bot the user is pointing at with the cursor
        #     bestBot, dist = self.getClosestBotFromEvents(moveEvents)
        #     if dist < MAX_CURSOR_SELECTION_DISTANCE:
        #         self.bestBot = bestBot
        # else:
        #     self.bestBot = None

        self.drawBotPaths()


    def drawBotPaths(self):
        def updColors(b, highlightColor=None):
            (path, color) = self.botWaypoints[b]
            if highlightColor is not None:
                color = highlightColor
            for u, v in zip(path, path[1:]):
                #if the node is not already colored
                if u not in colored:
                    self.visualizer.setColor(self.graph.node[u]["shape"], color)
                    colored.append(u)
            self.visualizer.setColor(self.graph.node[path[-1]]["shape"], color)
            colored.append(path[-1])

        ## Draw paths
        colored = []
        #order of operations is important as we dont color nodes
        #that were already colored
        if self.selectedBot is not None:
            updColors(self.selectedBot, Color(227, 223, 28))  # bright yellow
        for bot in self.botWaypoints.keys():
            if bot not in self.game.bots_available and bot is not self.selectedBot:#self.bestBot:
                updColors(bot)
        #if self.bestBot is not None and self.bestBot is not self.selectedBot:
        #    updColors(self.bestBot, Color(238, 149, 43))  # orange

        for n in self.graph.nodes():
            if n not in colored and self.graph.node[n]["explored"]:
                self.visualizer.setColor(self.graph.node[n]["shape"], Color(0, 0, 0, 200))


    def initGraphVisualization(self):
        nodeRadius = 0.5
        thickness = 0.15

        self.lid = self.visualizer.beginLayer("Graph", "", False)
        for s, f in self.graph.edges():
            sv = Vector2(*self.graph.node[s]["position"])
            fv = Vector2(*self.graph.node[f]["position"])
            l = (fv - sv).length()
            d = (fv - sv).normalized()
            b = sv + d * (l - nodeRadius)
            e = fv - d * (l - nodeRadius)
            self.graph[s][f]["shape"] = self.visualizer.addLine(b, e, 0.1, Color(0, 0, 0, 100))

        for n in self.graph.nodes():
            self.graph.node[n]["shape"] = self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius, True, thickness, Color(0, 0, 0, 100))

        self.visualizer.endLayer()
