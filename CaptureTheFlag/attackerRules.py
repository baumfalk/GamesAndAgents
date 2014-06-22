from api import orders

#General attack rules.
## either move to enemy flag, midsection, our scoring point.


def attack_rule_1(bot,commander,knowledgeBase):
    """ 1. [3] if (our flag captured && at midsection) Attack enemy scoring point """
    if knowledgeBase.ourFlagCaptured and knowledgeBase.atMidsection(bot):
        commander.issue(orders.Attack, bot, knowledgeBase.findCloseSpot(commander.game.enemyTeam.flagScoreLocation,bot.position) ,description = "Attacker " + bot.name + " attack to enemy scoring point")
        return True
    return False


def attack_rule_2(bot,commander,knowledgeBase):
    """ 2. [3] if (our flag captured && at midsection) Charge closest side edges """
    if(knowledgeBase.ourFlagCaptured and knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.nearestSideEdge(bot)
        commander.issue(orders.Charge, bot, loc,description = "Attacker " + bot.name + " charge to nearest side edge")
        return True
    return False


def attack_rule_3(bot,commander,knowledgeBase):
    """ 3. [3] if (our flag captured && not at midsection) Attack at midsection """
    if((commander.game.team.flag.carrier != None) and not knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.getMidsection()
        commander.issue(orders.Attack, bot, loc,description = "Attacker " + bot.name + " attack to mid section")
        return True
    return False

	
def attack_rule_4(bot,commander,knowledgeBase):
    """ 4. [3] if (our flag captured && not at midsection) Charge (at closest side edges) """
    if((commander.game.team.flag.carrier != None) and not knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.nearestSideEdge(bot)
        commander.issue(orders.Charge, bot, loc,description = "Attacker " + bot.name + " charge to nearest side edge")
        return True
    return False


def attack_rule_5(bot,commander,knowledgeBase):
    """ 5. [2] if (flag picked up by enemy) Attack towards enemyCarrier position. """
    if((commander.game.team.flag.carrier != None)):
        loc = knowledgeBase.predictPosition(commander.game.team.flag.carrier)
        commander.issue(orders.Attack, bot, loc,description = "Attacker " + bot.name + " attack to enemy carrier")
        return True
    return False


def attack_rule_6(bot,commander,knowledgeBase):
    """ 6. [2] if (their flag is not picked up) Attack to enemy flag """
    if( (commander.game.enemyTeam.flag.carrier == None)):
        loc = commander.game.enemyTeam.flagSpawnLocation
        commander.issue(orders.Attack, bot, loc,description = "Attacker " + bot.name + " attacking towards to enemy flag spawn")
        return True
    return False


def attack_rule_7(bot,commander,knowledgeBase):
    """ 7. [0] if (our flag is in base && not in area near the midsection) Attack (to the midsection) """
    if((commander.game.team.flag.position == commander.game.team.flagSpawnLocation) and not knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.getMidsection()
        commander.issue(orders.Attack, bot, loc,description = "Attacker " + bot.name + " attacking towards midsection")
        return True
    return False


def attack_rule_8(bot,commander,knowledgeBase):
    """ 8. [0] if ( I'm closest to our flag carrier) Attack (To our flag carrier) """
    ourFlagCarrierPos = knowledgeBase.teamNearestFriend(bot).position
    if(ourFlagCarrierPos == commander.game.enemyTeam.flag.position):
        commander.issue(orders.Attack, bot, knowledgeBase.findCloseSpot(ourFlagCarrierPos,bot.position),description = "Attacker " + bot.name + " attacking towards our flag carrier")
        return True
    return False


def attack_rule_9(bot,commander,knowledgeBase):
    """ 9. [0] if ( I'm closest to our flag carrier) Charge (To our flag carrier) """
    ourFlagCarrierPos = knowledgeBase.teamNearestFriend(bot).position
    if(ourFlagCarrierPos == commander.game.enemyTeam.flag.position):
        commander.issue(orders.Charge, bot, knowledgeBase.findCloseSpot(ourFlagCarrierPos,bot.position),description = "Attacker " + bot.name + " charging towards our flag carrier")
        return True
    return False  



def attack_rule_10(bot,commander,knowledgeBase):
    """ 10.[0] if (we have their flag) Attack (towards our carrier along a short flanking path) #Try to intercept enemy flankers. """
    if( commander.game.enemyTeam.flag.carrier != None ):
        ourFlagCarrierPos = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createShortFlankingPath(bot.position,knowledgeBase.findCloseSpot(ourFlagCarrierPos,bot.position))
        commander.issue(orders.Attack, bot, path,description = "Attacker " + bot.name + " trying to intercept flanking bots via short route")
        return True
    return False  



def attack_rule_11(bot,commander,knowledgeBase):
    """ 11.[0] if (we have their flag) Attack (towards our carrier along a long flanking path) #Try to intercept enemy flankers. """
    if( commander.game.enemyTeam.flag.carrier != None ):
        ourFlagCarrierPos = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createLongFlankingPath(bot.position,knowledgeBase.findCloseSpot(ourFlagCarrierPos,bot.position))
        commander.issue(orders.Attack, bot, path,description = "Attacker " + bot.name + " trying to intercept flanking bots via long route")
        return True
    return False  


def attack_rule_12(bot,commander,knowledgeBase):
    """ 12.[0] if (no flags are captured) Attack ( flanking via short route towards enemy flag) """
    if( commander.game.team.flag.carrier == None and commander.game.enemyTeam.flag.carrier == None):
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Attack, bot, path,description = "Attacker " + bot.name + " flanking via short route towards enemy flag")
        return True
    return False


def attack_rule_13(bot,commander,knowledgeBase):
    """ 13.[0] if (no flags are captured) Attack ( flanking via long route towards enemy flag) """
    if( commander.game.team.flag.carrier == None and commander.game.enemyTeam.flag.carrier == None):
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Attack, bot, path,description = "Attacker " + bot.name + " flanking via long route towards enemy flag")
        return True
    return False


def attack_rule_14(bot,commander,knowledgeBase):
    """ 14.[0] if (we have their flag && i'm not the closest to our carrier) Attack (towards our carrier) """
    ourFlagCarrierPos = knowledgeBase.teamNearestFriend(bot).position
    if(  knowledgeBase.theirFlagCaptured and not(ourFlagCarrierPos == commander.game.enemyTeam.flag.position)):
        commander.issue(orders.Attack, bot, knowledgeBase.findCloseSpot(ourFlagCarrierPos,bot.position),description = "Attacker " + bot.name + " attacking towards our flag carrier")
        return True
    return False
	

def default_attacker_rule(bot,commander,knowledgeBase):
    """ The default attacker rule. """
    if(knowledgeBase.ourFlagCaptured and knowledgeBase.atMidsection(bot)):
        commander.issue(orders.Charge, bot, commander.game.enemyTeam.flag.position,description = "Attacker " + bot.name + " charge to enemy flag")
    else:
        commander.issue(orders.Charge, bot, knowledgeBase.findCloseSpot(knowledgeBase.enemyBase,bot.position),description = "Attacker " + bot.name + " charge to enemy base")
    return True