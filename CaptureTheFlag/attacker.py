from api import orders

#General attack rules.

"""
1. [3] if (our flag captured && at midsection)
    Charge enemy base
"""
def attack_rule_1(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured and knowledgeBase.atMidsection(bot)):
        commander.issue(orders.Charge, bot, knowledgeBase.enemyBase,description = "Attacker" + bot.name + "charge to enemy flag")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
2. [3] if (our flag captured && at midsection)
    Charge closest side edges
"""  
def attack_rule_2(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured and knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.nearestSideEdge(bot)
        commander.issue(orders.Charge, bot, loc,description = "Attacker" + bot.name + "charge to nearest side edge")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
3. [3] if (our flag captured && not at midsection)
    Charge at midsection
"""
def attack_rule_3(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured and not knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.getMidsection(bot)
        commander.issue(orders.Attack, bot, loc,description = "Attacker" + bot.name + "move to mid section")
       # knowledgeBase.updateStatistics(things)
        return True
    return False    
"""
4. [3] if (our flag captured && not at midsection)
    Charge (atclosest side edges)
"""
def attack_rule_4(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured and not knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.nearestSideEdge(bot)
        commander.issue(orders.Charge, bot, loc,description = "Attacker" + bot.name + "charge to nearest side edge")
       # knowledgeBase.updateStatistics(things)
        return True
    return False


"""
5. [2] if (flag picked up by enemy)
    Charge towards enemyCarrier position.
"""
def attack_rule_5(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured):
        loc = knowledgeBase.predictPosition(commander.game.team.flag.carrier)
        commander.issue(orders.Charge, bot, loc,description = "Attacker" + bot.name + "charge to enemy carrier")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
6. [2] if (our flag is not picked up)
    Charge to enemy flag
"""
def attack_rule_6(bot,commander,knowledgeBase):
    if( not knowledgeBase.ourFlagCaptured):
        loc = knowledgeBase.enemyBase
        print "attack rule 6: ", loc
        commander.issue(orders.Charge, bot, loc,description = "Attacker" + bot.name + "charge to enemy base")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
7. [0] if (our flag is in base && not in area near the midsection)
    Move (to the midsection)
"""
def attack_rule_7(bot,commander,knowledgeBase):
    if(knowledgeBase.flagInBase and not knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.getMidsection(bot)
        commander.issue(orders.Attack, bot, loc,description = "Attacker" + bot.name + "moving towards midsection")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
8. [0] if ( I'm closest to our flag carrier)
    Move (To our flag carrier) 
"""
def attack_rule_8(bot,commander,knowledgeBase):
    ourFlagCarrierPos = knowledgeBase.teamNearestFriend(bot).position
    if(  ourFlagCarrierPos == commander.game.enemyTeam.flag.position):
        commander.issue(orders.Attack, bot, ourFlagCarrierPos,description = "Attacker" + bot.name + "moving towards our flag carrier")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
9. [0] if ( I'm closest to our flag carrier)
    Charge (To our flag carrier) 
"""
def attack_rule_9(bot,commander,knowledgeBase):
    ourFlagCarrierPos = knowledgeBase.teamNearestFriend(bot).position
    if(  ourFlagCarrierPos == commander.game.enemyTeam.flag.position):
        commander.issue(orders.Charge, bot, ourFlagCarrierPos,description = "Attacker" + bot.name + "Charging towards our flag carrier")
       # knowledgeBase.updateStatistics(things)
        return True
    return False  


""" 
10.[0] if (we have their flag)
    Attack (towards our carrier along a short flanking path) #Try to intercept enemy flankers.
"""
def attack_rule_10(bot,commander,knowledgeBase):
    if(  knowledgeBase.theirFlagCaptured ):
        ourFlagCarrierPos = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createShortFlankingPath(bot.position,ourFlagCarrierPos)
        commander.issue(orders.Attack, bot, path,description = "Attacker" + bot.name + "trying to intercept flanking bots via short route")
       # knowledgeBase.updateStatistics(things)
        return True
    return False  


"""
11.[0] if (we have their flag)
    Attack (towards our carrier along a long flanking path) #Try to intercept enemy flankers.
"""
def attack_rule_11(bot,commander,knowledgeBase):
    if(  knowledgeBase.theirFlagCaptured ):
        ourFlagCarrierPos = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createLongFlankingPath(bot.position,ourFlagCarrierPos)
        commander.issue(orders.Attack, bot, path,description = "Attacker" + bot.name + "trying to intercept flanking bots via long route")
       # knowledgeBase.updateStatistics(things)
        return True
    return False  

"""
12.[0] if (no flags are captured)
    Attack ( flanking via short route towards enemy flag)
"""
def attack_rule_12(bot,commander,knowledgeBase):
    if( not knowledgeBase.ourFlagCaptured and not knowledgeBase.theirFlagCaptured):
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Attack, bot, path,description = "Attacker" + bot.name + "Flanking via short route towards enemy flag")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
13.[0] if (no flags are captured)
    Attack ( flanking via long route towards enemy flag)
"""
def attack_rule_13(bot,commander,knowledgeBase):
    if( not knowledgeBase.ourFlagCaptured and not knowledgeBase.theirFlagCaptured):
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Attack, bot, path,description = "Attacker" + bot.name + "Flanking via long route towards enemy flag")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
14.[0] if (we have their flag && i'm not the closest to our carrier)
    Attack (towards our carrier)
"""
def attack_rule_14(bot,commander,knowledgeBase):
    ourFlagCarrierPos = knowledgeBase.teamNearestFriend(bot).position
    if(  knowledgeBase.theirFlagCaptured and not(ourFlagCarrierPos == commander.game.enemyTeam.flag.position)):
        commander.issue(orders.Attack, bot, commander.game.enemyTeam.flag.position,description = "Attacker" + bot.name + "Attacking towards our flag carrier")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
15.[0] if (True)
    Attack (move to nearest friend) # General "Stick together" rule.
"""
def attack_rule_15(bot,commander,knowledgeBase):
    if( True ):
        nearestFriend = knowledgeBase.teamNearestFriend(bot).position
        commander.issue(orders.Attack, bot, nearestFriend,description = "Attacker" + bot.name + "Moving towards nearsest teammate")
       # knowledgeBase.updateStatistics(things)
        return True
    return False
	
"""
	The default attacker rule.
"""
def default_attacker_rule(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured and knowledgeBase.atMidsection(bot)):
        commander.issue(orders.Charge, bot, knowledgeBase.enemyBase,description = "Attacker" + bot.name + "charge to enemy flag")
    else:
        commander.issue(orders.Charge, bot, knowledgeBase.enemyBase,description = "Attacker" + bot.name + "charge to enemy base")
    return True
