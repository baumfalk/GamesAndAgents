from api import orders

#rules for catcher        
def gotoflag(listFlagLocations,listFlagReturnLocations, listVisibleEnemies,randomFreePosition, hasFlag):
    # no one to attack: return to flag
    if len(listVisibleEnemies) == 0:
        if hasFlag: # we have the flag, return to base
            return (orders.Charge,listFlagLocations[0], "Catcher returning flag!")
        else: #search the flag
            return (orders.Charge,listFlagLocations[1], "Catcher going to flag flag!")
    else: # attack a random enemy in sight
        return (orders.Attack, random.choice(listVisibleEnemies),"Catcher is attacking random enemy")
"""
1. [1] if (has flag)
	Move (closest edge map and approach scoring point following the edge)
"""        
def capture_rule1(bot,commander,knowledgeBase):
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Move,bot,path, description = "Catcher "+ bot.name + " Move to scoring point from closest side")
        return True
    return False
	
"""
2. [1] if (has flag)
	Charge (closest edge map and approach base sides following the edge)
"""
def capture_rule2(bot,commander,knowledgeBase):
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,path, description = "Catcher "+ bot.name + " Charge to scoring point from closest side")
        return True
    return False
	
"""
3. [1] if (has flag)
	Move (shortest path to base)
"""
def capture_rule3(bot,commander,knowledgeBase):
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        commander.issue(orders.Move,bot,target, description = "Catcher "+ bot.name + " Move directly to scoring point")
        return True
    return False
	
"""
4. [1] if (has flag)
	Charge (shortest path to base)
"""
def capture_rule4(bot,commander,knowledgeBase):
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge directly to scoring point")
        return True
    return False
	
"""
5. [1] if (has flag)
	Move (furthest edge map and approach base sides following the edge)
"""
def capture_rule5(bot,commander,knowledgeBase):
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Move,bot,path, description = "Catcher "+ bot.name + " Move to scoring point from furthest side")
        return True
    return False
	
"""
6. [1] if (has flag)
	Charge (furthest edge map and approach base sides following the edge)
"""
def capture_rule6(bot,commander,knowledgeBase):
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,path, description = "Catcher "+ bot.name + " Charge to scoring point from furthest side")
        return True
    return False
	
""" 
7. [0] if (doesn't have flag && enemy flag isn't captured)
	Move (closest edge map and approach flag following the side edge)
"""
def capture_rule7(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Move,bot,path, description = "Catcher "+ bot.name + " Move to flag from closest side")
        return True
    return False
	
"""
8. [0] if (doesn't have flag && enemy flag isn't captured)
	Charge (closest edge map and approach flag following the side edge)
"""
def capture_rule8(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,path, description = "Catcher "+ bot.name + "Charge to flag from closest side")
        return True
    return False
	
"""
9. [0] if (doesn't have flag && flag isn't captured)
	Move (closest path to flag)
"""
def capture_rule9(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        commander.issue(orders.Move,bot,target, description = "Catcher "+ bot.name + " Move directly to flag")
        return True
    return False

"""
10. [0] if (doesn't have flag && enemy flag isn't captured)
	 Charge (closest path to flag)
"""
def capture_rule10(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge directly to flag")
        return True
    return False
	
"""
11. [0] if (doesn't have flag && enemy flag isn't captured)
	 Move (furthest edge map and approach flag following the side edge)
"""
def capture_rule11(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Move,bot,path, description = "Catcher "+ bot.name + " Move to flag from furthest side")
        return True
    return False
	
"""
12.[0] if (doesn't have flag && enemy flag isn't captured)
	Charge (furthest edge map and approach flag following the side edge)
"""
def capture_rule12(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,path, description = "Catcher "+ bot.name + " Charge to flag from furthest side")
        return True
    return False
	
"""
13. [0] if (doesn't have flag && enemy flag is captured)
	 Charge (closest edge map and approach flag spawning point following the side edge)
"""
def capture_rule13(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier != None:
        target = commander.game.enemyTeam.flagSpawnLocation
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge to flag spawning point from closest side")
        return True
    return False
	
"""
14. [0] if (doesn't have flag && enemy flag is captured)
	 Charge (furthest edge map and approach flag spawning point following the side edge)
"""
def capture_rule14(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier != None:
        target = commander.game.enemyTeam.flagSpawnLocation
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge to flag spawning point from furthest side")
        return True
    return False
	
"""
15. [0] if (doesn't have flag && our flag is captured)
	 Charge (enemy scoring point)
"""
def capture_rule15(bot,commander,knowledgeBase):
    if not bot.flag and knowledgeBase.ourFlagCaptured:
        target = commander.game.enemyTeam.flagScoreLocation
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge enemy's scoring point")
        return True
    return False
	
"""
	The default catcher rule.
"""
def default_catcher_rule(bot,commander,knowledgeBase):
    if not bot.flag:
        target = commander.game.enemyTeam.flag.position
    else:
        target = commander.game.team.flagScoreLocation
    commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge directly to flag")
    return True