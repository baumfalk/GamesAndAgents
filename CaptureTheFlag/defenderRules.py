from api import orders
from api.vector2 import Vector2

#General defend rules.

def defend_rule_1(bot,commander,knowledgeBase):
    """ 1. if (flag is close) Move (to flag) """
    if(bot.position.distance(commander.game.team.flag.position) < commander.level.width / 3):
        campspot = knowledgeBase.findCampSpot(commander.game.team.flag.position)
        diff = commander.game.team.flag.position - campspot
        toClosestEnemy = knowledgeBase.predictNearestEnemy(bot).position - campspot
        if(bot.position.distance(campspot) > 2):
            commander.issue(orders.Attack,bot,campspot,description = "Defender " + bot.name + " camp our flag")
        else:
            commander.issue(orders.Defend,bot,[(diff,1.0),(toClosestEnemy,1.0)],description = "Defender " + bot.name + " camping our flag")
        return True
    return False

def defend_rule_2(bot,commander,knowledgeBase):
    """ 2. if (our flag is captured) Charge (to enemy flag score campspot) and Defend """
    if(knowledgeBase.ourFlagCaptured):
        campspot = knowledgeBase.findCampSpot(commander.game.enemyTeam.flagScoreLocation)
        diff = commander.game.enemyTeam.flagScoreLocation - campspot
        toClosestEnemy = knowledgeBase.predictNearestEnemy(bot).position - campspot
        if(bot.position.distance(campspot) > 2):
            commander.issue(orders.Charge,bot,campspot,description = "Defender " + bot.name + " camp enemy flag score location")
        else:
            commander.issue(orders.Defend,bot,[(diff,1.0),(toClosestEnemy,1.0)],description = "Defender " + bot.name + " camping enemy flag score location")
        return True
    return False

def defend_rule_3(bot,commander,knowledgeBase):
    """ 3. if (enemy spawn is close) Move (to enemy spawn campspot) and Defend """
    if(bot.position.distance(knowledgeBase.avgEnemyBotSpawn) < commander.level.width / 3):
        campspot = knowledgeBase.findCampSpot(knowledgeBase.avgEnemyBotSpawn)
        diff = knowledgeBase.avgEnemyBotSpawn - campspot
        toClosestEnemy = knowledgeBase.predictNearestEnemy(bot).position - campspot
        if(bot.position.distance(campspot) > 2):
            commander.issue(orders.Attack,bot,campspot,description = "Defender " + bot.name + " camp enemy spawn point")
        else:
            commander.issue(orders.Defend,bot,[(diff,1.0),(toClosestEnemy,1.0)],description = "Defender " + bot.name + " camping enemy spawn point")
        return True
    return False

def defend_rule_4(bot,commander,knowledgeBase):
    """ 4. if (friend is close) Move (spread out) """
    nearestFriendPos = knowledgeBase.teamNearestFriend(bot).position
    if(bot.position.distance(nearestFriendPos) < commander.level.width / 12): #Close to a friend.
        differenceVec = bot.position - nearestFriendPos
        if(differenceVec.length() > 0): #Can only normalise non-zero vectors.
            differenceVec.normalize()
        else:
            differenceVec = knowledgeBase.randomDirection()
        newPosition = nearestFriendPos + differenceVec * commander.level.width / 12
        commander.issue(orders.Charge,bot,newPosition,description = "Defender " + bot.name + " spreading out.")
        return True
    return False

def defend_rule_5(bot,commander,knowledgeBase):
    """ 5. if (enemy is close) Move (to enemy) """
    nearestEnemyPos = knowledgeBase.predictNearestEnemy(bot).position
    if(bot.position.distance(nearestEnemyPos) < commander.level.width / 5): #Close to an enemy.
        commander.issue(orders.Attack,bot,nearestEnemyPos,description = "Defender " + bot.name + " approaching close enemy")
        return True
    return False

def defend_rule_6(bot,commander,knowledgeBase):
    """ 6. if (not close to friend) Defend (look in a random direction) """
    nearestFriendPos = knowledgeBase.teamNearestFriend(bot).position
    if(bot.position.distance(nearestFriendPos) < commander.level.width / 12): #Not close to a friend.
        commander.issue(orders.Defend,bot,knowledgeBase.randomDirection(),description = "Defender " + bot.name + " looking in a random direction")
        return True
    return False

def defend_rule_7(bot,commander,knowledgeBase):
    """ if (close to enemy) Move (flank enemy) """
    nearestEnemy = knowledgeBase.predictNearestEnemy(bot)
    if(bot.position.distance(nearestEnemy.position) < commander.level.width / 8): #Close to an enemy.
        flankpath = knowledgeBase.createShortFlankingPath(bot.position,nearestEnemy.position)
        commander.issue(orders.Attack,bot,flankpath,description = "Defender " + bot.name + " flanking nearest enemy.")
        return True
    return False
	
"""
	The default defender rule.
"""	
def default_defender_rule(bot,commander,knowledgeBase):
    """ if (our flag captured or at midsection) Charge (to enemy score location) else Charge (to midsection) """
    if knowledgeBase.ourFlagCaptured:
        commander.issue(orders.Charge,bot,commander.game.team.flag.position, description = "Defender " + bot.name + " Charge our score location")
    elif knowledgeBase.atMidsection(bot):
        commander.issue(orders.Charge,bot,commander.game.team.flag.position, description = "Defender " + bot.name + " Charge our score location")
    else:
        commander.issue(orders.Charge,bot,knowledgeBase.getMidsection(), description = "Catcher " + bot.name + " Charge midsection")
    return True