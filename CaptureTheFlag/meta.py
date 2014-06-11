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