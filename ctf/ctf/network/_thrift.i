#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2014, AiGameDev.com KG.
#==============================================================================

struct TVector2
{
    1: double x,
    2: double y,
}


struct TArea2
{
	1: TVector2 start,
	2: TVector2 finish,
}


enum EBotState
{
    UNKNOWN      = 0,             // The current state of the bot is invalid.
    IDLE         = 1,             // Not currently performing any orders.
    DEFENDING    = 2,             // Defending and automatically targeting.
    SPRINTING    = 3,             // Moving very quickly, avoiding contact.
    ATTACKING    = 4,             // Attacking methodically, targeting enemies.
    CHARGING     = 5,             // Charging quickly, can stop and target.
    SHOOTING     = 6,             // Shooting at an enemy underway.
    TAKINGORDERS = 7,             // Cooldown period after receiving an order.
    HOLDING      = 8,             // Attacking state, but blocked by defenders.
    DEAD         = 9,             // No longer alive, not moving or perceiving.
}


struct TBot
{
    1: string name,
    2: string team,

    3: string flag,
    4: double seenLast,
    5: double health,
    6: EBotState state,

    7: optional TVector2 position,
    8: optional TVector2 facingDirection,

    9: optional list<string> visibleEnemies,     // references TBot
    10: optional list<string> seenByEnemies,     // references TBot
}


struct TTeam
{
    1: string name,

    // Teams with the same faction number are allied, otherwise they are enemy.
    // Your AI has control of teams with a zero faction number (0).
    2: byte faction,

    3: list<string> members,                     // references TBot
    4: list<string> flags,                       // references TFlag

    5: list<TVector2> flagSpawnLocations,
    6: list<TArea2> flagScoreLocations,
    7: list<TArea2> botSpawnAreas,
}


struct TFlag
{
    1: string name,
    2: string team,                             // references TTeam
    3: TVector2 position,
    4: double respawnTimer,
    5: string carrier,                          // references TBot
}


struct TMatch
{
    1: map<string, i32> scores,
    2: double timeRemaining,
    3: double timeToNextRespawn,
    4: double timePassed,

    // 5: list<Events> events
}


struct TState
{
    1: TMatch match,

    2: map<string, TTeam> teams,
    3: map<string, TBot> bots,
    4: map<string, TFlag> flags,
}


struct TLevel
{
    1: i32 width,
    2: i32 height,

    3: list< list<byte> > blockHeights,

    // All the teams in this level.  Your own commander's team is always at index 0.
    4: list<string> teamNames,

    5: map<string, list<TVector2>> flagSpawnLocations,
    6: map<string, list<TArea2>> flagScoreLocations,
    7: map<string, list<TArea2>> botSpawnAreas,
}


struct TSettings
{
    1: list<double> fieldOfViewAngles,

    2: double characterRadius,
    3: double firingDistance,
    4: double walkingSpeed,
    5: double runningSpeed,

    6: double gameDuration,
    7: double initializationTime,
    8: double respawnDelay,
}


enum EOrderType
{
    DEFEND,
    ATTACK,
    CHARGE,
    SPRINT,
}


struct Order
{
    1: required EOrderType type,

    2: optional list<TVector2> positions,
    3: optional list<TVector2> facingDirections,
}


service _Commander
{
    TLevel getLevel();
    TSettings getSettings();

    TState getState();

    void connect(1: string name, 2: string language, 3: string version);
    void ready();
    void disconnect();

    oneway void sendDefendOrder(1: string bot, 2: TVector2 facingDirection);
    oneway void sendAttackOrder(1: string bot, 2: list<TVector2> positions, 3: TVector2 lookAt);
    oneway void sendChargeOrder(1: string bot, 2: list<TVector2> positions);
    oneway void sendSprintOrder(1: string bot, 2: list<TVector2> positions);

    oneway void sendOrders(1: list<Order> orders);

    bool step();
}
