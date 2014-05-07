import sys

from aisbx import callstack, settings
from ctf.application import CaptureTheFlag


class CaptureTheFlagTests(CaptureTheFlag):

    def __init__(self, level, verbosity = 'error'):
        config = settings.getSection('app')
        config.verbosity = verbosity

        super(CaptureTheFlagTests, self).__init__()
        self.levelConfig = level

    def initialize(self):
        super(CaptureTheFlagTests, self).initialize()
        self.setTitle(self.levelConfig.__class__.__name__)

        self.levelConfig = None
        self.completed = False
        self.testCreated = False
        self.numberTests = 0
        self.numberFailures = 0

    def shutdown(self):
        pass

