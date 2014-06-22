from api import orders

# Possible team configurations
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
    return ["catcher" for x in range(numberOfPersons)]

def singleCatcher(numberOfPersons):
    remainder = (numberOfPersons - 1) % 2
    attackerList = ["attacker" for x in range((numberOfPersons - 1) / 2 + remainder)]
    defenderList = ["defender" for x in range((numberOfPersons - 1) / 2)]
    catcherList = ["catcher"]
    return attackerList + defenderList + catcherList

def singleDefender(numberOfPersons):
    remainder = (numberOfPersons - 1) % 2
    attackerList = ["attacker" for x in range((numberOfPersons - 1) / 2 + remainder)]
    defenderList = ["defender"]
    catcherList = ["catcher" for x in range((numberOfPersons - 1) / 2)]
    return attackerList + defenderList + catcherList

def focusAttack(numberOfPersons):
    attackerList = ["attacker" for x in range(numberOfPersons - (numberOfPersons / 4) * 2)]
    defenderList = ["defender" for x in range(numberOfPersons / 4)]
    catcherList = ["catcher" for x in range(numberOfPersons / 4)]
    return attackerList + defenderList + catcherList

def focusDefence(numberOfPersons):
    attackerList = ["attacker" for x in range(numberOfPersons / 4)]
    defenderList = ["defender" for x in range(numberOfPersons - (numberOfPersons / 4) * 2)]
    catcherList = ["catcher" for x in range(numberOfPersons / 4)]
    return attackerList + defenderList + catcherList

def focusCatch(numberOfPersons):
    attackerList = ["attacker" for x in range(numberOfPersons / 4)]
    defenderList = ["defender" for x in range(numberOfPersons / 4)]
    catcherList = ["catcher" for x in range(numberOfPersons - (numberOfPersons / 4) * 2)]
    return attackerList + defenderList + catcherList

# meta switch rules 
def metaNeverSwitch(numberOfPersons,statistics):
    return None

def metaScoredDefensive(numberOfPersons,statistics):
    if statistics.weCaptured:
        return focusDefence(numberOfPersons)
    return None

def metaScoredOffensive(numberOfPersons,statistics):
    if statistics.weCaptured:
        return focusAttack(numberOfPersons)
    return None

def metaScoredCatching(numberOfPersons,statistics):
    if statistics.weCaptured:
        return focusCatch(numberOfPersons)
    return None

def metaScoredMixed(numberOfPersons,statistics):
    if statistics.weCaptured:
        return mixedAttackers(numberOfPersons)
    return None

def metaAheadDefensive(numberOfPersons,statistics):
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return focusDefence(numberOfPersons)
    return None

def metaAheadOffensive(numberOfPersons,statistics):
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return focusAttack(numberOfPersons)
    return None

def metaAheadCatching(numberOfPersons,statistics):
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return focusCatch(numberOfPersons)
    return None

def metaAheadMixed(numberOfPersons,statistics):
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return mixedAttackers(numberOfPersons)
    return None

def metaAheadSingleCatcher(numberOfPersons,statistics):
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return singleCatcher(numberOfPersons)
    return None

def metaBehindDefensive(numberOfPersons,statistics):
    if statistics.theyCaptured and statistics.theirScore > statistics.ourScore:
        return focusDefence(numberOfPersons)
    return None

def metaBehindOffensive(numberOfPersons,statistics):
    if statistics.theyCaptured and statistics.theirScore > statistics.ourScore:
        return focusAttack(numberOfPersons)
    return None

def metaBehindCatching(numberOfPersons,statistics):
    if statistics.theyCaptured and statistics.theirScore > statistics.ourScore:
        return focusCatch(numberOfPersons)
    return None

def metaBehindMixed(numberOfPersons,statistics):
    if statistics.theyCaptured and statistics.theirScore > statistics.ourScore:
        return mixedAttackers(numberOfPersons)
    return None

def metaSpawnAttackers(numberOfPersons,statistics):
    if statistics.weRespawned:
        return onlyAttackers(numberOfPersons)
    return None

