#==============================================================================
# This file is part of The AI Sandbox.
# Copyright (c) 2007-2013, AiGameDev.com
#==============================================================================

"""Various helper functions for JSON data processing.
"""

from api.gameinfo import *
from api.orders import *
from api.vector2 import Vector2

def encodeVector2(v):
    return [v.x, v.y]

def decodeVector2(cls, v):
    assert isinstance(v, list)
    assert len(v) == 2
    return Vector2(v[0], v[1])

def encodeGameInfo(game):
    return { 'match': game.match,
             'team': game.team.name,
             'enemyTeam': game.enemyTeam.name,
             'teams': game.teams,
             'flags': game.flags,
             'bots': game.bots }

def decodeGameInfo(cls, value):
    game = GameInfo()
    game.match = value['match']
    game.teams = {}
    for name, team in value['teams'].items():
        game.teams[name] = team
    game.team = value['team'] # needs fixup
    game.enemyTeam = value['enemyTeam'] # needs fixup
    game.bots = {}
    for name, bot in value['bots'].items():
        game.bots[name] = bot
    game.flags = {}
    for name, flag in value['flags'].items():
        game.flags[name] = flag
    return game

def encodeTeamInfo(team):
    return  { 'name': team.name,
              'members': [b.name for b in team.members],
              'flag': team.flag.name,
              'flagScoreLocation': team.flagScoreLocation,
              'flagSpawnLocation': team.flagSpawnLocation,
              'botSpawnArea': team.botSpawnArea }

def decodeTeamInfo(cls, value):
    team = TeamInfo(value['name'])
    team.members = value['members'] # needs fixup
    team.flag = value['flag'] # needs fixup
    team.flagScoreLocation = value['flagScoreLocation']
    team.flagSpawnLocation = value['flagSpawnLocation']
    if value['botSpawnArea'] is not None:
        team.botSpawnArea = (value['botSpawnArea'][0], value['botSpawnArea'][1])    
    else:
        team.botSpawnArea = None
    return team

def encodeFlagInfo(flag):
    return { 'name': flag.name,
             'position': flag.position,
             'team': flag.team.name,
             'carrier': flag.carrier.name if flag.carrier else None,
             'respawnTimer': flag.respawnTimer }

def decodeFlagInfo(cls, value):
    flag = FlagInfo(value['name'])
    flag.team = value['team'] # needs fixup
    flag.position = value['position']
    flag.carrier = value['carrier'] if value['carrier'] else None # needs fixup
    flag.respawnTimer = value['respawnTimer']
    return flag

def encodeBotInfo(bot):
    return { 'name': bot.name,
             'team': bot.team.name,
             'health': bot.health,
             'state': bot.state,
             'position': bot.position,
             'facingDirection': bot.facingDirection,
             'seenlast': bot.seenlast,
             'flag': bot.flag.name if bot.flag else None,
             'visibleEnemies': [b.name for b in bot.visibleEnemies],
             'seenBy': [b.name for b in bot.seenBy] }

def decodeBotInfo(cls, value):
    bot = BotInfo(value['name'])
    bot.team = value['team'] # needs fixup
    bot.health = value['health']
    bot.state = value['state']
    bot.position = value['position'] if value['position'] else None
    bot.facingDirection = value['facingDirection'] if value['facingDirection'] else None
    bot.seenlast = value['seenlast'] if value['seenlast'] else None
    bot.flag = value['flag'] if value['flag'] else None # needs fixup
    bot.visibleEnemies = value['visibleEnemies'] # needs fixup
    bot.seenBy = value['seenBy'] # needs fixup
    return bot

def encodeMatchCombatEvent(combatEvent):
        return { 'type': combatEvent.type,
                 'subject': combatEvent.subject.name,
                 'instigator': combatEvent.instigator.name if combatEvent.instigator else None,
                 'time': combatEvent.time }

def decodeMatchCombatEvent(cls, value):
    combatEvent = MatchCombatEvent(value['type'], value['subject'], value['instigator'], value['time']) # subject and instigator needs fixup
    return combatEvent



