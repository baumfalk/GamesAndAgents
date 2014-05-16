"""A set of example Commanders with simple AI.
"""

import random
import os

from api import gameinfo
from api.commander import Commander
from api import orders
from api.vector2 import Vector2
import jsonpickle
import sys

def contains(area, position):
    start, finish = area
    return position.x >= start.x and position.y >= start.y and position.x <= finish.x and position.y <= finish.y

    
#
# RULES
# todo: maybe put this in different file
#   
 
# meta roles rules  
def onlyAttackers(numberOfPersons):
    return ["attacker" for x in range(numberOfPersons)]
    
def onlyDefenders(numberOfPersons):
    return ["defender" for x in range(numberOfPersons)]
    
def onlyCatchers(numberOfPersons):
    print numberOfPersons
    return ["catchers" for x in range(numberOfPersons)] 

# meta switch rules 
def neverSwitch(statistics):
    return False
    
# rules for the different roles 
#todo: put all these arguments in a separate object
def attack(listFlagLocations,listFlagReturnLocations, listVisibleEnemies,randomFreePosition, hasFlag):
    # no one to attack: explore
    if len(listVisibleEnemies) == 0:
        return (orders.Charge,randomFreePosition, "Attacker is exploring!")
    else: # attack a random enemy in sight
        return (orders.Charge, random.choice(listVisibleEnemies),"Attacker is attacking random enemy")

def defend(listFlagLocations,listFlagReturnLocations, listVisibleEnemies,randomFreePosition, hasFlag):
    # no one to attack: return to flag
    if len(listVisibleEnemies) == 0:
        return (orders.Defend,listFlagLocations[0], "Defender is returning to flag!")
    else: # attack a random enemy in sight
        return (orders.Attack, random.choice(listVisibleEnemies),"Defender is attacking random enemy")  

def gotoflag(listFlagLocations,listFlagReturnLocations, listVisibleEnemies,randomFreePosition, hasFlag):
    # no one to attack: return to flag
    if len(listVisibleEnemies) == 0:
        if hasFlag: # we have the flag, return to base
            return (orders.Charge,listFlagLocations[0], "Catcher returning flag!")
        else: #search the flag
            return (orders.Charge,listFlagLocations[1], "Catcher going to flag flag!")
    else: # attack a random enemy in sight
        return (orders.Attack, random.choice(listVisibleEnemies),"Catcher is attacking random enemy")   

class Rule(object):
    def __init__(self, func):
        self.func = func
        self.weight = 1.0
        self.index = -1

class DynamicScriptingClass:
    """Generic Dynamic Scripting Class"""
    def __init__(self, rulebase):
          
        self.rulebase =  rulebase
        self.rulecount = len(rulebase)
        for i in range(0, self.rulecount):
                    self.rulebase[i].index = i
                    thismodule = sys.modules[__name__]
                    # If a function with the string name exists in the module then store it
                    # in the variable, we do this because the function names
                    # are stored as strings in the rulebase
                    if hasattr(thismodule, str(rulebase[i].func)):
                        self.rulebase[i].func = getattr(sys.modules[__name__],str(rulebase[i].func))

class DynamicScriptingInstance:
    """Instance using a subset of rules from the generic dynamic scripting class"""
    def __init__(self, dsclass):
        self.rules = []
        self.rules_active = []
        self.scriptsize = 0
        self.dsclass = dsclass;

    def insertInScript( self, rule ):
        if rule in self.rules:
            return False
        self.rules.append( rule )
        return True

    def generateScript( self, scriptsize ) :
        maxtries = 8

        self.scriptsize = scriptsize
        self.rules = []

        sumweights = 0
        for i in range(0, self.dsclass.rulecount):
            sumweights += self.dsclass.rulebase[i].weight
            self.rules_active.append( False )

        for i in range(0, scriptsize):
            num_tries = 0
            lineadded = False

            while num_tries < maxtries and not lineadded:
                j = 0
                sum = 0
                selected = False
                fraction = random.uniform(0.0, sumweights)

                while not selected:
                    sum += self.dsclass.rulebase[j].weight
                    if sum > fraction:
                        selected = True
                    else:
                        j += 1
                lineadded = self.insertInScript( self.dsclass.rulebase[j] )
                num_tries += 1

    def calculateAdjustment( self, fitness ):
        return fitness

    def distributeRemainder( self, remainder):
        for i in range(0, self.dsclass.rulecount):
            self.dsclass.rulebase[i].weight += remainder / self.dsclass.rulecount

    def adjustWeights( self, fitness ):
        active = 0
        for i in range(0, self.scriptsize):
            if self.rules_active[i]:
                active += 1

        if active <= 0 or active >= self.dsclass.rulecount:
            return

        nonactive = self.dsclass.rulecount - active
        adjustment = self.calculateAdjustment( fitness )
        compensation = -active * adjustment / nonactive
        remainder = 0

        #minweight is a minimum weight so all rules always have a chance of getting selected
        minweight = 0.1
        maxweight = 10.0

        for i in range(0, self.dsclass.rulecount):
            if self.rules_active[i]:
                self.dsclass.rulebase[i].weight += adjustment
            else:
                self.dsclass.rulebase[i].weight += compensation
            if self.dsclass.rulebase[i].weight < minweight:
                remainder += self.dsclass.rulebase[i].weight - minweight
                self.dsclass.rulebase[i].weight = minweight
            elif self.dsclass.rulebase[i].weight > maxweight:
                remainder += self.dsclass.rulebase[i].weight - maxweight
                self.dsclass.rulebase[i].weight = maxweight
        self.distributeRemainder( remainder )
    
    """
    run a certain rule
    """
    def runRule(self,index, parameters):
        rule_index = self.rules[index].index
        self.rules_active[rule_index] = True

        return self.rules[index].func(*parameters)
    
    """
    Still need some tweaking w.r.t. parameters and such...
    """
    def runDynamicScript( self ):
        for i in range(0, self.scriptsize):
            if self.rules[i].func(self, "test %d" % (i)):
                rule_index = self.rules[i].index
                self.rules_active[ rule_index ] = True
                return # should we return here?

