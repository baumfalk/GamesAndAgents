#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

"""Various classes and functions related to bot orders sent to the server.
"""

import math

from inception.math import Vector2, Vector3, Quaternion, QuaternionFromFacingDirection, QuaternionFromRotationAroundY, Situation
from inception.navigation import Waypoint, NavigationStatus, RegionPassabilityFlags
from inception.motion import Motion, LocomotionComponent

from ctf.gameconfig import GameConfig
from api import vector2
from api import orders

from aisbx.actor.navigation import NavigationComponent
from aisbx.actor.interface.navigation import NavigationCallback

import api.gameinfo as gameinfo


from aisbx import logger
log = logger.getLog(logger.LOG_APP)


def filterWaypoints(waypoints):
    """Filter a given list of (attack) waypoints.

    Multiple waypoints sent in one bot order need to have a minimum distance
    of GameConfig.WAYPOINT_MIN_DISTANCE in between. This function filters out
    all those waypoints in the given list that are not far enough from the first
    (or lastly checked) waypoint.

    Args:
        waypoints: The list of wapoints to check

    Returns:
        The filtered list of waypoints
    """
    filtered_waypoints = waypoints
    if len(waypoints) >= 2:
        cur_waypoint = waypoints[0]
        filtered_waypoints = [waypoints[0]]
        for w in waypoints:
            assert type(w) == type(cur_waypoint)
            if( (w-cur_waypoint).length() > GameConfig.WAYPOINT_MIN_DISTANCE):
                filtered_waypoints.append(w)
                cur_waypoint = w
    return filtered_waypoints


def fixupOrderPositions(positions, bot):
    """Fix positions received from a bot.

    This function uses the bots navigation component to check for valid positions
    based on region.checkPassable(). If a given point is not passable, then get a close
    alternative with region.findClosestPassableNode().

    Args:
        positions: A list of positions/waypoints
        bot: The bot that sent the order

    Returns:
        The list of fixed positions
    """

    navC = bot.actor.getComponent(NavigationComponent)
    if not navC:
        return positions

    navS = navC.getNavigationSystem()
    pathfinder = navS.getPathfinder()
    region = pathfinder.getRegion()

    outpositions = []
    for position in positions:
        index = region.getIndexForPosition(Vector3(position.x, 0, position.y))
        if region.checkPassable(index, RegionPassabilityFlags.OBSTACLES_ALL):
            outpositions.append(position)
        else:
            index = region.findClosestPassableNode(Vector3(position.x, 0, position.y))
            if region.checkPassable(index, RegionPassabilityFlags.OBSTACLES_ALL):
                v3 = region.getPositionForIndex(index)
                outpositions.append(vector2.Vector2(v3.x, v3.z))
            else:
                pass

    return outpositions


def createOrder(order, bot):
    """Create a class instance of the given order type.

    Helper function that checks for valid bot order. It creates and returns
    an instance of either `DefendOrder`, `MoveOrder`, `AttackOrder`, or
    `ChargeOrder`.

    Args:
        apiOrder: Instance of the according order class from the API
        bot: The bot that sent this order to the server

    Returns:
        The newly created class instance, or None if unkonwn order provided
    """
    if isinstance(order, orders.Defend):
        return DefendOrder(order.botId, order.facingDirection)
    elif isinstance(order, orders.Move):
        return MoveOrder(order.botId, fixupOrderPositions(order.target, bot))
    elif isinstance(order, orders.Attack):
        return AttackOrder(order.botId, fixupOrderPositions(order.target, bot), order.lookAt)
    elif isinstance(order, orders.Charge):
        return ChargeOrder(order.botId, fixupOrderPositions(order.target, bot))
    else:
        assert 'Unknown order {}'.format(order)
        return None


def calculateTurningFirePenalty(facingDirection, desiredFacingDirection):
    """Helper function for calculating the firing penalty from turning.

    Args:
        facingDirection: The bot's current facing direction
        desiredFacingDirection: The new, desired facing direction

    Returns:
        The penalty calculated for the angle the bot needs to turn
    """
    angleRadians = facingDirection.angleBetween(desiredFacingDirection)
    angle = max(0, abs(angleRadians.valueRadians())-0.05)
    turningFirePenalty = GameConfig.TURNING_PENALTY_PER_RAD * angle
    return turningFirePenalty


