GamesAndAgents
==============

Team CaptureTheFacts!

################
# How to play: #
################

0. Install the AISandbox. It can be downloaded from http://releases.aisandbox.com/ You must create an account at http://www.aigamedev.com to login at the sandbox.
0.5. install jsonpickle by opening a terminal in the the CaptureTheFlag/jsonpickle-0.71 folder and running "python setup.py install" in that folder. This only needs to be done once.
1. Make sure the AISandbox is running.
2. run "python train.py" in the CaptureTheFlag folders. Run "python train.py --headless" to run the matches without graphics.
3. If it doesn't work, make sure that you are running the 32-bit version of python 2.7!

#############################
# Altering the competition: #
#############################
In train.py you can change how often the dynamic commander fights against differents bots. You can also add bots to fight against as follows:
if you have a bot 'bar', the code of which is in 'foo.py' (foo.py must be in the same folder as train.py), then you add the following to train.py

	showdowns["foo.bar"] = 1,

The DynamicCommander will then compete once against the bar bot.

