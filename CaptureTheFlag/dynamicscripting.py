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

from api import gameinfo
from api.commander import Commander
from api import orders
from api.vector2 import Vector2
from knowledge import Knowledge
import sys
import jsonpickle
import random
import rules

def contains(area, position):
    start, finish = area
    return position.x >= start.x and position.y >= start.y and position.x <= finish.x and position.y <= finish.y
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
        self.statistics = {"numberOfKills":0} #todo: fill this while playing
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
        self.distributeRoles()
        # and generate the corresponding scripts
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
        
        #script generation! Currently only one rule in the rulebase.
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
        self.dsclassAttacker = DynamicScriptingClass(self.attackerRulebase)
        self.dsclassDefender = DynamicScriptingClass(self.defenderRulebase)
        self.dsclassCatcher = DynamicScriptingClass(self.catcherRulebase)
        for bot in self.game.team.members:       
            if(bot.role == "attacker"):
                self.log.info("Generating attacker script")
                bot.script = DynamicScriptingInstance(self.dsclassAttacker)
                bot.script.generateScript(1)
                # add default rule
                bot.script.insertInScript(Rule(rules.default_attacker_rule))
            elif(bot.role == "defender"):
                self.log.info("Generating defender script")
                bot.script = DynamicScriptingInstance(self.dsclassDefender)
                bot.script.generateScript(1)
                bot.script.insertInScript(Rule(rules.default_defender_rule))
            elif(bot.role == "catcher"):
                self.log.info("Generating catcher script")
                bot.script = DynamicScriptingInstance( self.dsclassCatcher)
                bot.script.generateScript(3)
                #for i in bot.script.rules: #to check if there are different type of rules at base
                #    print(i.rule_type)
                bot.script.insertInScript(Rule(rules.default_catcher_rule))
            else: #backup: also attacker 
                bot.script = DynamicScriptingInstance( self.dsclassAttacker)
                bot.role = "attacker"
                bot.script.generateScript(1)
                bot.script.insertInScript(Rule(rules.default_attacker_rule))

    def updateWeights(self):
        self.log.info("Updating weights!")
        self.metaRoleScript.adjustWeights(self.metaRoleScript.calculateTeamFitness(None),self)
        for bot in self.game.team.members:
            fitness = bot.script.calculateAgentFitness(bot.role,None)
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

    def tick(self):
       # self.log.info("Tick at time " + str(self.game.match.timePassed) + "!")
        
        self.knowledge.tick() #Update knowledge base
        
        # should the commander issue a new strategy?
        # TODO:
        # 1. make distributeRoles take the current distribution into account
        # 2. Let initializeRoles take currently good performing scripts for roles into account
        if self.metaSwitchScript.runRule(0,[self.statistics]):
            self.log.info("Switching tactics and adjusting weights")
            self.updateWeights()
            distributeRoles()
            initializeRoles()
    
        # give the bots new commands
        #self.log.info("Giving orders to all the bots")
        for bot in self.game.bots_available:
            bot.script.runDynamicScript([bot,self,self.knowledge])
    
    def shutdown(self):
        self.updateWeights()
        self.saveWeights()
#                
# dynamic scripting stuff
#
class Rule(object):
    def __init__(self, func):
        self.func = func
        self.weight = 1.0
        self.index = -1
        self.rule_type = 1

class DynamicScriptingClass:
    """Generic Dynamic Scripting Class"""
    def __init__(self, rulebase):
          
        self.rulebase =  rulebase
        self.rulecount = len(rulebase)
        self.different_types = []   # which different types
        self.rule_types = []        # rule types
        self.types_num = 0          # how many different types
        for i in range(0, self.rulecount):
            self.rulebase[i].index = i
            rulesmodule = sys.modules["rules"]
            # If a function with the string name exists in the module then store it
            # in the variable, we do this because the function names
            # are stored as strings in the rulebase
            if hasattr(rulesmodule, str(rulebase[i].func)):
                self.rulebase[i].func = getattr(sys.modules["rules"],str(rulebase[i].func))
            # add rule type
            self.rule_types.append(self.rulebase[i].rule_type)
        # get unique different types e.g. [1,2,3]
        self.different_types = list(set(self.rule_types))
        self.types_num = len(self.different_types)