def calculateNewFacingDirection(facingDirection, desiredFacingDirection, dt):
    """Helper function for calculating a new facing direction.
    """
    facingDirection2d = Vector2(facingDirection.x, facingDirection.z)
    desiredFacingDirection2d = Vector2(desiredFacingDirection.x, desiredFacingDirection.z)
    angleRadians = desiredFacingDirection2d.angleTo(facingDirection2d)
    rotationAngle = angleRadians.valueRadians()
    if rotationAngle > math.pi:
        rotationAngle -= 2 * math.pi
    maxTurningAngle = GameConfig.TURNING_SPEED * dt
    remainingAngleToTarget = 0.0
    if rotationAngle > maxTurningAngle:
        remainingAngleToTarget = rotationAngle - maxTurningAngle
        rotationAngle = maxTurningAngle
    elif rotationAngle < -maxTurningAngle:
        remainingAngleToTarget = rotationAngle + maxTurningAngle
        rotationAngle = -maxTurningAngle
    newFacingDirection = QuaternionFromRotationAroundY(rotationAngle) * facingDirection
    newFacingDirection.y = 0.0 # clamp to x,z plane
    return newFacingDirection, remainingAngleToTarget


class DefendOrder(object):
    """This class represents a bot's "defend" order sent by a commander
    """

    def __init__(self, botId, facingDirections):
        super(DefendOrder, self).__init__()
        self.botId = botId
        self.bot = None
        self.stopped = False
        self.facingDirections = facingDirections
        self.nextFacingDirectionIndex = 0
        self.currentPauseTime = 0.0
        self.botState = gameinfo.BotInfo.STATE_DEFENDING


    def execute(self, bot):
        assert bot.name == self.botId
        self.bot = bot
        self.stopped = False
        if not self.facingDirections:
            facingDirection = self.bot.location.getOrientation() * Vector3.UNIT_Z
            self.facingDirections = [(Vector2(facingDirection.x, facingDirection.z), 0)]
        self.nextFacingDirectionIndex = 0
        self.currentPauseTime = 0.0
        bot.targetingComponent.enabled = True
        self.tick(0)


    def tick(self, dt):
        # stop the bot
        if not self.stopped:
            self.stopped = True
            self.bot.actor.getComponent(NavigationComponent).clearWaypoints()
            self.bot.locomotionComponent.cancelLockTarget()
            self.bot.locomotionComponent.setStyle(Motion.Motion_Crouch)

        targetFacingDirection, targetPauseTime = self.facingDirections[self.nextFacingDirectionIndex]
        if targetPauseTime < 1.0: # minimum pause time
            targetPauseTime = 1.0
        if (self.currentPauseTime >= targetPauseTime) or targetFacingDirection.isZeroLength():
            self.currentPauseTime = 0.0
            self.nextFacingDirectionIndex += 1
            if self.nextFacingDirectionIndex >= len(self.facingDirections):
                self.nextFacingDirectionIndex = 0
            targetFacingDirection, _ = self.facingDirections[self.nextFacingDirectionIndex]
        targetFacingDirection = Vector3(targetFacingDirection.x, 0, targetFacingDirection.y)

        currentFacingDirection = self.bot.location.getOrientation() * Vector3.UNIT_Z
        if GameConfig.DEFEND_TURN_SNAP:
            newFacingDirection = targetFacingDirection
            remainingAngleToTarget = 0.0
            angle = Vector2(currentFacingDirection.x, currentFacingDirection.z).angleBetween(Vector2(targetFacingDirection.x, targetFacingDirection.z))
            penalty = max(0, abs(angle.valueRadians())-0.01) / GameConfig.TURNING_SPEED
            if penalty > 0:
                self.bot.setFirePenalty(GameConfig.DEFEND_TURN_PENALTY + penalty, 'defend snap')
        else:
            newFacingDirection, remainingAngleToTarget = calculateNewFacingDirection(currentFacingDirection, targetFacingDirection, dt)

        position = self.bot.location.getPosition()
        orientation = QuaternionFromFacingDirection(newFacingDirection, Vector3.UNIT_Y)
        self.bot.location.teleport(Situation(position, orientation))

        if abs(remainingAngleToTarget) < 0.05:
            self.currentPauseTime += dt


    def isCompleted(self):
        return False

    def check(self, bot):
        return True

    def __repr__(self):
        return 'Defend'


