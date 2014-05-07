#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception import framework


class WeaponCommand(framework.Event):
    pass

class WeaponFireShotCommand(WeaponCommand):
    def __init__(self, weapon, target):
        super(WeaponFireShotCommand, self).__init__()
        self.weapon = weapon
        self.target = target

class WeaponKillTargetCommand(WeaponCommand):
    def __init__(self, weapon, target):
        super(WeaponKillTargetCommand, self).__init__()
        self.weapon = weapon
        self.target = target

class WeaponClearTargetCommand(WeaponCommand):
    def __init__(self, weapon):
        super(WeaponClearTargetCommand, self).__init__()
        self.weapon = weapon


class ChangeTargetCommand(framework.Event):
    def __init__(self, bot, target):
        super(ChangeTargetCommand, self).__init__()
        self.bot = bot
        self.target = target
