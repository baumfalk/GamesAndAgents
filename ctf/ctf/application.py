#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2014 AiGameDev.com KG.
#==============================================================================

import os
import random
import importlib

from inspect import isclass

from inception.math import Vector2, Vector3, Quaternion, ColorValue
from inception.framework import ControllerManager
from inception.input import KeyEventDelegate, AnyKeyEventDelegate, KeyCode, EventPriority, MouseActionDelegate, MouseButtonID
from inception.navigation import NavigationComponent as _NavigationComponent, NavigationRepresentation as _NavigationRepresentation
from inception.rendering import OgreLight, Visualizer
from inception.simulation import WorldBuilderFromImage, DemoCamerasController
from inception.simulation import PickerManager
from inception.overlay import UserInterfacePlugin

from aisbx import logger, settings, game, reloader
from aisbx.visualizer.service import Service as VisService
from aisbx.game import camera

from ctf.gamestate import CaptureTheFlagGameState
from ctf.gamecontroller import CaptureTheFlagGameController

import api.commander

from ctf import character
from ctf import teambase
from ctf import levelconfig
from ctf import perception
from ctf import replayservice


__all__ = ['CaptureTheFlag']


# By default load these commanders if not specified on the command line, including
# a placeholder commander for you to modify.
defaultCompetitors = ['mycmd.Placeholder', 'examples.Balanced']

# Use these commanders for example if you want two networked clients with custom languages.
# defaultCompetitors = ['game.Network', 'game.Network']

## Possible levels that can be used.  Use the --level=<MAP> command line to specify.
levels = ['map00', 'map01', 'map02', 'map03', 'map04', 'map05',
          'map10', 'map11', 'map12', 'map13', 'map14', 'map15',
          'map20', 'map21', 'map22', 'map23', 'map24', 'map25',
          'map30', 'map31', 'map32', 'map33', 'map34', 'map35']


#Settings registry
settings.Section('ctf',

level           =   {'default': None, 'type': str,
                    'description': "Specify which level should be loaded, e.g. map00 or map21.  These are loaded from the .png and .ini file combination in #/assets/. If no level is specified, one is randomly chosen.",
                    'parseOpt': ['l', settings.PARSEOPTION.NAMED]
                    },
games           =   {'default': 1, 'type': int,
                    'description': "Number of simulated games to be run before quitting, -1 for infinite loop and by default play only one.",
                    'parseOpt': ['g', settings.PARSEOPTION.NAMED]
                    },
replay_file     =   {'default': None, 'type': str,
                    'description': "Enable the replay of a game from the given file.",
                    'parseOpt': ['r', settings.PARSEOPTION.NAMED]
                    },
competitors     =   {'default': defaultCompetitors, 'type': list,
                    'description': "The name of a script and class (e.g. mybot.Placeholder) implementing the Commander interface.  Files are exact, but classes match by substring.",
                    'parseOpt': ['', settings.PARSEOPTION.POSITIONAL, '*']
                    },
keep_running    =   {'default': False, 'type': bool,
                     'description': "Whether or not to keep the simulation running forever.",
                     'parseOpt': [None, settings.PARSEOPTION.NAMED]
                    },
viz_perception  =   {'default': True, 'type': bool,
                     'description': "Enable debug visualization of a characters perception cone.",
                     'parseOpt': [None, settings.PARSEOPTION.NAMED]
                    },
viz_character   =   {'default': False, 'type': bool,
                     'description': "Enable debug visualization of a character.",
                     'parseOpt': [None, settings.PARSEOPTION.NAMED]
                    },
viz_navigation  =   {'default': False, 'type': bool,
                     'description': "Enable debug visualization of paths.",
                     'parseOpt': [None, settings.PARSEOPTION.NAMED]
                    },
dev_visualizer  =   {'default': True, 'type': bool,
                     'description': "Enable WIP visualization API.",
                     'parseOpt': [None, settings.PARSEOPTION.NAMED]
                    },
)