class MoveOrder(object):
    """This class represents a bot's "move" order sent by a commander.
    """
    def __init__(self, botId, target):
        super(MoveOrder, self).__init__()
        self.botId = botId
        self.bot = None
        self.target = target
        self.botState = gameinfo.BotInfo.STATE_MOVING


    def execute(self, bot):
        assert bot.name == self.botId
        self.bot = bot
        if type(self.target) == list:
            bot.actor.getComponent(NavigationComponent).moveToLocation([Waypoint(Vector3(t.x, 0.0, t.y), 0.3, "move target") for t in self.target])
        else:
            bot.actor.getComponent(NavigationComponent).moveToLocation([Waypoint(Vector3(self.target.x, 0.0, self.target.y), 0.3, "move target")])

        bot.locomotionComponent.cancelLockTarget()
        bot.locomotionComponent.setStyle(Motion.Motion_Run)
        bot.targetingComponent.enabled = False


    def tick(self, dt):
        self.bot.setFirePenalty(max(self.bot.firePenalty, GameConfig.RUNNING_FIRE_PENALTY), 'move')


    def isCompleted(self):
        return self.bot.actor.getComponent(NavigationComponent).getStatus() != NavigationStatus.NavigationInProgress


    def check(self, bot):
        return bot.actor.getComponent(NavigationComponent).isValidMoveTarget(self.target)


    def __repr__(self):
        return 'Sprint'


class AttackOrder(object):
    """This class represents a bot's "attack" order sent by a commander.
    """
    def __init__(self, botId, target, lookAt):
        super(AttackOrder, self).__init__()
        self.botId = botId
        self.bot = None
        self.target = target
        self.lookAt = lookAt
        self.paused = False


    def getBotState(self):
        if self.paused:
            return gameinfo.BotInfo.STATE_HOLDING
        else:
            return gameinfo.BotInfo.STATE_ATTACKING
    botState = property(getBotState)


    def execute(self, bot):
        assert bot.name == self.botId
        self.bot = bot

        if self.lookAt is not None:
            bot.locomotionComponent.setStyle(Motion.Motion_Strafing)
            bot.locomotionComponent.lookAtPosition(Vector3(self.lookAt.x, 0, self.lookAt.y))
        else:
            bot.locomotionComponent.setStyle(Motion.Motion_Walk)
            bot.locomotionComponent.cancelLockTarget()

        if type(self.target) == list:
            filtered_targets = filterWaypoints(self.target)
            bot.actor.getComponent(NavigationComponent).moveToLocation([Waypoint(Vector3(t.x, 0.0, t.y), 0.3, "attack target") for t in filtered_targets])
        else:
            bot.actor.getComponent(NavigationComponent).moveToLocation([Waypoint(Vector3(self.target.x, 0.0, self.target.y), 0.3, "attack target")])

        bot.targetingComponent.enabled = True
        self.paused = False
        self.tick(0)


    def tick(self, dt):
        self.bot.setFirePenalty(max(self.bot.firePenalty, GameConfig.WALKING_FIRE_PENALTY), 'attack')

        position = self.bot.location.getPosition()
        botsThatCanSeeUs = set(a.characterComponent for a in self.bot.perceptionComponent.getPerceivableByPerceivable())

        # don't walk into the firing range of bots that can already see us
        if not self.paused:
            remainingWaypoints = self.bot.actor.getComponent(NavigationComponent).getRemainingWaypoints()
            assert len(remainingWaypoints) > 0
            target = remainingWaypoints[0].getPosition() # TODO: replace this with self.bot.actor.getComponent(NavigationComponent).getCurrentTarget().translation
        else:
            target = Vector3(self.target[0].x, 0.0, self.target[0].y)
        movementDirection = (target - position)
        movementDirection.normalize()
        positionInOneMeter = position + 1.5 * movementDirection
        botsThatWillBeAbleToShootUs = [b for b in botsThatCanSeeUs if positionInOneMeter.squaredDistance(b.location.getPosition()) < GameConfig.SHOOTING_DISTANCE * GameConfig.SHOOTING_DISTANCE] # TODO: handle defend distance being different

        if not self.paused and len(botsThatWillBeAbleToShootUs) > 0:
            # stop the bot if someone will kill us if we keep going
            if len(remainingWaypoints) > 0:
                self.target = [vector2.Vector2(w.getPosition().x, w.getPosition().z) for w in remainingWaypoints]
            self.bot.actor.getComponent(NavigationComponent).clearWaypoints()
            self.bot.locomotionComponent.cancelLockTarget()
            self.bot.locomotionComponent.setIdle()
            self.paused = True
            return
        elif self.paused and len(botsThatWillBeAbleToShootUs) == 0:
            # resume moving if no-one is going to kill us
            self.execute(self.bot)


    def isCompleted(self):
        return not self.paused and (self.bot.actor.getComponent(NavigationComponent).getStatus() != NavigationStatus.NavigationInProgress)


    def check(self, bot):
        return bot.actor.getComponent(NavigationComponent).isValidMoveTarget(self.target)


    def __repr__(self):
        return 'Attack'


