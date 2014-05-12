import random
import networkx as nx

from api import orders
from api.vector2 import Vector2
from api.commander import Commander
from api.color import Color

from tools import visualizer
from PySide import QtGui, QtCore

import itertools
import scipy.spatial
import corridormap


class GraphRandomExploreCommander(Commander):

    def initialize(self):

        self.graph = corridormap.build_graph(self.level.blockHeights, self.level.width, self.level.height)
        self.kdtree = scipy.spatial.cKDTree([self.graph.node[n]["position"] for n in self.graph.nodes()])

        self.lookup = [ [None for y in range(self.level.height)] for x in range(self.level.width)]
        node_count = len(self.graph.nodes())
        for x, y in itertools.product(range(self.level.width), range(self.level.height)):
            closest = None
            for d, i in zip(*self.kdtree.query((x, y), 2, distance_upper_bound=8.0)):
                if i >= node_count:
                    continue
                if closest is None or d < closest:
                    self.lookup[x][y] = i
                    closest = d

        for n in self.graph.nodes():
            self.graph.node[n]["explored"] = False
        self.initGraphVisualization()

    def getRandomUnexploredNodes(self, count):
        unexplored = [n for n in self.graph.nodes() if not self.graph.node[n]["explored"]]
        return random.sample(unexplored, count)


    def explore(self, bot, goalNode):
        start = self.lookup[int(bot.position.x)][int(bot.position.y)]
        path = nx.shortest_path(self.graph, start, goalNode, weight="weight")

        for nodeIndex in path:
            self.graph.node[nodeIndex]["explored"] = True

        waypoints = [Vector2(*self.graph.node[nodeIndex]["position"]) for nodeIndex in path]
        self.issue(orders.Charge, bot, waypoints)


    def tick(self):
        goals = self.getRandomUnexploredNodes(len(self.game.bots_available))

        for goal, bot in zip(goals, self.game.bots_available):
            self.explore(bot, goal)

        ##Draw explored
        for n in self.graph.nodes():
            if self.graph.node[n]["explored"]:
                self.visualizer.setColor(self.graph.node[n]["shape"], Color(229, 122, 41, 255))


    def initGraphVisualization(self):
        nodeRadius = 0.5
        thickness = 0.15
        for s, f in self.graph.edges():
            sv = Vector2(*self.graph.node[s]["position"])
            fv = Vector2(*self.graph.node[f]["position"])
            l = (fv - sv).length()
            d = (fv - sv).normalized()
            b = sv + d * (l - nodeRadius)
            e = fv - d * (l - nodeRadius)
            self.graph[s][f]["shape"] = self.visualizer.addLine(b, e, 0.1, Color(255, 255, 255, 204))

        for n in self.graph.nodes():
            self.graph.node[n]["shape"] = self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius, True, thickness, Color(255, 255, 255, 153))
            self.visualizer.addCircle(Vector2(*self.graph.node[n]["position"]), nodeRadius + thickness, False, thickness, Color(178, 178, 178, 153))
