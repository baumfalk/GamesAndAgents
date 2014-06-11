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
The actual implementation in this rules is (currently) in this file. Most of the text files describe the rules for various roles
that a bot can have, such as an attacker, a defender etc. There are two special text files, namely meta_roles.txt and meta_switch.txt. These
files list the rules that are used for distributing the various roles to the bots and the rules used for deciding when to switch role distribution.

The code flow is as follows:

1. The commander is created. It loads all the rules from the dynamicscripting folder
2. It distributes the roles to the agents according to its meta role rules.
3. For each bot, a script is generated based on the rule set associated with its role
4. For each tick, the following happens:
5. The meta switch rules determine whether a role switch is necessary and if so, perform this.
6. Each bot generates a new action, based on its rule set and the information provided by the commander. The commander 'issues' this command
   to the bot (even though the bot generated it himself)

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
import rules
from dynamicscripting import *

def contains(area, position):
    start, finish = area
    return position.x >= start.x and position.y >= start.y and position.x <= finish.x and position.y <= finish.y

def resetBotStats(bot):
    bot.deaths = 0
    bot.kills = 0
    bot.flag_pickedup = 0
    bot.flag_dropped = 0
    bot.flag_captured = 0
    bot.flag_restored = 0
#
# RULES
# todo: maybe put this in different file
#   
 
# meta roles rules 
# currently just a list of strings, one string for each bot saying what role he is

class DynamicCommander(Commander):
    """
    A very dynamic and flexible commander ifyouknowwhatimean
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
            self.distributeRoles(rules.mixedAttackers(len(self.game.team.members)))
        # and generate the corresponding scripts
        self.initializeRoles()
        self.initializeBotStats()

    def loadMetaRules(self):
        self.log.info("Loading the meta rules")
        conn = open(sys.path[0]+"/dynamicscripting/meta.txt",'r')
        self.metaRuleBase = jsonpickle.decode(conn.read())
        conn.close()
        
        # Generate an initial meta script
        self.metaScript = DynamicScriptingInstance(DynamicScriptingClass(self.metaRuleBase))
        self.metaScript.generateScript(3)
    
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
    
    def distributeRoles(self,roleList):
        self.log.info("Distributing the roles")
        
        self.log.info("Rolelist: "+ str(roleList))
        #assign each bot a role
        for botIndex in range(len(roleList)):
            self.game.team.members[botIndex].role = roleList[botIndex]
            
    def initializeRoles(self):
        self.log.info("Initializing roles")
        self.dsclassAttacker = DynamicScriptingClass(self.attackerRulebase)
        self.dsclassDefender = DynamicScriptingClass(self.defenderRulebase)
        self.dsclassCatcher = DynamicScriptingClass(self.catcherRulebase)
        for bot in self.game.team.members:       
            if(bot.role == "attacker"):
                self.log.info("Generating attacker script")
                bot.script = DynamicScriptingInstance(self.dsclassAttacker)
                bot.script.generateScript(1)
                bot.script.insertInScript(Rule(rules.default_attacker_rule))
            elif(bot.role == "defender"):
                self.log.info("Generating defender script")
                bot.script = DynamicScriptingInstance(self.dsclassDefender)
                bot.script.generateScript(1)
                bot.script.insertInScript(Rule(rules.default_defender_rule))
            else: #if(bot.role == "catcher"): #backup
                self.log.info("Generating catcher script")
                bot.script = DynamicScriptingInstance(self.dsclassCatcher)
                bot.script.generateScript(1)
                bot.script.insertInScript(Rule(rules.default_catcher_rule))

    def initializeBotStats(self):
        for bot in self.game.team.members:
            resetBotStats(bot)

    def updateWeights(self):
        self.log.info("Updating weights!")
        self.metaScript.adjustWeights(self.metaScript.calculateTeamFitness(self.knowledge),self)
        for bot in self.game.team.members:
            fitness = bot.script.calculateAgentFitness(bot, self.knowledge)
            self.log.info("fitness:" + str(fitness))
            # print "fitness:" + str(fitness)
            for ruleid in  range(len(bot.script.dsclass.rulebase)):
                print "old weight of rule ", ruleid," ", bot.script.dsclass.rulebase[ruleid].weight
            #bot.script.dsclass.rulebase[0].weight = 100
            bot.script.adjustWeights(fitness,self)
            for ruleid in  range(len(bot.script.dsclass.rulebase)):
               print "new weight of rule ", ruleid," ", bot.script.dsclass.rulebase[ruleid].weight
            #print "newer weight ", self.attackerRulebase[0].weight

    def saveWeights(self):
        conn = open(sys.path[0]+"/dynamicscripting/attacker2.txt",'w')
        rulebaseEncoded = jsonpickle.encode(self.dsclassAttacker.rulebase)
        conn.write(rulebaseEncoded)
        conn.close()
         
        conn = open(sys.path[0]+"/dynamicscripting/defender2.txt",'w')
        rulebaseEncoded = jsonpickle.encode(self.defenderRulebase)
        conn.write(rulebaseEncoded)
        conn.close()
        
        conn = open(sys.path[0]+"/dynamicscripting/catcher2.txt",'w')
        rulebaseEncoded = jsonpickle.encode(self.catcherRulebase)
        conn.write(rulebaseEncoded)
        conn.close()
        
        conn = open(sys.path[0]+"/dynamicscripting/meta2.txt",'w')
        rulebaseEncoded = jsonpickle.encode(self.metaRuleBase)
        conn.write(rulebaseEncoded)
        conn.close()

    def updateBotStats(self):
        for event in self.game.match.combatEvents:
            if event.type == event.TYPE_FLAG_RESTORED:
                if event.subject.team == self.game.team:
                    for bot in self.game.team.members:
                        bot.flag_restored += 1
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
            self.metaScript = DynamicScriptingInstance(DynamicScriptingClass(self.metaRuleBase))
            self.metaScript.generateScript(3)
    
        # give the bots new commands
        #self.log.info("Giving orders to all the bots")
        for bot in self.game.bots_available:
            bot.script.runDynamicScript([bot,self,self.knowledge])
    
    def shutdown(self):
        self.updateWeights()
        self.saveWeights()