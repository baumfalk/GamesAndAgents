#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

"""Weapon components (state and controller) to allow a bot to shoot another.
"""

from inception import framework

from ctf.gameconfig import GameConfig
from ctf.commands import WeaponCommand, WeaponFireShotCommand, WeaponKillTargetCommand, WeaponClearTargetCommand


class WeaponState(framework.State):
    """Component that stores a weapon state.

    The class includes member variables for when to fire next, how much damage
    is inflicted, and who the current target is.  This component also
    centralizes events relating to weapons being fired  or killing.
    """

    def __init__(self, name):
        """Setup parameters for this particular weapon.
        """
        super(WeaponState, self).__init__()

        self.name = name                                            #: The string identifier of this weapon.
        self.nextFireDelay = GameConfig.AQUIRE_TARGET_DELAY         #: Time in seconds when this weapon can be fired next.
        self.damage = GameConfig.WEAPON_DAMAGE                      #: How much damage this weapon deals.
        self.target = None                                          #: The current target bot, or None.

    def clearTarget(self):
        """Target was lost, reset it and update the firing delay.
        """
        self.target = None
        self.nextFireDelay = max(self.nextFireDelay, GameConfig.AQUIRE_TARGET_DELAY)

    def resetTargetAfterShot(self, delay):
        """"Reload the weapon, and set the firing delay as specified.

        Args:
            delay (float) Time interval before weapon can be fired again.
        """
        self.target = None
        self.nextFireDelay = delay


class WeaponController(framework.Controller):
    """Weapon logic for bots dealing damage.
    """

    def __init__(self, weapon):
        super(WeaponController, self).__init__(weapon)
        self.weapon = weapon

        self.subscribe(WeaponFireShotCommand, self.cmdFireShot)
        self.subscribe(WeaponClearTargetCommand, self.cmdClearTarget)

        self.connect(WeaponCommand, self.weapon)


    def tick(self, dt):
        self.weapon.nextFireDelay = max(0, self.weapon.nextFireDelay-dt)

        # do this first to allow simultaneous firing
        if self.weapon.target:
            target = self.weapon.target
            targetHealthComponent = target.healthComponent

            # Don't shoot dead people
            if targetHealthComponent.points <= 0:
                self.send(WeaponClearTargetCommand(self.weapon))
                return

            target = self.weapon.target

            # Read to fire the weapon? If so, send event.
            if self.weapon.nextFireDelay <= 0:
                self.send(WeaponFireShotCommand(self.weapon, target))

            # If target is dead, also dispatch event.
            if targetHealthComponent.points <= 0:
                self.send(WeaponKillTargetCommand(self.weapon, target))

    def cmdFireShot(self, event):
        # assert event.target.actor in self.weapon.perceptionComponent.perceivableEntities['visual']
        targetHealthComponent = event.target.healthComponent
        targetHealthComponent.applyDamage(event.weapon.damage, self.weapon.location.getPosition())
        event.weapon.resetTargetAfterShot(event.weapon.characterComponent.getReloadDelay())

    def cmdClearTarget(self, event):
        event.weapon.clearTarget()

