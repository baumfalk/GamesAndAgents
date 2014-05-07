#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

try:
    from ctf.network import serialization
    from ctf.network.commander import NetworkCommander
    __all__ = ['NetworkCommander']
except ImportError:
    # Running as a client, not all modules may be imported.
    pass
