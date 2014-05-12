#==============================================================================
# This file is part of The AI Sandbox
# Copyright (c) 2013, AiGameDev.com KG.
#==============================================================================

"""Sample implementation of a flanking commander.

This CTF commander will guide its bots to the enemy flag, while trying to
avoid moving them at the shortest path. Instead it will calculate a flanking
position to that shortest path and try to reach the enemy flag from there.
"""

import random
import itertools


from collections import defaultdict

import networkx as nx

from api import orders
from api.vector2 import Vector2

from api.color import Color
from api.commander import Commander

from PySide import QtCore


class FlankingGridCommander(Commander):
    """This commander uses a grid-based graph to navigate through the map.
    """

    def initialize(self):
        """Initialize the commander class.
        """

        ## Some default values.
        self.verbose = False
        self.showShortestPath = 0
        self.showFlankPath = 0
        self.showDistance = 0

        self._initPathfinding(1)
        self._initVisualization()


    def _initPathfinding(self, resolution):
        """Initialize the pathfinding and related objects used during runtime.
        """

        ## Create the Pathfinder object based on the networkx module.
        self.pathfinder = PathFinder(self.level.blockHeights, resolution)
        graph = self.pathfinder.graph

        ## Calculate the shortest path from our base to the enemy flag.
        basePosition = (self.game.team.botSpawnArea[0] + self.game.team.botSpawnArea[1]) * 0.5
        flagPosition = self.game.enemyTeam.flag.position

        self.shortest_path = self.pathfinder.computeShortestPath(basePosition, flagPosition)

        ## Calculate the path lengths of all graph nodes to the shortest path nodes.
        self.distances = self.pathfinder.computeDistanceMap(self.shortest_path)

        ## Create weight heuristics based on path lengths.
        for index, distance in self.distances.iteritems():
            # IMPORTANT: Fix this equation to provide good heuristics for the
            # shortest path...
            graph.node[index]["weight"] = 5000.0 / distance ** 2

        for u, v in graph.edges():
            try:
                w = (graph.node[u]["weight"] + graph.node[v]["weight"]) * 0.5
                graph[u][v]["weight"] += w
            except KeyError:
                # If a node is disconnected from the rest of the map, an exception is thrown. As a fix,
                # check if the node is inside the distance map.
                pass

        ## And finally calculate the path to the flanking position.
        self.flanking_path = self.pathfinder.computeShortestPath(basePosition, flagPosition)


    def keyPressed(self, window, event):
        """Called by Qt whenever a key has been pressed.
        """

        window.dirty = True  # redraw the debug window in any case

        if event.key() == QtCore.Qt.Key_F1:
            self.showDistance = self.showDistance ^ 1

        if event.key() == QtCore.Qt.Key_F2:
            self.showShortestPath = self.showShortestPath ^ 1

        if event.key() == QtCore.Qt.Key_F3:
            self.showFlankPath = self.showFlankPath ^ 1

        if event.key() == QtCore.Qt.Key_F4:
            self.window.drawBots = self.window.drawBots ^ 1


    def _initVisualization(self):
        """Draw some visualization directly to the 3d world of the simulation.
        """
        self.visualizer.beginLayer("GridWeights", "", False)
        ## First we draw a grid of boxes/rectangles to the floor of the map.
        ## The shade of gray of these boxes represent the weights of the graph's nodes.
        maximum = max([self.pathfinder.graph.node[n]["weight"] for n in self.pathfinder.graph.nodes()])
        minimum = min([self.pathfinder.graph.node[n]["weight"] for n in self.pathfinder.graph.nodes()])
        for i, j in itertools.product(range(self.level.width), range(self.level.height)):
            index = self.pathfinder.getNodeIndex((i, j))
            if index is not None:  # None = obstacles
                intensity = ((self.pathfinder.graph.node[index]["weight"] - minimum) / (maximum - minimum)) ** 0.5
                sid = self.visualizer.addBox(Vector2(i, j) + 0.5, Vector2(0.5, 0.5), 0.05 + (1.0 - intensity) * 2.0, Color(intensity * 255, intensity * 255, intensity * 255, 217))
                self.pathfinder.graph.node[index]['sid'] = sid
        self.visualizer.endLayer()

        self.visualizer.beginLayer("ShortestPath", "", False)
        ## Draw the shortest path as calculated 0before as orange trail to the map.
        for u, v in zip(self.shortest_path, self.shortest_path[1:]):
            self.visualizer.addCircle(self.pathfinder.getNodePosition(u), 0.35, True, 1, Color(229, 122, 41, 255))
            self.visualizer.addCircle(self.pathfinder.getNodePosition(v), 0.35, True, 1, Color(229, 122, 41, 255))
        self.visualizer.endLayer()

        self.visualizer.beginLayer("SelectedFlankingPath", "", False)
        ## Draw the flanking path as calculated before as green trail to the map.
        for u, v in zip(self.flanking_path, self.flanking_path[1:]):
            self.visualizer.addCircle(self.pathfinder.getNodePosition(u), 0.35, True, 1, Color(10, 122, 17, 255))
            self.visualizer.addCircle(self.pathfinder.getNodePosition(v), 0.35, True, 1, Color(10, 122, 17, 255))
        self.visualizer.endLayer()
        

    def findClosest(self, botPosition, pathPositions):
        """Determine the node closest to the given bot position.
        """

        positions = [(i, p) for (i, p) in enumerate(pathPositions)]
        return min(positions, key=lambda e: e[1].squaredDistance(botPosition))[0]


    def tick(self):
        """Called at every frame to update the world.
        """

        flankPathPositions = [self.pathfinder.getNodePosition(cell) for cell in self.flanking_path]

        for bot in self.game.bots_available:

            closestNodeIndex = self.findClosest(bot.position, flankPathPositions)
            self.issue(orders.Charge, bot, flankPathPositions[closestNodeIndex:])


