#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

import math
from inception.math import Vector3

class GameConfig():
    MAX_FOV_ANGLE = math.pi/2.0
    MOVING_FOV_ANGLE = math.pi/2.0
    DEFEND_FOV_ANGLE = math.pi/6.0
    IDLE_FOV_ANGLE = math.pi*2.0

    SHOOTING_DISTANCE = 15.0
    SHOOTING_DISTANCE_DEFEND = 15.0
    SHOOTING_DISTANCE_IDLE = 5.0
    SHOOTING_TARGETTING_BONUS = 5.0
    LOS_OFFSET = Vector3(0.0, 1.5, 0.0)
    VISIBILITY_MINIMUM_DISTANCE = 2.5           # circle around character in which he sees everything
    VISIBILITY_DISTANCE = 250.0

    VISIBILITY_DISTANCE_DEFEND = 250.0
    VISIBILITY_DISTANCE_IDLE = 5.0
    SPAWN_IMMUNE_TIME = 2.5

    INITIAL_HEALTH = 100.0
    HEALTH_REGEN_DELAY = -1.0        # no health regeneration
    HEALTH_REGEN_RATE = 0.0

    CHARACTER_RADIUS = 0.25

    WALKING_SPEED = 3.0              # the walking speed in m/s
    STRAFING_SPEED = 2.5             # speed in m/s when looking at target
    RUNNING_SPEED = 6.0              # the running speed in m/s
    TURNING_SPEED = 2.5              # turning speed in radians/s

    AQUIRE_TARGET_DELAY = 0.1*3                     # initial delay no matter what
    TURNING_PENALTY_PER_RAD = 1.0 / TURNING_SPEED   # delay to firing at a given angle offset (seconds/radian)
    RELOAD_DELAY = 0.38*4                           # delay to reload
    RELOAD_DELAY_DEFEND = RELOAD_DELAY              #

    DEFEND_TURN_SNAP = True
    DEFEND_TURN_PENALTY = 0.5

    WALKING_FIRE_PENALTY = 0.21*3
    RUNNING_FIRE_PENALTY = 0.36*3
    WEAPON_DAMAGE = 200.0            # one shot one kill

    WAYPOINT_MIN_DISTANCE = 1.5

    ORDER_DELAY = 1.0
    ORDER_FROM_IDLE_DELAY = 0.5
    ORDER_DEFEND_DELAY = 2.0
    ORDER_REPEAT_ORDER_DELAY = 1.0
    ORDER_HOLDING_DELAY = 0.0

    PERCEPTION_EVENT_REACTION_TIME = 0.7
    PERCEPTION_IGNORE_EVENTS_AFTER = 2.0

    MAX_FIRE_DELAY = max(RELOAD_DELAY, AQUIRE_TARGET_DELAY, WALKING_FIRE_PENALTY, RUNNING_FIRE_PENALTY)+TURNING_PENALTY_PER_RAD*MAX_FOV_ANGLE

    DEFAULT_TEAMBASE_FONTSIZE = 32.0

    DEFAULT_NETWORK_PORT = 41041
