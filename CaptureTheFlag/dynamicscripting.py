import sys
import random
import math

def resetBotStats(bot):
    bot.deaths = 0
    bot.kills = 0
    bot.flag_pickedup = 0
    bot.flag_dropped = 0
    bot.flag_captured = 0
    bot.flag_restored = 0
#                
# dynamic scripting stuff
#
class Rule(object):
    def __init__(self, func):
        self.func = func
        self.weight = 1.0
        self.index = -1

class DynamicScriptingClass:
    """Generic Dynamic Scripting Class"""
    def __init__(self, rulebase, role):
          
        self.rulebase =  rulebase
        self.rulecount = len(rulebase)
        for i in range(0, self.rulecount):
            self.rulebase[i].index = i
            rulesmodule = sys.modules[role]
            # If a function with the string name exists in the module then store it
            # in the variable, we do this because the function names
            # are stored as strings in the rulebase
            if hasattr(rulesmodule, str(rulebase[i].func)):
                self.rulebase[i].func = getattr(sys.modules[role],str(rulebase[i].func))

class DynamicScriptingInstance:
    """Instance using a subset of rules from the generic dynamic scripting class"""
    def __init__(self, dsclass,botRole = "meta", botNumber = 0):
        self.rules = []
        self.rules_active = []
        self.scriptsize = 0
        self.dsclass = dsclass;
        self.botRole = botRole
        self.botNumber = botNumber

    def printScript(self):
        i = 1
        for rule in self.rules:
            print "Rule #",i,": ",rule.func.__name__
            i += 1
    
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

    def calculateTeamFitness(self, knowledge):
        """ Calculates the fitness of the team.
        The fitness depends on whether we would have won if the game ended now.
        """

        myScore = knowledge.teamOurScore()
        theirScore = knowledge.teamEnemyScore()
		
        if myScore + theirScore == 0:
            return 0
        
        team_score = (myScore - theirScore) / (myScore + theirScore)
        return team_score
        
    def calculateAgentFitness(self, bot, knowledge):
        """ Calculates the fitness of a specific agent.
        The fitness depends on the role of the agent (for a flag carrier flag captures are more important than kills)
        and on several performatives (number of kills, number of deaths, team performance, etc)
        """
        team_fitness = self.calculateTeamFitness(knowledge)
        
        bot_fitness = 0
        if(bot.role == "attacker"):
            bot_fitness = 0.4 * (bot.kills - bot.deaths)
            bot_fitness += 2.0 * bot.flag_captured
            bot_fitness += 0.4 * bot.flag_pickedup - 0.2 * bot.flag_dropped
        elif(bot.role == "defender"):
            bot_fitness = 0.25 * (bot.kills - bot.deaths)
            bot_fitness += 2.0 * bot.flag_restored
        else: #if(bot.role == "catcher"): #backup
            bot_fitness = 0.2 * (bot.kills - bot.deaths)
            bot_fitness += 3.0 * bot.flag_captured
            bot_fitness += 1.0 * bot.flag_pickedup - 0.3 * bot.flag_dropped
        
        #make sure fitness is between zero and one
        if bot_fitness > 0:
            bot_fitness = math.exp( -1 / bot_fitness ) 
        elif bot_fitness < 0:
            bot_fitness = -math.exp( 1 / bot_fitness ) 
        #reset the stats since we don't need them anymore. This does mean no peaking into the current fitness!
        resetBotStats(bot)

        return 0.75 * bot_fitness + 0.25 * team_fitness
            
    def adjustWeights( self, fitness, commander ):
        """ adjust the weights of the rules. Based on Spronck's paper """
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
            
        self.distributeRemainder( remainder )
    
 
    def runRule(self,index, parameters):
        """
        run a certain rule
        """
        rule_index = self.rules[index].index
        self.rules_active[rule_index] = True

        return self.rules[index].func(*parameters)
    
   
    def runDynamicScript( self, parameters):
        """
        Run one rule from the dynamic script.
        """
        for i in range(0, self.scriptsize):
            
            result = self.rules[i].func(*parameters)
            if result: # For non-booleans, will not execute if "None", but will execute if not "None"!
                print "Bot #", self.botNumber, "[", self.botRole, "] Rule #", (i+1), " named ", self.rules[i].func.__name__, " was  executed succesfully."
                print "Rule description:", self.rules[i].func.__doc__
                rule_index = self.rules[i].index
                self.rules_active[ rule_index ] = True
                return result
        return self.rules[len(self.rules)-1].func(*parameters)