##-------------------------------------------------------
class CaptureTheFlag(game.Application):
    """The main application responsible for setting up and running Capture the Flag games.

    This contains the top-level tick function, as well as logic for setting up or
    destroying the world and levels.

    Override of partly abstract base class.
    """

    def configure(self, config):
        """Sets up the configuration for the application when called by the base class.

        Override of abstract method of the base class.
        """
        config.name = 'ctf'
        config.title = 'Capture The Flag'
        config.theme = 'western'


    def __init__(self, commanderOptions=None, eventObserver=None, levelConfig=levelconfig.Competition()):
        super(CaptureTheFlag, self).__init__(eventObserver=eventObserver)

        self.helpWindowVisible = False

        config = settings.getSection('ctf')

        self.games = config.games
        self.level = config.level if config.level else random.choice(levels)
        self.keepRunning = config.keep_running

        self.levelConfig = levelConfig

        self.visualizerService = None
        self.gameState = None

        self.replayFilename = config.replay_file if config.replay_file else replayservice.DEFAULT_REPLAY_FILENAME
        enableReplay = (config.replay_file is not None) and os.path.isfile(self.replayFilename)
        self.replayService = replayservice.ReplayService(enableReplay)

        if enableReplay:
            self.replayService.loadFromFile(self.replayFilename)
            self.level = self.replayService.level
            self.levelConfig.configure(self.level)
            self.competitors = [replayservice.ReplayCommander, replayservice.ReplayCommander]
            self.levelConfig.commanders = self.competitors
            self.commanderOptions = [{'name': name, 'nick': opts['nick']} for name, opts in zip(self.replayService.commanders, commanderOptions)]
            self.games = 1
            self.reloadModules = None
        else:
            if self.level:
                self.levelConfig.configure(self.level)

            with reloader.saveImportedModulesList() as moduleList:
                self.competitors = self.getCompetitors(config.competitors)

            self.replayService.level = self.level
            self.commanderOptions = commanderOptions or [{} for _ in self.competitors]
            self.reloadModules = [m for m in moduleList.newModules if hasattr(m, '__name__')]

            assert len(self.competitors) > 0, "No commanders specified for this Competition."
            self.levelConfig.commanders = self.competitors


    def getCompetitors(self, names):
        """Return Python classes for Commanders specified by name.

        Given a list of Commander names, import the modules and return the class
        object so it can be instantiated for the game.  The string representing
        the Commander is in <module.ClassName> format, with the class being
        matched by sub-string case-insensitive search and the exact module name.

        Args:
            names (list): List of strings that represent a Commander.

        Returns:
            A list of Commander classes loaded by introspection.
        """
        competitors = []
        for request in names:
            if isclass(request) and issubclass(request, api.commander.Commander):
                competitors.append(request)
                continue

            if '.' in request:
                filename, _, classname = request.rpartition('.')
            else:
                filename, classname = request, None

            try:
                module = importlib.import_module(filename)
            except ImportError as e:
                self.log.error("Problem importing '%s', %s." % (request, e))
                raise

            found = False
            for c in dir(module):
                # Check if this Commander was explicitly exported in the module.
                if hasattr(module, '__all__') and not c in module.__all__:
                    continue
                # Discard private classes or the base class.
                if c.startswith('__') or c == 'Commander':
                    continue
                # Match the class by the specified sub-name.
                if classname is not None and classname.lower() not in c.lower():
                    continue

                # Now check it's the correct derived class...
                cls = getattr(module, c)
                try:
                    if isclass(cls) and issubclass(cls, api.commander.Commander):
                        competitors.append(cls)
                        found = True
                except TypeError:
                    pass

            if not found:
                self.log.error("Unable to find commander {}".format(request))
                assert False

        return competitors


    def createLevel(self):
        """Populate the world with static geometry, set the scene for the game.

        This function is called when the application is initialized or refreshed,
        and uses the level builder to add blocks.
        """
        self.scores = {}

        self.buildWorld(self.levelConfig.map)
        self.builder.sceneAddBlocks()


    def destroyLevel(self):
        """Remove all the static geometry from the world, tearing down the game.

        This function is called when the application is shutdown or about to be
        refreshed.  The work is delegated to the level builder.
        """
        self.builder.removeAllBlocks()


    def createGameState(self):
        """Returns the GameState instance to use with this application.
        """
        self.gameState = CaptureTheFlagGameState(self.world)
        self.replayService.dictionary = self.gameState

        renderer = self.services.getRenderer()
        if renderer is not None and settings.getSection('ctf').dev_visualizer:
            inpt = self.services.getInputHandler()
            visualizerPlugin = renderer.findPlugin(Visualizer)
            uiPlugin = renderer.findPlugin(UserInterfacePlugin)
            picker = PickerManager(renderer, self.world.getFloorPlane())
            self.visualizerService = VisService(3232, self.gameState, inpt, visualizerPlugin, uiPlugin, picker, self.log)
            self.visualizerService.start()

        return self.gameState


    def createGameController(self, gameState, builder):
        """Returns the GameController to use with this application.
        """
        return CaptureTheFlagGameController(gameState, builder, self.levelConfig, self.commanderOptions)


    def createGame(self):
        """Setup the Capture the Flag game, all the objects required to play.

        The simulation itself is split into game state (or the model) which
        stores data, and the logic (or controller) which updates every frame.
        """

        super(CaptureTheFlag, self).createGame()

        self.replayService.subscribeToControllers(self.gameController)

        if self.replayService.enabled:
            def tickFromReplay(ctrl, dt):
                idx = self.replayService.controllers.index(ctrl)
                self.replayService.requestEvents(ctrl, idx)

            self.gameController.ticker = tickFromReplay


    def destroyGame(self):
        """Discard all objects and entities required for playing Capture the Flag.

        First shut down the controller and remove it, then detach the state
        from world model.

        Override of virtual method of the base class.
        """

        super(CaptureTheFlag, self).destroyGame()


    def buildWorld(self, level):
        """Create the fundamental elements of the world.

        This function is called exactly once to setup required objects in the
        world such as a camera, light and the world's boundaries.

        Args:
            level (str): The filename for the .png file to build from.
        """
        self.builder = WorldBuilderFromImage(self.world)
        self.builder.setCenteredOnOrigin(False)
        self.builder.sceneLoadFrom(level)
        self.builder.setClampClearance(32)

        height = self.world.getBounds().getSize().x
        zoom = 0.73 # custom factor to tweak the size of the margin around the world

        config = settings.getSection('app')

        if self.resolution[0] > self.resolution[1]:
            orientation = Quaternion(0.7071067811865476, -0.7071067811865475, 0.0, 0.0)
        else:
            orientation = Quaternion(-0.5, 0.5, -0.5, -0.5)

        self.builder.createCamera("Camera", 1.0, height+1.0, self.world.getBounds().getCenter()+Vector3(0.0, zoom * height, 0.0), Vector3.ZERO, orientation)
        self.builder.createLight("SunLight", OgreLight.LightTypes.LT_DIRECTIONAL, ColorValue(1.0, 1.0, 1.0), ColorValue(0.25, 0.25, 0.25), Vector3(0.4, -2.0, -0.6), True)
        self.builder.setupBoundaries()


    def setupCameraController(self):
        """Setup and initialize a camera controller for this playground

        This function is called exactly once.

        Override of abstract method of the base class.
        """
        return camera.Controller(self.world, self.services, self.world.camera, self.gameState)


    def initialize(self):
        """Start the application and setup the basic infrastructure.

        This function explicitly initializes everything that's required to run
        a Capture the Flag game.  It supports both initializing with a window
        and in headless mode, based on parameters passed in to the constructor.

        Override of virtual method of the base class.
        """

        inpt = self.services.getInputHandler()

        #handling pause mode with keys control window together.
        self.wasPausedBeforeHelpWindowOpen = False
        self.funcKeyListener = AnyKeyEventDelegate(self._onKeyPressed)
        inpt.addAnyKeyPressedListener(self.funcKeyListener.getDelegate(), EventPriority.EP_LOW)

        config = settings.getSection('ctf')

        # In case there's a 3D window open, do some additional setup for visuals.
        if self.services.getRenderer():
            if config.viz_perception:
                self.services.getRenderer().view.associate(perception.PerceptionComponent, perception.CTFPerceptionConeRepresentation)
            if config.viz_character:
                self.services.getRenderer().view.associate(character.CharacterComponent, character.CharacterRepresentation)
            if config.viz_navigation:
                self.services.getRenderer().view.associate(_NavigationComponent, _NavigationRepresentation)

            self.services.getRenderer().view.associate(teambase.TeamBase, teambase.TeamBaseRepresentation)

        super(CaptureTheFlag, self).initialize()


    def tick(self):
        """This is the top-level of the application that runs CTF each frame.

        The application runs this function inside a loop as quickly as possible.
        The world is responsible for updating its internal model/view/controller
        representation, and the bulk of the work is done there.

        Override of virtual method of the base class.
        """

        self.replayService.incrementFrameCounter()
        super(CaptureTheFlag, self).tick()

        if self.gameState.gameMode in [game.GameState.MODE_FINISHING, game.GameState.MODE_FINISHED]:
            if self.levelConfig and self.levelConfig.endOfGameCallback:
                self.levelConfig.endOfGameCallback(self.gameState, self.gameController.commanders.keys())

            self.updateStatistics()

            if self.replayService:

                def getName(commander):
                    try:
                        return commander.getName()
                    except AttributeError:
                        cls = commander.__class__
                        return "%s.%s" % (cls.__module__, cls.__name__)

                self.replayService.commanders = [getName(c) for c in self.gameController.commanders]
                self.replayService.saveToFile(self.replayFilename)

            if self.gameState.gameMode == game.GameState.MODE_FINISHED:
                return

            self.games -= 1
            if self.games == 0:
                self.done = True
            else:
                self.refresh()


    def updateStatistics(self):
        """Extract information from the game state for later reporting.

        This queries the underlying model for details about the game scores,
        and stores them for later so they can be accessed externally.
        """
        total = sum([team.score for team in self.gameState.teams.values()])
        for commander in self.gameController.commanders:
            index = (commander.nick, commander.name)
            self.scores.setdefault(index, [0, 0])
            score = self.gameState.teams[commander.game.team.name].score
            against = total - score
            self.scores[index][0] += score
            self.scores[index][1] += against

        logger.getLog(logger.LOG_GAME).info("SCORES: " + str(self.scores))


    def onPause(self):
        if self.gameController.isPaused():
            logger.getLog(logger.LOG_GAME).info("Resumed the game at {:0.2f}s.".format(self.gameState.timePassed))
        else:
            logger.getLog(logger.LOG_GAME).info("Paused the game at {:0.2f}s.".format(self.gameState.timePassed))

        self.gameController.togglePause()
        self.systems.togglePause()


    def onRefresh(self):
        if self.reloadModules is not None:
            wasPaused = self.gameController.isPaused()

            if not wasPaused:
                self.gameController.togglePause()
                self.systems.togglePause()

            reloader.refresh(self.reloadModules)

            if not wasPaused:
                self.gameController.togglePause()
                self.systems.togglePause()


    def onGameFinished(self):
        self.gameState.gameMode = game.GameState.MODE_FINISHED if self.keepRunning else game.GameState.MODE_FINISHING


    def _onKeyPressed(self, keyCode, _):
        if keyCode == KeyCode.KC_F1:
            self.helpWindowVisible = not self.helpWindowVisible
            if self.helpWindowVisible and not self.gameController.isPaused():
                self.onPause()
            if not self.helpWindowVisible and not self.wasPausedBeforeHelpWindowOpen:
                self.onPause()
        elif keyCode == KeyCode.KC_P and not self.helpWindowVisible:
            self.onPause()
            self.wasPausedBeforeHelpWindowOpen = self.gameController.isPaused()
        return True