def metaSpawnDefenders(numberOfPersons,statistics):
    if statistics.weRespawned:
        return onlyDefenders(numberOfPersons)
    return None

def metaSpawnCatchers(numberOfPersons,statistics):
    if statistics.weRespawned:
        return onlyCatchers(numberOfPersons)
    return None

def metaEndgameOffensive(numberOfPersons,statistics):
    if statistics.isRemainingTime(60): # 1 minute left
        return focusAttack(numberOfPersons)
    return None

def metaEndgameDefensive(numberOfPersons,statistics):
    if statistics.isRemainingTime(60): # 1 minute left
        return focusDefence(numberOfPersons)
    return None

def metaEndgameCatching(numberOfPersons,statistics):
    if statistics.isRemainingTime(60): # 1 minute left
        return focusCatch(numberOfPersons)
    return None

def metaEndgameMixed(numberOfPersons,statistics):
    if statistics.isRemainingTime(60): # 1 minute left
        return mixedAttackers(numberOfPersons)
    return None

def metaEndgameAllOut(numberOfPersons,statistics):
    if statistics.isRemainingTime(60): # 1 minute left
        return onlyCatchers(numberOfPersons)
    return None

def metaAvengers(numberOfPersons,statistics):
    if statistics.theyKilled:
        return onlyAttackers(numberOfPersons)
    return None

def metaSpawnCampers(numberOfPersons,statistics):
    if statistics.theyRespawned:
        return singleDefender(numberOfPersons)
    return None

def metaIronMan(numberOfPersons,statistics):
    if statistics.weDropped:
        return singleCatcher(numberOfPersons)
    return None

def metaIntercepters(numberOfPersons,statistics):
    if statistics.theyDropped:
        return onlyDefenders(numberOfPersons)
    return None

def metaPussy(numberOfPersons,statistics):
    if (statistics.weCaptured or statistics.theyCaptured) and statistics.ourScore == statistics.theirScore:
        return mixedAttackers(numberOfPersons)
    return None

def metaImpatient(numberOfPersons,statistics):
    if statistics.isCurrentTime(60): # After 1 minute
        return onlyCatchers(numberOfPersons)
    return None
    
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
        target = [commander.game.team.flagScoreLocation,commander.level.findRandomFreePositionInBox(commander.game.team.flagScoreLocation-2.5,commander.game.team.flagScoreLocation+2.5)]
        commander.issue(orders.Move,bot,target, description = "Catcher "+ bot.name + " Move directly to scoring point")
        return True
    return False
	
"""
4. [1] if (has flag)
	Charge (shortest path to base)
"""
def capture_rule4(bot,commander,knowledgeBase):
    if bot.flag:
        target = [commander.game.team.flagScoreLocation,commander.level.findRandomFreePositionInBox(commander.game.team.flagScoreLocation-2.5,commander.game.team.flagScoreLocation+2.5)]
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
        target = [commander.game.enemyTeam.flag.position,commander.level.findRandomFreePositionInBox(commander.game.enemyTeam.flag.position-2.5,commander.game.enemyTeam.flag.position+2.5)]
        commander.issue(orders.Move,bot,target, description = "Catcher "+ bot.name + " Move directly to flag")
        return True
    return False

"""
10. [0] if (doesn't have flag && enemy flag isn't captured)
	 Charge (closest path to flag)
"""
def capture_rule10(bot,commander,knowledgeBase):
    if not bot.flag and commander.game.enemyTeam.flag.carrier == None:
        target = [commander.game.enemyTeam.flag.position,commander.level.findRandomFreePositionInBox(commander.game.enemyTeam.flag.position-2.5,commander.game.enemyTeam.flag.position+2.5)]
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
        commander.issue(orders.Defend,bot,commander.game.enemyTeam.flagSpawnLocation,description = "Capper " + bot.name + " occupying enemy flag location")
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
        commander.issue(orders.Defend,bot,commander.game.enemyTeam.flagSpawnLocation,description = "Capper " + bot.name + " occupying enemy flag location")
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
        commander.issue(orders.Defend,bot,commander.game.enemyTeam.flagScoreLocation,description = "Capper " + bot.name + " occupying enemy flag score location")
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
