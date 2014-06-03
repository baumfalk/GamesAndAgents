from api import orders

def mixedAttackers(numberOfPersons):
    extraAttackers = numberOfPersons % 3 
    attackerList = ["attacker" for x in range(numberOfPersons/3 + extraAttackers)]
    defenderList = ["defender" for x in range(numberOfPersons/3)]
    catcherList = ["catcher" for x in range(numberOfPersons/3)]
    return attackerList + defenderList + catcherList

def onlyAttackers(numberOfPersons):
    return ["attacker" for x in range(numberOfPersons)]
    
def onlyDefenders(numberOfPersons):
    return ["defender" for x in range(numberOfPersons)]
    
def onlyCatchers(numberOfPersons):
    print numberOfPersons
    return ["catcher" for x in range(numberOfPersons)] 

# meta switch rules 
def neverSwitch(statistics):
    return False
    
# rules for the different roles 

#rules for attacker

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
        loc = knowledgeBase.enemyCarrierPos
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


 
#rules for defender
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
        differenceVec.normalize()
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
# Attack rule 1 and 6
def default_attacker_rule(bot,commander,knowledgeBase):
    if(knowledgeBase.ourFlagCaptured and knowledgeBase.atMidsection(bot)):
        commander.issue(orders.Charge, bot, knowledgeBase.enemyBase,description = "Attacker" + bot.name + "charge to enemy flag")
    else:
        commander.issue(orders.Charge, bot, knowledgeBase.enemyBase,description = "Attacker" + bot.name + "charge to enemy base")
    return True
    
def default_defender_rule(bot,commander,knowledgeBase):
    if knowledgeBase.ourFlagCaptured:
        commander.issue(orders.Charge,bot,commander.game.team.flag.position, description = "Catcher "+ bot.name + " Charge our socre location")
    elif knowledgeBase.atMidsection(bot):
        commander.issue(orders.Charge,bot,commander.game.team.flag.position, description = "Catcher "+ bot.name + " Charge our socre location")
    else:
        commander.issue(orders.Charge,bot,knowledgeBase.getMidsection(bot), description = "Catcher "+ bot.name + " Charge our socre location")
    return True
    
def default_catcher_rule(bot,commander,knowledgeBase):
    if not bot.flag:
        target = commander.game.enemyTeam.flag.position
    else:
        target = commander.game.team.flagScoreLocation
    commander.issue(orders.Charge,bot,target, description = "Catcher "+ bot.name + " Charge directly to flag")
    return True
