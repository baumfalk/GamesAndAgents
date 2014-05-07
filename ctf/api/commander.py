#==============================================================================
# This file is part of The AI Sandbox.
# Copyright (c) 2007-2013, AiGameDev.com
#==============================================================================

"""This is the base class for any custom sandbox commanders.
"""

import os
import sys
import inspect
import logging
import datetime


class Commander(object):
    """The base class for Commanders, that give orders to the team members.
    This class should be inherited from to create your own competition Commander.
    You must implement `tick(self)` in your custom Commander.
    """

    def initialize(self):
        """Use this function to setup your bot before the game starts.
        You can also set self.verbose = True to get more information about each bot visually.
        You must not issue any orders during `initialize`.
        """
        pass


    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in `self.game`,
        which includes game information, and `self.level` which includes information about the level.
        You can send orders to your bots using the `self.issue()` function in this class.
        """
        raise NotImplementedError


    def shutdown(self):
        """Use this function to teardown your bot after the game is over.
        """
        pass


    def issue(self, OrderClass, bot, *args, **dct):
        """Issue an order to a single bot, with optional arguments depending on the order.
        `OrderClass`: must be one of `[api.orders.Defend, api.orders.Attack, api.orders.Move, api.orders.Charge]`
        """

        # In verbose mode, if no description is specificed substitute the
        # current order for this bot.
        if self.verbose and 'description' not in dct:
            dct['description'] = '[Order]'

        # If not verbose, then the game only prints the bot names visually.
        if not self.verbose and 'description' in dct:
            del dct['description']

        order = OrderClass.create(bot.name, *args, **dct)
        self.orderQueue.append(order)


    def __init__(self, nick, **kwargs):
        super(Commander, self).__init__()

        self.nick = nick
        self.name = self.__class__.__name__      #: The name of this commander.

        self.verbose = False             #: Set this to true to enable the display of the bot order descriptions next to each bot.        
        self.game = None                 #: The GameInfo object describing this Commander's knowledge of the current state of the game.
        """:type: api.gameinfo.GameInfo"""

        self.level = None                #: The LevelInfo object describing the current level.
        """:type: api.gameinfo.LevelInfo"""

        self.orderQueue = []             #: The queue where issued order are stored to be run later by the game
        self.cheat = False               #: For testing, should the game include all information about the opponent.


        self.log = logging.getLogger(self.name)  #: The logging object that should be used for debug printing.
        if not self.log.handlers:
            try:
                dirname = os.path.dirname(inspect.getfile(self.__class__))
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)

                timestamp = datetime.datetime.now().strftime(".%Y-%m-%d.%H;%M;%S")
                filename = os.path.join(dirname, 'logs', self.name+timestamp+'.log')

                self.log.setLevel(logging.DEBUG)
                output = logging.FileHandler(filename)
                output.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
                self.log.addHandler(output)

            except (OSError, IOError, TypeError):
                # error making the logging directory
                # error opening the log file
                # error because source is not found
                pass

            finally:
                class MyFilter(logging.Filter):
                    def filter(self, record):
                        return 1 if record.levelno < logging.WARNING else 0

                stderr = logging.StreamHandler(sys.stderr)
                self.log.addHandler(stderr)
                stderr.setLevel(logging.WARNING)
                # stderr.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

                stdout = logging.StreamHandler(sys.stdout)
                self.log.addHandler(stdout)
                stdout.setLevel(logging.INFO)
                stdout.addFilter(MyFilter())
                # stdout.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

