"""Everything that is needed for a dynamic scripting AI commander
"""

#TODO:
#1. Evaluation and weight altering
#2. more and better rules
#3. A way to select different rules from the script
#4. Enhance the way the arguments are passed to the rules.
#   For example, it might be useful if we have a custom info object that contains all the info needed
#   for the bot rules.

"""
This bot works as follows

There exists various text files in the folder ./dynamicscripting/. These contain rules, as well as weights for these and an ordering on these rules.
The actual implementation in this rules are in the *Rules.py. Most of the text files describe the rules for various roles
that a bot can have, such as an attacker, a defender etc. There are two special text files, namely meta_roles.txt and meta_switch.txt. These
files list the rules that are used for distributing the various roles to the bots and the rules used for deciding when to switch role distribution.

The code flow is as follows:

1. The commander is created. It loads all the rules from the dynamicscripting folder
2. It distributes the roles to the agents according to its meta role rules.
3. For each bot, a script is generated based on the rule set associated with its role
4. For each tick, the following happens:
5. The meta switch rules determine whether a role switch is necessary and if so, perform this.
6. Each available bot generates a new action, based on its rule set and the information provided by the commander. The commander 'issues' this command
   to the bot (even though the bot generated it himself)
7. Any bot which has the flag becomes a Catcher and is assigned a corresponding script
8. Any bot which has been unavailable for more than 45s is issued a new order.
"""

import random
import os
import math

from api import gameinfo
from api.commander import Commander
from api import orders
from api.vector2 import Vector2
from knowledge import Knowledge
from statistics import Statistics
import sys
import jsonpickle
import attackerRules
import defenderRules
import catcherRules
import metaRules
from dynamicscripting import *

def contains(area, position):
    start, finish = area
    return position.x >= start.x and position.y >= start.y and position.x <= finish.x and position.y <= finish.y

def resetBotStats(bot):
    bot.deaths = 0
    bot.kills = 0
    bot.flag_pickedup = 0
    bot.flag_dropped = 0
    bot.flag_stolen = 0
    bot.flag_captured = 0
    bot.flag_restored = 0

