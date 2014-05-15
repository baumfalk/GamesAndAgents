import os
cmdBasic = "simulate.py match -a -v debug -l map53"

ourBot = "barriebot.BarrieCommander" # {packagename}.{botname}

showdowns = {} #nameofbot (str) / numberofbattles (int)
showdowns["examples.RandomCommander"] = 10
showdowns["examples.GreedyCommander"] = 11
showdowns["examples.DefenderCommander"] = 12
showdowns["examples.BalancedCommander"] = 13
showdowns["mycmd.PlaceholderCommander"] = 12
showdowns["SleekoCommander.SleekoCommander"] = 12
                                        
for key in showdowns.keys():
    print "Battling ", ourBot , " against ", key, "!"
    for i in range(showdowns[key]):
        print "Match [",i,"/",showdowns[key],"]"
        cmd = cmdBasic + " " + ourBot + " " + key + " --headless"
        os.system(cmd)
    
