#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

"""Ragdoll components (state and controller) to allow a bot to go into ragdoll
   when it is killed.
"""

import inception
from inception import framework
from inception.physics import RagdollComponent, RagdollSynchronizationController

from ctf.gameconfig import GameConfig


class RagdollState(inception.physics.RagdollComponent):
    """Component that stores a ragdoll state.
    """

    def __init__(self, actor):
        """Setup parameters for this particular ragdoll.
        """
        super(RagdollState, self).__init__()
        self.init(actor)
        self.deactivate()
        self.synchronizationController = None


class RagdollController(framework.Controller):
    """Ragdoll logic for synchronizing ragdoll with animation.
    """

    def __init__(self, ragdoll):
        super(RagdollController, self).__init__(ragdoll)
        self.ragdoll = ragdoll
        self.synchronizationController = RagdollSynchronizationController()
        self.synchronizationController.init(ragdoll)
        self.ragdoll.synchronizationController = self.synchronizationController
         
    def update(self, dt):
        self.synchronizationController.tick(dt)

    def tick(self, dt):
        pass
