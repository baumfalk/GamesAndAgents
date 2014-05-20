

#General attack rules.

"""
1. [3] if (our flag captured && at midsection)
    Charge enemy base
"""
def attack_rule_1(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured and knowledgeBase.atMidsection(bot)):
        commander.issue(orders.Charge, bot, knowledgeBase.enemyBase,description = "Attacker" + bot.id + "charge to enemy flag")
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
        commander.issue(orders.Charge, bot, loc,description = "Attacker" + bot.id + "charge to nearest side edge")
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
        commander.issue(orders.Attack, bot, loc,description = "Attacker" + bot.id + "move to mid section")
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
        commander.issue(orders.Charge, bot, loc,description = "Attacker" + bot.id + "charge to nearest side edge")
       # knowledgeBase.updateStatistics(things)
        return True
    return False


"""
5. [2] if (flag picked up by enemy)
    Charge towards enemyCarrier position.
"""
def attack_rule_5(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured):
        loc = knowledgeBase.enemyCarrierPos
        commander.issue(orders.Charge, bot, loc,description = "Attacker" + bot.id + "charge to enemy carrier")
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
        commander.issue(orders.Charge, bot, loc,description = "Attacker" + bot.id + "charge to enemy base")
       # knowledgeBase.updateStatistics(things)
        return True
    return False


"""
This should be a meta rule

7. [1] if (flag visible && no enemies around)
    Request to become a catcher
"""

"""
8. [0] if (our flag is in base && not in area near the midsection)
    Move (to the midsection)
"""
def attack_rule_7(bot,commander,knowledgeBase):
    if(knowledgeBase.flagInBase and not knowledgeBase.atMidsection(bot)):
        loc = knowledgeBase.getMidsection(bot)
        commander.issue(orders.Attack, bot, loc,description = "Attacker" + bot.id + "moving towards midsection")
       # knowledgeBase.updateStatistics(things)
        return True
    return False

"""
Also a Meta ( or possibly defend Rule)

9. [0] if (at midesction and no enemies around)
    find cover( I dont know if it is possible) and Defend  
"""
            
""" 
TODO: Make a helper isAround(bot) function to check if friendly bots are around.

10.[0] if (midesction and no enemies around)
    Charge closest side edge
11.[0] if (midesction and no enemies around)
    Move to our base
12.[0] if (midesction and no enemies around)
    Charge to enemy base
"""