class DynamicCommander(Commander):
    """
    Initializes everything that the commander needs. This includes loading the different rulesets, distributing the roles and generating scripts for the bots.
    """
    def initialize(self):
        self.verbose = True
        self.statistics = Statistics()
        self.statistics.initialize(self)
        self.knowledge = Knowledge()
        self.knowledge.initialize(self)
        
        #todo: make this more generic,
        # i.e. allow for an arbitrary number of roles
        # load all rule bases
        self.loadMetaRules()
        self.loadAttackerRules()
        self.loadDefenderRules()
        self.loadCatcherRules()
        
        # distribute the roles to the bots 
        roleList = self.metaScript.runDynamicScript([len(self.game.team.members),self.statistics])
        if(roleList != None):
            self.distributeRoles(roleList)
        else: #If none of the rules apply, use a mixed team.
            self.distributeRoles(metaRules.mixedAttackers(len(self.game.team.members)))
        # and generate the corresponding scripts
        self.initializeRoles()
        self.initializeBotStats()

    """
    Loads the meta rules with their weights.
    """
    def loadMetaRules(self):
        self.log.info("Loading the meta rules")
        conn = open(sys.path[0]+"/dynamicscripting/meta.txt",'r')
        self.metaRuleBase = jsonpickle.decode(conn.read())
        conn.close()
        
        # Generate an initial meta script
        self.metaScript = DynamicScriptingInstance(DynamicScriptingClass(self.metaRuleBase,"metaRules"))
        self.metaScript.generateScript(3)
        self.metaScript.printScript()
    
    """
    Loads the attacker rules with their weights.
    """
    def loadAttackerRules(self):
        self.log.info("Loading the attacker rules")
        conn = open(sys.path[0]+"/dynamicscripting/attacker.txt",'r')
        self.attackerRulebase = jsonpickle.decode(conn.read())
        conn.close()    
        
    """
    Loads the defender rules with their weights.
    """
    def loadDefenderRules(self):
        self.log.info("Loading the defender rules")
        conn = open(sys.path[0]+"/dynamicscripting/defender.txt",'r')
        self.defenderRulebase = jsonpickle.decode(conn.read())
        conn.close()        

    """
    Loads the catcher rules with their weights.
    """
    def loadCatcherRules(self):
        self.log.info("Loading the catcher rules")
        conn = open(sys.path[0]+"/dynamicscripting/catcher.txt",'r')
        self.catcherRulebase = jsonpickle.decode(conn.read())
        conn.close()
    
    """
    Distributes the roles to the bots according to a given distribution.
    """
    def distributeRoles(self,roleList):
        self.log.info("Distributing the roles")       
        self.log.info("Rolelist: "+ str(roleList))
        #assign each bot a role
        for botIndex in range(len(roleList)):
            self.game.team.members[botIndex].role = roleList[botIndex]
            
    def initializeRoles(self):
        self.log.info("Initializing roles")
		# load the rulebases
        self.dsclassAttacker = DynamicScriptingClass(self.attackerRulebase,"attackerRules")
        self.dsclassDefender = DynamicScriptingClass(self.defenderRulebase,"defenderRules")
        self.dsclassCatcher = DynamicScriptingClass(self.catcherRulebase,"catcherRules")
        i = 1
		#assign each bot a role, depending on its role
        for bot in self.game.team.members:
            bot.id = i
            self.log.info("Bot #" + str(i) + ": Generating " + bot.role + " script")
            if(bot.role == "attacker"):
                bot.script = DynamicScriptingInstance(self.dsclassAttacker,botRole = bot.role,botNumber = i)
                bot.script.generateScript(4)
                # add default rule
                bot.script.insertInScript(Rule(attackerRules.default_attacker_rule))
            elif(bot.role == "defender"):
                bot.script = DynamicScriptingInstance(self.dsclassDefender,botRole = bot.role,botNumber = i)
                bot.script.generateScript(4)
                bot.script.insertInScript(Rule(defenderRules.default_defender_rule))
            else: #if(bot.role == "catcher"): #backup
                bot.script = DynamicScriptingInstance(self.dsclassCatcher,botRole = bot.role,botNumber = i)
                bot.script.generateScript(4)
                #for i in bot.script.rules: #to check if there are different type of rules at base
                #    print(i.rule_type)
                bot.script.insertInScript(Rule(catcherRules.default_catcher_rule))
            bot.script.printScript()
            self.log.info("")
            i += 1

    """
    Initialises the statistics for the bots.
    """
    def initializeBotStats(self):
    
        self.timeSinceLastCommand = {} # used to detect bots that are stuck
    
        for bot in self.game.team.members:
            resetBotStats(bot)
            self.timeSinceLastCommand[bot.id] = 0

    """
    Updates the weights for all bots and the meta script in accordance
    with the procedure given in Spronck's paper.
    """
    def updateWeights(self):
        self.log.info("Updating weights!")
        self.metaScript.adjustWeights(self.metaScript.calculateTeamFitness(self.knowledge),self)
        for bot in self.game.team.members:
            fitness = bot.script.calculateAgentFitness(bot, self.knowledge)
            self.log.info("Bot #" + str(bot.id) + "[" + bot.role + "] fitness:" + str(fitness))
           
            bot.script.adjustWeights(fitness,self)

    """
    Save all the weights back to the files.
    """
    def saveWeights(self):
        self.saveWeightsRulebase(self.attackerRulebase,"attacker")
        self.saveWeightsRulebase(self.defenderRulebase,"defender")
        self.saveWeightsRulebase(self.catcherRulebase,"catcher")
        self.saveWeightsRulebase(self.metaRuleBase,"meta")
    
	"""
	save a certain rulebase
	"""
    def saveWeightsRulebase(self,rulebase,name):
        conn = open(sys.path[0] + "/dynamicscripting/" + name + ".txt",'w')
        funcBackup = []
        # Replace function by function names
        for rule in rulebase:
            funcBackup.append(rule.func)
            rule.func = rule.func.__name__
        rulebaseEncoded = jsonpickle.encode(rulebase)
        conn.write(rulebaseEncoded)
        conn.close()
        
        # Put them back.
        for i in range(len(rulebase)):
            rulebase[i].func = funcBackup[i]

    """
    Update the statistics for the bots. 
	Statistics are used to calculate bot fitness
    """
    def updateBotStats(self):
        for event in self.game.match.combatEvents:
            if event.type == event.TYPE_FLAG_RESTORED:
                if event.subject.team == self.game.team:
                    for bot in self.game.team.members:
                        bot.flag_restored += 1
                continue
            elif event.type == event.TYPE_FLAG_CAPTURED:
                if event.subject.team == self.game.team:
                    for bot in self.game.team.members:
                        bot.flag_stolen += 1
                continue

            if event.instigator == None:
                continue
            if event.instigator.team == self.game.team:
                if event.type == event.TYPE_KILLED:
                    event.instigator.kills += 1
                elif event.type == event.TYPE_FLAG_PICKEDUP:
                    event.instigator.flag_pickedup += 1
                elif event.type == event.TYPE_FLAG_DROPPED:
                    event.instigator.flag_dropped += 1
                elif event.type == event.TYPE_FLAG_CAPTURED:
                    event.instigator.flag_captured += 1
            else:
                if event.type == event.TYPE_KILLED:
                    event.subject.deaths += 1

    """
    This method is executed every game tick. It updates the statistics, it
    can switch the team composition and it gives new orders to the bots
    (based on their own scripts).
    """
    def tick(self):
       # self.log.info("Tick at time " + str(self.game.match.timePassed) + "!")
        
        self.statistics.tick() # Update statistics
        self.knowledge.tick() # Update knowledge base

        # update bot stats
        self.updateBotStats()
        
        # should the commander issue a new strategy?
        # TODO:
        # 1. make distributeRoles take the current distribution into account
        # 2. Let initializeRoles take currently good performing scripts for roles into account
        
        roleList = self.metaScript.runDynamicScript([len(self.game.team.members),self.statistics])
        if roleList != None:
            self.log.info("Switching tactics and adjusting weights")
            self.updateWeights()
            self.distributeRoles(roleList)
            self.initializeRoles()
            # Generate a new script based on latest weights for the next time.
            self.metaScript = DynamicScriptingInstance(DynamicScriptingClass(self.metaRuleBase,"metaRules"))
            self.metaScript.generateScript(3)
        
		# a bot that has the flag needs to be a catcher
        for bot in self.game.team.members:
            if bot.flag is not None and bot.role != "catcher":
                bot.role = "catcher"
                bot.script = DynamicScriptingInstance(self.dsclassCatcher,botRole = bot.role,botNumber = bot.id)
                bot.script.generateScript(4)
                bot.script.insertInScript(Rule(catcherRules.default_catcher_rule))
    
        # give the bots new commands
        for bot in self.game.bots_available:
            bot.script.runDynamicScript([bot,self,self.knowledge])
            self.timeSinceLastCommand[bot.id] = self.game.match.timePassed     

        # detect bots that are stuck    
        for bot in self.game.team.members:
            # more than 30 seconds (90 ticks) since bot has been available
            # it is probably stuck doing something silly, so reactivate it.
            if self.game.match.timePassed - self.timeSinceLastCommand[bot.id] > 30:
                print "REACTIVATING BOT", bot.id
                bot.script.runDynamicScript([bot,self,self.knowledge])
                self.timeSinceLastCommand[bot.id] = self.game.match.timePassed     
    
    """
    This method is executed at the end of the game.
    """
    def shutdown(self):
        self.updateWeights()
        self.saveWeights()
        print "statistics:",self.statistics.ourScore,"-",self.statistics.theirScore
