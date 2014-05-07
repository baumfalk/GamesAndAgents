import bootstrap
import sys
import os

from multiprocessing.queues import Queue
from multiprocessing.pool import Pool
import multiprocessing
import itertools

from inception import demo as platform
from aisbx import callstack, settings
from ctf import application


def run(args):
    try:
        level, commanders = args
    
        #get config for application
        appConfig = settings.getSection('app')
        #only show errors
        appConfig.verbosity = 'warning'
        #set the competitors
        appConfig.competitors = list(commanders)
        #set the level
        appConfig.level = level
        #set number of games
        appConfig.games = 1
        
        sys.stderr.write('.')

        runner = platform.ConsoleRunner()

        runner.forceAcceleration()

        # no more parameters needed, the application gets it's information from the config/settings
        app = application.CaptureTheFlag()
        runner.main(app)
        sys.stderr.write('o')
        return level, app.scores
    except Exception as e:
        print >> sys.stderr, str(e)
        tb_list = callstack.format(sys.exc_info()[2])
        for s in tb_list:
            print >> sys.stderr, s
        raise
    except KeyboardInterrupt:
        return None 


if __name__ == '__main__':
    p = Pool(processes = multiprocessing.cpu_count())

    settings.initAndParseSettings()

    total = 0
    scores = {}

    mycmd = 'mycmd.Placeholder'
    competitors = ['examples.Greedy', 'examples.Balanced', 'examples.Random', 'examples.Defender']
    levels = ['map00', 'map01', 'map10', 'map11', 'map20', 'map30']

    pairs = itertools.product([mycmd], competitors)
    games = list(itertools.product(levels, pairs))

    print "Running against %i commanders on %i levels, for a total of %i games.\n" % (len(competitors), len(levels), len(games))
    try:
        for level, results in p.map(run, games):
            for (_, bot), score in results.items():
                scores.setdefault(bot, [0, 0, 0, 0, 0])
                scores[bot][0] += score[0]                      # Flags captured.
                scores[bot][1] += score[1]                      # Flags conceded.
                scores[bot][2] += int(score[0] > score[1])      # Win.
                scores[bot][3] += int(score[0] == score[1])     # Draw.
                scores[bot][4] += int(score[1] > score[0])      # Loss.
            total += 1
    except KeyboardInterrupt:
        print "\nTerminating competition due to keyboard interrupt."
        p.terminate()
        p.join()
    else:        
        print "\n"
        for r, s in sorted(scores.items(), key = lambda i: i[1][2]*30 + i[1][3]*10 + i[1][0] - i[1][1], reverse = True):
            nick = r.replace('Commander', '')
            if nick in mycmd: continue

            print "{}\n\tCaptured {} flags and conceded {}.\n\tWon {}, drew {} and lost {}.\n".format(nick.upper(), *s)

        print '\n\nAll matches played against {}; best opponent at top of list.\n'.format(mycmd)

    raw_input()