class ChargeOrder(object):
    """This class represents a bot's "charge" order sent by a commander.
    """
    def __init__(self, botId, target):
        super(ChargeOrder, self).__init__()
        self.botId = botId
        self.bot = None
        self.target = target
        self.botState = gameinfo.BotInfo.STATE_CHARGING


    def execute(self, bot):
        assert bot.name == self.botId
        self.bot = bot
        if type(self.target) == list:
            filtered_targets = filterWaypoints(self.target)
            bot.actor.getComponent(NavigationComponent).moveToLocation([Waypoint(Vector3(t.x, 0.0, t.y), 0.3, "charge target") for t in filtered_targets])
        else:
            bot.actor.getComponent(NavigationComponent).moveToLocation([Waypoint(Vector3(self.target.x, 0.0, self.target.y), 0.3, "charge target")])

        bot.locomotionComponent.cancelLockTarget()
        bot.locomotionComponent.setStyle(Motion.Motion_Run)
        bot.targetingComponent.enabled = True
        self.tick(0)


    def tick(self, dt):
        self.bot.setFirePenalty(max(self.bot.firePenalty, GameConfig.RUNNING_FIRE_PENALTY), 'charge')


    def isCompleted(self):
        return self.bot.actor.getComponent(NavigationComponent).getStatus() != NavigationStatus.NavigationInProgress


    def check(self, bot):
        return bot.actor.getComponent(NavigationComponent).isValidMoveTarget(self.target)


    def __repr__(self):
        return 'Charge'


def calcLookat(position, target, up, fallbackrotation):
    """
    computes the rotation from a position to a given target
    if target and position are the same use fallbackrotation
    """
    z = target - position
    q = fallbackrotation
    if z != Vector3.ZERO:
        z.normalize()
        x = up.crossProduct(z)
        assert(x != Vector3.ZERO)
        x.normalize()
        y = z.crossProduct(x)
        y.normalize()
        q = Quaternion(x, y, z)
    return q


