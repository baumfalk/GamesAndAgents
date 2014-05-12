#!/usr/bin/python2.7

#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

import bootstrap

from ctf.application import CaptureTheFlag


# USAGE:
#   simulate.py match --help
#   simulate.py challenge --help


def run_match(args):
    """Execute the CTF application by setting up its runner, then launching it.
    
    This function returns once the simulation is over.  To customize the
    game you can derive from the application, and to configure the execution
    see the command line arguments with `--help`.
    """

    from aisbx import runner
    return runner.main(CaptureTheFlag, args)



def run_challenge(args):
    """Launch a single map evaluation of a challenge.
    """

    from aisbx import simulator
    return simulator.main_challenge(CaptureTheFlag, args)


def run_evaluate(args):
    """Launch a full simulation of a challenge, which may include multiple matches.

    The simulator uses multi-processing to handle each of the individual matches, and
    returns the final result.  Also use the `--help` argument for this command to see
    options available for configuring challenges.
    """

    from aisbx import simulator
    return simulator.main_evaluate(CaptureTheFlag, args)



# This is the entry point for the whole application.  The main function is
# called only when the module is first executed.  Subsequent resetting or
# refreshing cannot automatically update this __main__ module.
if __name__ == '__main__':
    import os
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    if cmd == "match":
        code = run_match(args)
    elif cmd == "evaluate":
        code = run_evaluate(args)
    elif cmd == "challenge":
        code = run_challenge(args)
    else:
        print "USAGE: %s (match|challenge|evaluate) [args]" % os.path.basename(sys.argv[0])
        code = 1

    sys.exit(code or 0)