class DynamicScriptingInstance:
    """Instance using a subset of rules from the generic dynamic scripting class"""
    def __init__(self, dsclass):
        self.rules = []
        self.rules_active = []
        self.scriptsize = 0
        self.dsclass = dsclass

    def insertInScript( self, rule ):
        if rule in self.rules:
            return False
        self.rules.append( rule )
        return True
    
    
    def generateScript( self, scriptsize ) :
        maxtries = 8

        self.scriptsize = scriptsize
        self.rules_active = [False for i in range(scriptsize)]
        self.rules = []
        # the rule types than are going to be added
        types = []
        # if all the rules are of the same type then we add 1
        if self.dsclass.types_num == 1:
            types =[1]*(scriptsize)
        else:
            k = 0
            tmp_list = self.dsclass.rule_types[:] # copy the list
            while len(types) < scriptsize and tmp_list:
                # use mod in order to get each type once before getting the same e.g. for 3 types 1,2,3,1,2,3
                index =  k % self.dsclass.types_num
                if self.dsclass.different_types[index] in tmp_list: # maybe there aren't anymore rules of that type
                    types.append(self.dsclass.different_types[index])
                    tmp_list.pop(tmp_list.index(self.dsclass.different_types[index]))
                k += 1
        sumweights = [0]*self.dsclass.types_num
        for i in range(0, self.dsclass.rulecount):
            # we calculate the weight for each rule type separately
            sumweights[self.dsclass.rulebase[i].rule_type-1] += self.dsclass.rulebase[i].weight
            self.rules_active.append( False )

        for i in range(0, scriptsize):
            num_tries = 0
            lineadded = False
            while num_tries < maxtries and not lineadded:
                j = 0
                sum = 0
                selected = False
                # fraction depending on the sum of the weights of the rule type
                fraction = random.uniform(0.0, sumweights[types[0]-1])
                while not selected:
                    # we sum the weight of the same rule type
                    if(self.dsclass.rulebase[j].rule_type == types[0]):
                        sum += self.dsclass.rulebase[j].weight
                    if sum > fraction and self.dsclass.rulebase[j].rule_type == types[0]:
                        selected = True
                    else:
                        j += 1
                lineadded = self.insertInScript( self.dsclass.rulebase[j] )
                if(lineadded):
                    # if line added pop and go to the next rule
                    types.pop(0)
                num_tries += 1

    def calculateAdjustment( self, fitness ):
        return fitness

    def distributeRemainder( self, remainder):
        for i in range(0, self.dsclass.rulecount):
            self.dsclass.rulebase[i].weight += remainder / self.dsclass.rulecount

    def calculateTeamFitness(self, performatives):
        """ Calculates the fitness of the team.
        The fitness depends on whether we would have won if the game ended now.
        """
        return random.random()  # random fitness, todo do something sensible here
        
    def calculateAgentFitness(self, agentRole, performatives):
        """ Calculates the fitness of a specific agent.
        The fitness depends on the role of the agent (for a flag carrier flag captures are more important than kills)
        and on several performatives (number of kills, number of deaths, team performance, etc)
        """
        return random.random() # random fitness, todo do something sensible here
            
    def adjustWeights( self, fitness, commander ):
        active = 0
        for i in range(0, self.scriptsize):
            print self.scriptsize, " ", len(self.rules_active)
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
            self.dsclass.rulebase[i].weight *= 10
            commander.log.info( "new weight", str(self.dsclass.rulebase[i].weight), " active:", str(self.rules_active[i]))
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
    def runDynamicScript( self, parameters ):
        for i in range(0, self.scriptsize):
            if self.rules[i].func(*parameters):
                rule_index = self.rules[i].index
                self.rules_active[ rule_index ] = True
                return # should we return here?
        # since there is no return then run the default rule
        self.rules[len(self.rules)-1].func(*parameters)
