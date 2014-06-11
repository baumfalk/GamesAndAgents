from api import orders

#General defend rules.

def defendOurFlag(bot,commander,knowledgeBase):
    if(bot.position.distance(commander.game.team.flag.position) < commander.level.width / 3):
        commander.issue(orders.Attack,bot,commander.game.team.flag.position,description = "Defender " + bot.name + " intercept our flag")
        return True
    return False

def defendTheirFlagScoreLocation(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured):
        commander.issue(orders.Charge,bot,commander.game.enemyTeam.flagScoreLocation,description = "Defender " + bot.name + " charging to enemy flag location")
        commander.issue(orders.Defend,bot,commander.game.enemyTeam.flagScoreLocation,description = "Defender " + bot.name + " occupying enemy flag location")
        return True
    return False

def defendCampTheirBase(bot,commander,knowledgeBase):
    if(bot.position.distance(knowledgeBase.avgEnemyBotSpawn) < commander.level.width / 3):
        commander.issue(orders.Attack,bot,knowledgeBase.avgEnemyBotSpawn,description = "Defender " + bot.name + " camp enemy spawn point")
        commander.issue(orders.Defend,bot,knowledgeBase.avgEnemyBotSpawn,description = "Defender " + bot.name + " camping enemy spawn point")
        return True
    return False

def defendSpread(bot,commander,knowledgeBase):
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

def defendGetNearestEnemy(bot,commander,knowledgeBase):
    nearestEnemyPos = knowledgeBase.predictNearestEnemy(bot).position
    if(bot.position.distance(nearestEnemyPos) < commander.level.width / 5): #Close to an enemy.
        commander.issue(orders.Attack,bot,nearestEnemyPos,description = "Defender " + bot.name + " approaching close enemy")
        return True
    return False

def defendSpin(bot,commander,knowledgeBase):
    nearestFriendPos = knowledgeBase.teamNearestFriend(bot).position
    if(bot.position.distance(nearestFriendPos) < commander.level.width / 12): #Not close to a friend.
        commander.issue(orders.Defend,bot,knowledgeBase.randomDirection(),description = "Defender " + bot.name + " looking in a random direction")
        return True
    return False

def defendFlankEnemy(bot,commander,knowledgeBase):
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
    if knowledgeBase.ourFlagCaptured:
        commander.issue(orders.Charge,bot,commander.game.team.flag.position, description = "Catcher "+ bot.name + " Charge our socre location")
    elif knowledgeBase.atMidsection(bot):
        commander.issue(orders.Charge,bot,commander.game.team.flag.position, description = "Catcher "+ bot.name + " Charge our socre location")
    else:
        commander.issue(orders.Charge,bot,knowledgeBase.getMidsection(bot), description = "Catcher "+ bot.name + " Charge our socre location")
    return True