class PathFinder(object):
    """This class generates the graph for networkx based on the level's grid.
    """

    def __init__(self, blocks, resolution=1):
        self.blocks = blocks
        self.makeGraph(resolution)


    def makeGraph(self, resolution):
        """Generate the grid-based graph based on the level's topology (obstacles and free cells).
        """

        width, height = len(self.blocks), len(self.blocks[0])
        g = nx.Graph(directed=False, map_height=height / resolution,
                     map_width=width / resolution)

        cells = defaultdict(list)
        self.terrain = []
        for j in range(0, height):
            row = []
            for i in range(0, width):
                if self.blocks[i][j] == 0:
                    index = (i / resolution) + (j / resolution) * (width / resolution)
                    cells[index].append(Vector2(float(i) + 0.5, float(j) + 0.5))
                    row.append(index)
                else:
                    row.append(None)
            self.terrain.append(row)

        r = resolution - 1
        for index, positions in cells.iteritems():
            average = sum(positions, Vector2((random.random() - 0.5) * r, (random.random() - 0.5) * r)) / float(len(positions))
            g.add_node(index, position=average)

        for i, j in itertools.product(range(0, width), range(0, height)):
            p = self.terrain[j][i]
            if i < width - 1:
                q = self.terrain[j][i + 1]
                if q is not None and p is not None:
                    e = g.add_edge(p, q, weight=1.0 * resolution)
            else:
                q = None

            if j < height - 1:
                r = self.terrain[j + 1][i]
                if r is not None and p is not None:
                    e = g.add_edge(p, r, weight=1.0 * resolution)
            else:
                r = None

            ## Diagonal connections, only if both sides are not blocked.
            if i < width - 1 and j < height - 1:
                s = self.terrain[j + 1][i + 1]
                if s is not None and p is not None and (q is not None or r is not None):
                    e = g.add_edge(p, s, weight=1.414213562 * resolution)

            if r is not None and q is not None:
                if p is not None or s is not None:
                    e = g.add_edge(r, q, weight=1.414213562 * resolution)

        self.graph = g


    def getNodeIndex(self, position):
        """Return the graph node index based on the given position in the map.
        """

        if isinstance(position, tuple):
            i, j = position
        else:
            i, j = int(position.x), int(position.y)

        return self.terrain[j][i]


    def getNodePosition(self, index):
        return Vector2(*self.getNode(index)["position"])


    def computeDistanceMap(self, cells):
        """Using networkx generate the distance map between pairs of cells.
        """

        start = "start"
        self.graph.add_node(start)
        for index in cells:
            self.graph.add_edge(start, index, weight=1.0)
        distance_map = nx.single_source_dijkstra_path_length(self.graph, start, weight="weight")
        del distance_map["start"]
        self.graph.remove_node(start)
        return distance_map


    def computeShortestPath(self, source, target):
        """Calculate the shortest path between the two given nodes.
        """

        # IMPORTANT: You can only use astar_path() and this heuristic if your distances are only ever
        # longer than the real Euclidean distances.
        # def calculateDistance(n, t):
        #    return Vector2(*nodes[n]["position"]).distance(Vector2(*nodes[t]["position"]))

        s = self.getNodeIndex(source)
        t = self.getNodeIndex(target)
        return nx.shortest_path(self.graph, s, t, weight="weight")  # heuristic=calculateDistance


    def getNode(self, index):
        """Return the graph node based on the given indices.
        """

        if isinstance(index, tuple):
            (i, j) = index
            index = self.terrain[j][i]

        return self.graph.node[index]