class DynamicCommander(Commander):
    """
    A very dynamic and flexible commander ifyouknowwhatimean
    """
    def initialize(self):
        self.verbose = True
        self.statistics = {"numberOfKills":0}
        #todo: make this more generic,
        # i.e. allow for an arbitrary number of roles
        self.loadMetaRules()
        self.loadAttackerRules()
        self.loadDefenderRules()
        self.loadCatcherRules()
        
        self.distributeRoles()
        self.initializeRoles()

    def loadMetaRules(self):
        self.log.info("Loading the meta role rules")
        conn = open(sys.path[0]+"/dynamicscripting/meta_roles.txt",'r')
        self.metaRoleRuleBase = jsonpickle.decode(conn.read())
        conn.close()
        
        self.log.info("Loading the meta switch rules")
        conn = open(sys.path[0]+"/dynamicscripting/meta_switch.txt",'r')
        self.metaSwitchRuleBase = jsonpickle.decode(conn.read())
        conn.close()
    
    def loadAttackerRules(self):
        self.log.info("Loading the attacker rules")
        conn = open(sys.path[0]+"/dynamicscripting/attacker.txt",'r')
        self.attackerRulebase = jsonpickle.decode(conn.read())
        conn.close()    
        
    def loadDefenderRules(self):
        self.log.info("Loading the defender rules")
        conn = open(sys.path[0]+"/dynamicscripting/defender.txt",'r')
        self.defenderRulebase = jsonpickle.decode(conn.read())
        conn.close()        

    def loadCatcherRules(self):
        self.log.info("Loading the catcher rules")
        conn = open(sys.path[0]+"/dynamicscripting/catcher.txt",'r')
        self.catcherRulebase = jsonpickle.decode(conn.read())
        conn.close()
    
    def distributeRoles(self):
        self.log.info("Distributing the roles")
        number_bots = len(self.game.team.members)
        
        self.metaRoleScript =  DynamicScriptingInstance(DynamicScriptingClass(self.metaRoleRuleBase))
        self.metaRoleScript.generateScript(1)
        
        self.metaSwitchScript = DynamicScriptingInstance(DynamicScriptingClass(self.metaSwitchRuleBase))
        self.metaSwitchScript.generateScript(1)
        
        #generate a rolelist
        args = [number_bots]
        roleList = self.metaRoleScript.runRule(0,args)
        self.log.info("Rolelist: "+ str(roleList))
        #assign each bot a role
        for botIndex in range(number_bots):
            self.game.team.members[botIndex].role = roleList[botIndex]
            
    def initializeRoles(self):
        self.log.info("Initializing roles")
        for bot in self.game.team.members:
            
            if(bot.role == "attacker"):
                self.log.info("Generating attacker script")
                bot.script = DynamicScriptingInstance(DynamicScriptingClass(self.attackerRulebase))
                bot.script.generateScript(1)
            elif(bot.role == "defender"):
                self.log.info("Generating defender script")
                bot.script = DynamicScriptingInstance(DynamicScriptingClass(self.defenderRulebase))
                bot.script.generateScript(1)
            elif(bot.role == "catcher"):
                self.log.info("Generating catcher script")
                bot.script = DynamicScriptingInstance(DynamicScriptingClass(self.catcherRulebase))
                bot.script.generateScript(1)
            else: #backup: also attacker 
                bot.script = DynamicScriptingInstance(DynamicScriptingClass(self.attackerRulebase))
                bot.script.generateScript(1)

    def tick(self):
        """Process all the bots that are done with their orders and available for taking orders."""
        self.log.info("Tick!")
        # should the commander issue a new strategy?
        # TODO:
        # 1. make distributeRoles take the current distribution into account
        # 2. Let initialize take good performing scripts for roles into account
        if self.metaSwitchScript.runRule(0,[self.statistics]):
            self.log.info("Switching tactics")
            distributeRoles()
            initializeRoles()
        
        #load information
        our_flag = self.game.team.flag.position
        their_flag = self.game.enemyTeam.flag.position
        listFlagLocations = [our_flag,their_flag]
        our_flag_location = self.game.team.flagScoreLocation
        their_flag_location = self.game.team.flagScoreLocation
        listFlagReturnLocations = [our_flag_location,their_flag_location]
        # give the bots new commands
        self.log.info("Giving orders to all the bots")
        for bot in self.game.bots_alive:
            listVisibleEnemies = [b.position for b in bot.visibleEnemies]
            randomFreePosition = self.level.findRandomFreePositionInBox(self.level.area)
            hasFlag = bot.flag
            
            cmd, target, desc = bot.script.runRule(0,[listFlagLocations,listFlagReturnLocations, listVisibleEnemies,randomFreePosition, hasFlag])
          
            if target:
                self.issue(cmd, bot, target,description = desc)