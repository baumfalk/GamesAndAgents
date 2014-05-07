from inception.math import ColorValue

import api
from api.vector2 import Vector2
from ctf.levelconfig import LevelConfig


class TestConfig(LevelConfig):
    def __init__(self):
        super(TestConfig, self).__init__()

        self.map = 'test01.png'

        red = self.TeamConfig()
        red.name = 'Red'
        red.color = ColorValue.Red
        red.flagSpawnLocation = Vector2(2.0, 10.0)
        red.flagScoreLocation = Vector2(2.0, 20.0)
        red.botSpawnArea = (Vector2(0.0, 0.0), Vector2(4.0, 4.0))
        self.teamConfigs[red.name] = red
        self.teams.append(red)
        self.red = red

        blue = self.TeamConfig()
        blue.name = 'Blue'
        blue.color = ColorValue.Blue
        blue.flagSpawnLocation = Vector2(18.0, 10.0)
        blue.flagScoreLocation = Vector2(18.0, 20.0)
        blue.botSpawnArea = (Vector2(16.0, 0.0), Vector2(20.0, 4.0))
        self.teamConfigs[blue.name] = blue
        self.teams.append(blue)
        self.blue = blue

        self.gameLength = 0