def fixupReferences(obj, game):
    for bot in game.bots.values():
        assert bot is not None

    if isinstance(obj, LevelInfo):
        pass

    elif isinstance(obj, GameInfo):
        new_game = obj
        # game and new_game should be the same in production code
        # but they may differ in unittests
        new_game.team = game.teams[new_game.team]
        new_game.enemyTeam = game.teams[new_game.enemyTeam]
        for b in new_game.bots.values():
            fixupReferences(b, game)
        for t in new_game.teams.values():
            fixupReferences(t, game)
        for f in new_game.flags.values():
            fixupReferences(f, game)
        fixupReferences(new_game.match, game)

    elif isinstance(obj, TeamInfo):
        team = obj
        team.members = [game.bots[b] for b in team.members]
        team.flag = game.flags[team.flag]

    elif isinstance(obj, FlagInfo):
        flag = obj
        flag.team = game.teams[flag.team]
        flag.carrier = game.bots[flag.carrier] if flag.carrier else None

    elif isinstance(obj, BotInfo):
        bot = obj
        bot.team = game.teams[bot.team]
        bot.flag = game.flags[bot.flag] if bot.flag else None
        bot.visibleEnemies = [game.bots[b] for b in bot.visibleEnemies]
        bot.seenBy = [game.bots[b] for b in bot.seenBy]

    elif isinstance(obj, MatchInfo):
        match = obj
        for e in match.combatEvents:
            fixupReferences(e, game)

    elif isinstance(obj, MatchCombatEvent):
        combatEvent = obj
        if combatEvent.type == MatchCombatEvent.TYPE_KILLED:
            combatEvent.instigator = game.bots[combatEvent.instigator]
            combatEvent.subject = game.bots[combatEvent.subject]
            assert combatEvent.subject is not None
            assert combatEvent.instigator is not None
        elif combatEvent.type == MatchCombatEvent.TYPE_FLAG_PICKEDUP:
            combatEvent.instigator = game.bots[combatEvent.instigator]
            combatEvent.subject = game.flags[combatEvent.subject]
            assert combatEvent.subject is not None
            assert combatEvent.instigator is not None
        elif combatEvent.type == MatchCombatEvent.TYPE_FLAG_DROPPED:
            combatEvent.instigator = game.bots[combatEvent.instigator]
            combatEvent.subject = game.flags[combatEvent.subject]
            assert combatEvent.subject is not None
            assert combatEvent.instigator is not None
        elif combatEvent.type == MatchCombatEvent.TYPE_FLAG_CAPTURED:
            combatEvent.instigator = game.bots[combatEvent.instigator]
            combatEvent.subject = game.flags[combatEvent.subject]
            assert combatEvent.subject is not None
            assert combatEvent.instigator is not None
        elif combatEvent.type == MatchCombatEvent.TYPE_FLAG_RESTORED:
            assert combatEvent.instigator is None
            combatEvent.subject = game.flags[combatEvent.subject]
            assert combatEvent.subject is not None
        elif combatEvent.type == MatchCombatEvent.TYPE_RESPAWN:
            assert combatEvent.instigator is None
            combatEvent.subject = game.bots[combatEvent.subject]
            assert combatEvent.subject is not None
        else:
            assert False, "Unknown event type"


def fixupGameInfoReferences(obj):
    fixupReferences(obj, obj)


def mergeFlagInfo(gameInfo, newFlagInfo):
    flagInfo = gameInfo.flags[newFlagInfo.name]
    flagInfo.team         = newFlagInfo.team
    flagInfo.position     = newFlagInfo.position
    flagInfo.carrier      = newFlagInfo.carrier
    flagInfo.respawnTimer = newFlagInfo.respawnTimer
    fixupReferences(flagInfo, gameInfo)


def mergeBotInfo(gameInfo, newBotInfo):
    botInfo = gameInfo.bots[newBotInfo.name]
    botInfo.team            = newBotInfo.team
    botInfo.health          = newBotInfo.health
    botInfo.state           = newBotInfo.state
    botInfo.position        = newBotInfo.position
    botInfo.facingDirection = newBotInfo.facingDirection
    botInfo.seenlast        = newBotInfo.seenlast
    botInfo.flag            = newBotInfo.flag
    botInfo.visibleEnemies  = newBotInfo.visibleEnemies
    botInfo.seenBy          = newBotInfo.seenBy
    fixupReferences(botInfo, gameInfo)


def mergeMatchInfo(gameInfo, newMatchInfo):
    matchInfo = gameInfo.match
    matchInfo.scores            = newMatchInfo.scores
    matchInfo.timeRemaining     = newMatchInfo.timeRemaining
    matchInfo.timeToNextRespawn = newMatchInfo.timeToNextRespawn
    matchInfo.timePassed        = newMatchInfo.timePassed
    fixupReferences(newMatchInfo, gameInfo)
    matchInfo.combatEvents.extend(newMatchInfo.combatEvents)


def mergeGameInfo(gameInfo, newGameInfo):
    for newFlag in newGameInfo.flags.values():
        mergeFlagInfo(gameInfo, newFlag)

    for newBot in newGameInfo.bots.values():
        mergeBotInfo(gameInfo, newBot)

    mergeMatchInfo(gameInfo, newGameInfo.match)

