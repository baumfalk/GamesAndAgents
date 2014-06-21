from api import orders

# Possible team configurations
def mixedAttackers(numberOfPersons):
    extraAttackers = numberOfPersons % 3 
    attackerList = ["attacker" for x in range(numberOfPersons/3 + extraAttackers)]
    defenderList = ["defender" for x in range(numberOfPersons/3)]
    catcherList = ["catcher" for x in range(numberOfPersons/3)]
    return attackerList + defenderList + catcherList
    
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
def meta_rule_1(numberOfPersons,statistics):
    """ 1. Don't switch """
    return None

def meta_rule_2(numberOfPersons,statistics):
    """ 2. if (we captured flag) focus on defenders """
    if statistics.weCaptured:
        return focusDefence(numberOfPersons)
    return None

def meta_rule_3(numberOfPersons,statistics):
    """ 3. if (we captured flag) focus on attackers """
    if statistics.weCaptured:
        return focusAttack(numberOfPersons)
    return None

def meta_rule_4(numberOfPersons,statistics):
    """ 4. if (we captured flag) focus on catchers """
    if statistics.weCaptured:
        return focusCatch(numberOfPersons)
    return None

def meta_rule_5(numberOfPersons,statistics):
    """ 5. if (we captured flag) divide roles evenly """
    if statistics.weCaptured:
        return mixedAttackers(numberOfPersons)
    return None

def meta_rule_6(numberOfPersons,statistics):
    """ 6. if (we're ahead in score) focus on defenders """
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return focusDefence(numberOfPersons)
    return None

def meta_rule_7(numberOfPersons,statistics):
    """ 7. if (we're ahead in score) focus on attackers """
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return focusAttack(numberOfPersons)
    return None

def meta_rule_8(numberOfPersons,statistics):
    """ 8. if (we're ahead in score) focus on catchers """
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return focusCatch(numberOfPersons)
    return None

def meta_rule_9(numberOfPersons,statistics):
    """ 9. if (we're ahead in score) divide roles evenly """
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return mixedAttackers(numberOfPersons)
    return None

def meta_rule_10(numberOfPersons,statistics):
    """ 10. if (we're ahead in score) make only 1 catcher """
    if statistics.weCaptured and statistics.ourScore > statistics.theirScore:
        return singleCatcher(numberOfPersons)
    return None

def meta_rule_11(numberOfPersons,statistics):
    """ 11. if (we're behind in score) focus on defenders """
    if statistics.theyCaptured and statistics.theirScore > statistics.ourScore:
        return focusDefence(numberOfPersons)
    return None

def meta_rule_12(numberOfPersons,statistics):
    """ 12. if (we're behind in score) focus on attackers """
    if statistics.theyCaptured and statistics.theirScore > statistics.ourScore:
        return focusAttack(numberOfPersons)
    return None

def meta_rule_13(numberOfPersons,statistics):
    """ 13. if (we're behind in score) focus on catchers """
    if statistics.theyCaptured and statistics.theirScore > statistics.ourScore:
        return focusCatch(numberOfPersons)
    return None

def meta_rule_14(numberOfPersons,statistics):
    """ 14. if (we're behind in score) divide roles evenly """
    if statistics.theyCaptured and statistics.theirScore > statistics.ourScore:
        return mixedAttackers(numberOfPersons)
    return None

def meta_rule_17(numberOfPersons,statistics):
    """ 17. if (we just spawned) everyone is catcher """
    if statistics.weRespawned:
        return onlyCatchers(numberOfPersons)
    return None

def meta_rule_18(numberOfPersons,statistics):
    """ 18. if (1 minute left) focus on attackers """
    if statistics.isRemainingTime(60): # 1 minute left
        return focusAttack(numberOfPersons)
    return None

def meta_rule_19(numberOfPersons,statistics):
    """ 19. if (1 minute left) focus on defenders """
    if statistics.isRemainingTime(60): # 1 minute left
        return focusDefence(numberOfPersons)
    return None

def meta_rule_20(numberOfPersons,statistics):
    """ 20. if (1 minute left) focus on catchers """
    if statistics.isRemainingTime(60): # 1 minute left
        return focusCatch(numberOfPersons)
    return None

def meta_rule_21(numberOfPersons,statistics):
    """ 21. if (1 minute left) divide roles evenly """
    if statistics.isRemainingTime(60): # 1 minute left
        return mixedAttackers(numberOfPersons)
    return None

def meta_rule_22(numberOfPersons,statistics):
    """ 22. if (1 minute left) everyone is catcher """
    if statistics.isRemainingTime(60): # 1 minute left
        return onlyCatchers(numberOfPersons)
    return None

def meta_rule_24(numberOfPersons,statistics):
    """ 24. Spawn campers! if (they respawned) only one defender """
    if statistics.theyRespawned:
        return singleDefender(numberOfPersons)
    return None

def meta_rule_25(numberOfPersons,statistics):
    """ 25. Iron man! if (we dropped the flag) only one catcher """
    if statistics.weDropped:
        return singleCatcher(numberOfPersons)
    return None

def meta_rule_27(numberOfPersons,statistics):
    """ 27. Pussy! if (scores are equal) divide roles evenly """
    if (statistics.weCaptured or statistics.theyCaptured) and statistics.ourScore == statistics.theirScore:
        return mixedAttackers(numberOfPersons)
    return None

def meta_rule_28(numberOfPersons,statistics):
    """ 28. Impatient! if (1 minute passed) everyone is catcher """
    if statistics.isCurrentTime(60): # After 1 minute
        return onlyCatchers(numberOfPersons)
    return None