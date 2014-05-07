import random

from inception.math import Situation, Quaternion, Radian, Vector3, ColorValue
from inception.motion import LocomotionComponent, Motion

import aisbx.actor.sensory
import aisbx.actor.navigation
import aisbx.actor.locomotion


from ctf.gameconfig import GameConfig
from ctf.character import CharacterComponent, CharacterController
from ctf.commands import WeaponKillTargetCommand
from ctf.events import CombatEvent

from ctf import health
from ctf import perception
from ctf import targeting
from ctf import weapon
from ctf import ragdoll


class BotFactory(object):

    @staticmethod
    def createBot(name, team, teamConfig, worldBuilder, gameState, gameController):
        actor = worldBuilder.createActor(ColorValue.White, Situation.IDENTITY)

        locomotion = actor.getComponent(LocomotionComponent)
        locomotion.setDefaultIdleMotion(Motion.Motion_Idle)
        averageRunSpeed = locomotion.getAverageSpeed(Motion.Motion_Run)
        # averageWalkSpeed = locomotion.getAverageSpeed(Motion.Motion_Walk)

        aisbx.actor.locomotion.BuildLocomotion(actor, locomotion)

        locomotion.setSpeedScale(Motion.Motion_Run, GameConfig.RUNNING_SPEED/averageRunSpeed)
        locomotion.setSpeedScale(Motion.Motion_Walk, GameConfig.WALKING_SPEED) # /averageWalkSpeed
        locomotion.setSpeedScale(Motion.Motion_Strafing, GameConfig.STRAFING_SPEED)

        ## navigation
        navigationComponent = aisbx.actor.navigation.NavigationComponent(actor)
        actor.addState(navigationComponent)

        ## health
        healthComponent = health.HealthComponent()
        actor.addState(healthComponent)
        healthController = health.HealthController(healthComponent)
        gameController.addController(healthController)

        ## targeting
        targetingComponent = targeting.TargetingComponent()
        actor.addState(targetingComponent)
        targetingController = targeting.TargetingController(targetingComponent)
        gameController.addController(targetingController)

        ## weapon
        weaponState = weapon.WeaponState(name + 'Weapon')
        actor.addState(weaponState)
        gameState.addWeapon(weaponState)
        weaponController = weapon.WeaponController(weaponState)
        gameController.addController(weaponController)
        weaponState.connect(WeaponKillTargetCommand, gameState)

        ## character
        (h, s, b) = teamConfig.color.getHSB()
        col = ColorValue(0.0, 0.0, 0.0, 1.0)
        col.setHSB(h, s + random.uniform(-0.3, +0.15), b + random.uniform(-0.4, +0.2))

        character = CharacterComponent(actor, name, team, col)
        actor.addState(character)

        ## sensory
        sensoryComponent = aisbx.actor.sensory.SensoryComponent(actor, gameController.sensorySystem)
        actor.addState(sensoryComponent)

        ## perception
        perceptionComponent = perception.PerceptionComponent(actor, gameController.perceptionSystem)
        perceptionComponent.perceptionFromEvents = \
            perceptionComponent.addPerceptionDevice(perception.PerceptionFromCombatEventDevice('event', perceptionComponent, 'combat', gameState))
        actor.addState(perceptionComponent)

        ## ragdoll
        ragdollComponent = ragdoll.RagdollState(actor)
        actor.addState(ragdollComponent)        
        ragdollController = ragdoll.RagdollController(ragdollComponent)
        gameController.addController(ragdollController)

        characterController = CharacterController(character)
        gameController.addController(characterController)

        team.members.add(character)
        gameState.actors.append(actor)
        return actor.character
