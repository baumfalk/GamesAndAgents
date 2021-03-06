import os
import sys
cmdBasic = "python simulate.py match -a --viz-navigation --viz-perception --viz-character -v info "

ourBot = "dynamiccommander.DynamicCommander" # {packagename}.{botname}

showdowns = {} #nameofbot (str) : numberofbattles (int)
#showdowns["barriebot.BarrieCommander"] = 10
"""showdowns["examples.RandomCommander"] = 10
showdowns["examples.GreedyCommander"] = 11
showdowns["examples.DefenderCommander"] = 12
showdowns["examples.BalancedCommander"] = 13
"""
showdowns["examples.RandomCommander"] = 3
showdowns["mycmd.PlaceholderCommander"] = 3

showdowns["SleekoCommander.SleekoCommander"] = 3

args = sys.argv[1:] if len(sys.argv) > 1 else []

for key in showdowns.keys():
    print "Battling ", ourBot , " against ", key, "!"
    for i in range(showdowns[key]):
        print "Match [",(i+1),"/",showdowns[key],"]"
        cmd = cmdBasic + " " + ourBot + " " + key
        
        if len(args) > 0 and args[0] == "--headless":
            cmd += " --headless"

        os.system(cmd)
    