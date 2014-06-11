from api import orders

#rules for catcher        
	   
def capture_rule1(bot,commander,knowledgeBase):
    """ 1. [1] if (has flag) Move (closest edge map and approach scoring point following the edge) """ 
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Move,bot,path, description = "Catcher "+ bot.name + " Move to scoring point from closest side")
        return True
    return False
	

def capture_rule2(bot,commander,knowledgeBase):
    """ 2. [1] if (has flag) Charge (closest edge map and approach base sides following the edge) """
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,path, description = "Catcher "+ bot.name + " Charge to scoring point from closest side")
        return True
    return False
	

def capture_rule3(bot,commander,knowledgeBase):
    """ 3. [1] if (has flag) Move (shortest path to base) """
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        commander.issue(orders.Move,bot,target, description = "Catcher "+ bot.name + " Move directly to scoring point")
        return True
    return False
	

def capture_rule4(bot,commander,knowledgeBase):
    """ 4. [1] if (has flag) Charge (shortest path to base) """
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge directly to scoring point")
        return True
    return False
	

def capture_rule5(bot,commander,knowledgeBase):
    """ 5. [1] if (has flag) Move (furthest edge map and approach base sides following the edge) """
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Move,bot,path, description = "Catcher "+ bot.name + " Move to scoring point from furthest side")
        return True
    return False
	

def capture_rule6(bot,commander,knowledgeBase):
    """ 6. [1] if (has flag) Charge (furthest edge map and approach base sides following the edge) """
    if bot.flag:
        target = commander.game.team.flagScoreLocation
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,path, description = "Catcher "+ bot.name + " Charge to scoring point from furthest side")
        return True
    return False
	

def capture_rule7(bot,commander,knowledgeBase):
    """ 7. [0] if (doesn't have flag && enemy flag isn't captured) Move (closest edge map and approach flag following the side edge) """
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Move,bot,path, description = "Catcher "+ bot.name + " Move to flag from closest side")
        return True
    return False
	

def capture_rule8(bot,commander,knowledgeBase):
    """ 8. [0] if (doesn't have flag && enemy flag isn't captured) Charge (closest edge map and approach flag following the side edge) """ 
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,path, description = "Catcher "+ bot.name + "Charge to flag from closest side")
        return True
    return False
	

def capture_rule9(bot,commander,knowledgeBase):
    """ 9. [0] if (doesn't have flag && flag isn't captured) Move (closest path to flag) """
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        commander.issue(orders.Move,bot,target, description = "Catcher "+ bot.name + " Move directly to flag")
        return True
    return False


def capture_rule10(bot,commander,knowledgeBase):
    """ 10. [0] if (doesn't have flag && enemy flag isn't captured) Charge (closest path to flag) """
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge directly to flag")
        return True
    return False
	

def capture_rule11(bot,commander,knowledgeBase):
    """ 11. [0] if (doesn't have flag && enemy flag isn't captured) Move (furthest edge map and approach flag following the side edge) """
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Move,bot,path, description = "Catcher "+ bot.name + " Move to flag from furthest side")
        return True
    return False
	

def capture_rule12(bot,commander,knowledgeBase):
    """ 12.[0] if (doesn't have flag && enemy flag isn't captured) Charge (furthest edge map and approach flag following the side edge) """
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = commander.game.enemyTeam.flag.position
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,path, description = "Catcher "+ bot.name + " Charge to flag from furthest side")
        return True
    return False
	

def capture_rule13(bot,commander,knowledgeBase):
    """ 13. [0] if (doesn't have flag && enemy flag is captured) Charge (closest edge map and approach flag spawning point following the side edge) """
    if not bot.flag and commander.game.enemyTeam.flag.carrier != None:
        target = commander.game.enemyTeam.flagSpawnLocation
        path = knowledgeBase.createShortFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge to flag spawning point from closest side")
        return True
    return False
	

def capture_rule14(bot,commander,knowledgeBase):
    """ 14. [0] if (doesn't have flag && enemy flag is captured) Charge (furthest edge map and approach flag spawning point following the side edge) """
    if not bot.flag and commander.game.enemyTeam.flag.carrier != None:
        target = commander.game.enemyTeam.flagSpawnLocation
        path = knowledgeBase.createLongFlankingPath(bot.position,target)
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge to flag spawning point from furthest side")
        return True
    return False
	

def capture_rule15(bot,commander,knowledgeBase):
    """ 15. [0] if (doesn't have flag && our flag is captured) Charge (enemy scoring point) """
    if not bot.flag and commander.game.team.flag.carrier != None:
        target = commander.game.enemyTeam.flagScoreLocation
        commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge enemy's scoring point")
        return True
    return False
	

def default_catcher_rule(bot,commander,knowledgeBase):
    """ The default catcher rule. """
    if not bot.flag:
        target = commander.game.enemyTeam.flag.position
    else:
        target = commander.game.team.flagScoreLocation
    commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge directly to flag")
    return True