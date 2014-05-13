import os
cmd = "simulate.py match -a -v debug SleekoCommander.SleekoCommander barriebot.BarrieCommander -l map53"

for i in range(10):
    print i
    os.system(cmd)
    