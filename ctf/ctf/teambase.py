#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception import framework
from inception.math import Vector3
from inception.framework import LocationComponent
from inception.rendering import GraphicalRepresentation
from inception.simulation import Zone
from inception import overlay

from ctf.events import ScoreChangedEvent
from ctf.gameconfig import GameConfig


class TeamBase(framework.Model):
    """The game state for a team's home base, where the bots spawn.

    This is part of the world model, and stores information about the base as
    well as sub-components representing the actual base itself.
    """

    def __init__(self, teamConfig, teamName, gameState):
        """Initializes this team base component as a composite of a location, label
        and a zone."""

        super(TeamBase, self).__init__()

        self.game = gameState
        self.config = teamConfig
        self.teamName = teamName
        area = teamConfig.botSpawnArea

        minSpawnExtents = Vector3(area[0].x, 0, area[0].y)
        maxSpawnExtents = Vector3(area[1].x, 0, area[1].y)
        position = (minSpawnExtents + maxSpawnExtents) / 2
        dimensions = maxSpawnExtents - minSpawnExtents

        base = Zone(position, dimensions, "Plane/DashedOutline") #Zone_"+teamConfig.name.capitalize())
        base.color = teamConfig.getColor()
        self.addState(base)

        self.location = LocationComponent()
        self.location.setPosition(position)
        self.addState(self.location)


class TeamBaseRepresentation(GraphicalRepresentation):

    def __init__(self, entity):
        super(TeamBaseRepresentation, self).__init__(entity)
        self.state = entity
        self.score = None

    def setup(self, renderer):

        self.visualizer = renderer.findVisualizerPlugin()
        self.renderer = renderer
        self.overlay = renderer.findPlugin(overlay.RocketPlugin).findDynamicOverlay()

        self.element = self.overlay.addElement("base-label")        
        col = self.state.config.getColor()
        self.overlay.setProperty(self.element, "color", "rgba(%i,%i,%i,255)" % (col.r*255.0, col.g*255.0, col.b*255.0))

        self.state.game.subscribe(ScoreChangedEvent, self.onScoreChanged)

        self.updateLabelText(0)
        #self.tick()  # Temp. fix for a bug in calculateScreenCoordinates()

    def onScoreChanged(self, event):
        self.score = event.scores[self.state.config.name]

    def updateLabelText(self, score):
        self.overlay.setText(self.element, self.state.teamName + "<br/>(%i)" % (score,))

    def tick(self, dt=0.0):
        if self.overlay is None:
            return

        pos = self.state.location.getPosition()
        self.overlay.setPosition(self.element, self.renderer.calculateScreenCoordinates(pos))

        if self.score is not None:
            self.updateLabelText(self.score)

    def teardown(self, renderer):
        self.state.game.unsubscribe(ScoreChangedEvent, self.onScoreChanged)