class TakingOrders(object):
    def __init__(self, botId, nextOrder):
        super(TakingOrders, self).__init__()
        self.botId = botId
        self.bot = None
        self.nextOrder = nextOrder
        self.botCommand = None
        self.delay = 0
        self.timer = 0
        self.botState = gameinfo.BotInfo.STATE_TAKINGORDERS
        self.quiet = False


    def execute(self, bot):
        self.bot = bot
        self.botCommand = createOrder(self.nextOrder, bot)

        if (bot.currentAction and bot.currentAction.botState == gameinfo.BotInfo.STATE_DEFENDING) \
        or (self.botCommand and self.botCommand.botState == gameinfo.BotInfo.STATE_DEFENDING):
            self.delay = GameConfig.ORDER_DEFEND_DELAY
        elif bot.currentAction and bot.currentAction.botState == gameinfo.BotInfo.STATE_HOLDING:
            self.delay = GameConfig.ORDER_HOLDING_DELAY
        elif not bot.currentAction or bot.currentAction.botState == gameinfo.BotInfo.STATE_IDLE:
            self.delay = GameConfig.ORDER_FROM_IDLE_DELAY
        elif bot.currentAction and self.botCommand and self.botCommand.botState == bot.currentAction.botState:
            self.delay = GameConfig.ORDER_REPEAT_ORDER_DELAY
        else:
            self.delay = GameConfig.ORDER_DELAY
        self.timer = self.delay

        if self.delay > 0.0:
            bot.actor.getComponent(NavigationComponent).clearWaypoints()
            bot.locomotionComponent.cancelLockTarget()
            bot.locomotionComponent.setStyle(Motion.Motion_TakeOrders)
        else:
            self.tick(0.0)


    def tick(self, dt):
        self.timer -= dt
        if self.timer > 0.0:
            return

        if self.bot.checkOrder(self.botCommand):
            # self.output = True
            self.bot.executeOrder(self.botCommand)
        elif not self.quiet:
            log.error("Invalid order for %s: %s" % (self.bot.name, self.nextOrder))


    def isCompleted(self):
        return self.bot and not self.bot.checkOrder(self.botCommand)

    def check(self, bot):
        return bot.checkOrder(self.botCommand)

    def __repr__(self):
        return 'TakingOrders'


class ShootAtCommand(object):
    def __init__(self, botId, targetBotId):
        super(ShootAtCommand, self).__init__()
        self.botId = botId
        self.bot = None
        self.targetBotId = targetBotId
        self.botState = gameinfo.BotInfo.STATE_SHOOTING
        self.target = None


    def execute(self, bot):
        assert bot.name == self.botId
        self.bot = bot
        # stop the bot
        bot.actor.getComponent(NavigationComponent).clearWaypoints()
        bot.locomotionComponent.cancelLockTarget()
        self.bot.locomotionComponent.setStyle(Motion.Motion_Aim)

        self.target = self.bot.team.gameState.bots[self.targetBotId]
        bot.targetingComponent.target = self.bot.team.gameState.bots[self.targetBotId]

        # calculate the fire penalty based on the turning angle
        currentFacingDirection = self.bot.location.getOrientation() * Vector3.UNIT_Z
        targetDirection = self.target.location.getPosition() - self.bot.location.getPosition()
        turningFirePenalty = calculateTurningFirePenalty(currentFacingDirection, targetDirection)
        bot.setFirePenalty(bot.firePenalty + turningFirePenalty, 'shootat')


    def tick(self, dt):
        if self.target and self.target.health.points > 0:
            currentFacingDirection = self.bot.location.getOrientation() * Vector3.UNIT_Z
            targetDirection = self.target.location.getPosition() - self.bot.location.getPosition()
            newFacingDirection, _ = calculateNewFacingDirection(currentFacingDirection, targetDirection, dt)

            position = self.bot.location.getPosition()
            orientation = QuaternionFromFacingDirection(newFacingDirection, Vector3.UNIT_Y)
            self.bot.location.teleport(Situation(position, orientation))

            if self.bot.weapon and (self.bot.firePenalty <= 0):
                self.bot.weapon.target = self.target
        else:
            # don't try to shoot a dead person
            self.target = None


    def isCompleted(self):
        return not self.target or self.target.health.points <= 0

    def check(self, bot):
        return True

    def onLoseTarget(self, target):
        self.target = None

    def __repr__(self):
        return 'ShootAt'

