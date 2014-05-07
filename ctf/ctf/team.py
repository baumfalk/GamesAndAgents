#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception import framework
from inception.math import Vector3, Situation, QuaternionFromLookAt, QuaternionFromFacingDirection


class Team(framework.Model):
    """Part of the game state representing a single team of bots."""

    def __init__(self, teamConfig, gameState, eventDispatcher, mapUtilities):
        super(Team, self).__init__()
        self.teamConfig = teamConfig
        self.gameState = gameState
        self.eventDispatcher = eventDispatcher
        self.mapUtilities = mapUtilities
        self.name = teamConfig.name
        self.members = set()
        self.ragdollControllers = {}
        self.flag = None
        self.score = 0


    def getFlagBasePositionsForEnemyTeams(self):
        """Determine all enemy teams and return their flag spawn locations."""
        teamFlagPositions = []
        for t in self.gameState.teams:
            if t != self and t.flag:
                teamFlagPositions.append((t.name, t.flag.resetPosition))
        return teamFlagPositions


    def findSpawnLocation(self, bot):
        """Find a free position for this bot to spawn within the base."""

        # See if there's a specific spawn point for this bot.
        if bot.name in self.teamConfig.botSpawnLocations:
            location = self.teamConfig.botSpawnLocations[bot.name]
            position = Vector3(location[0].x, 0, location[0].y)
            orientation = QuaternionFromFacingDirection(Vector3(location[1].x, 0, location[1].y), Vector3.UNIT_Y)
            return Situation(position, orientation)

        # If a starting position is not specified find a random position in the spawn area.
        else:
            area = self.teamConfig.botSpawnArea
            spawnAreaMin = Vector3(area[0].x, 0.0, area[0].y)
            spawnAreaMax = Vector3(area[1].x, 0.0, area[1].y)

            position = Vector3.ZERO
            if not self.mapUtilities.findRandomFreePositionInBox(spawnAreaMin, spawnAreaMax, 0.3, 100, position):
                assert False, "No spawn position found for {}".format(bot.name)

            # Compute an orientation facing the flag so it's symmetrical on both sides.
            flagPosition = Vector3(self.flag.resetPosition.x, 0.0 , self.flag.resetPosition.y)
            orientation = QuaternionFromLookAt(position, flagPosition, Vector3.UNIT_Y)
            return Situation(position, orientation)


    def inSpawnLocation(self, position):
        """Check if a given position lies inside the spawn area of this team."""
        area = self.teamConfig.botSpawnArea
        if area is None:
            return False
        return position.x >= area[0].x and position.x <= area[1].x and position.z >= area[0].y and position.z <= area[1].y
