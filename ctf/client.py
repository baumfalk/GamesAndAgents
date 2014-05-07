#!/usr/bin/python2.7 -u

import os
import sys
import glob
import time
import argparse
import threading
import subprocess

import bootstrap

from inspect import isclass

import importlib
import logging

from ctf.network import client

import api

logger = logging.getLogger('client')


def flushLog(l):
    for h in l.handlers:
        try:
            h.flush()
        except:
            pass


def getCommander(name, path):
    """Given a Commander name, import the module and return the class
    object so it can be instantiated for the competition."""

    globbed = False
    files = []
    classname = None
    if name:
        if '.' in name:
            filename, _, classname = name.rpartition('.')
        else:
            if name.islower():
                filename, classname = name, ''
            else:
                filename, classname = '', name

        if filename:
            files.append(filename)

    if not name or not files:
        globbed = True
        files = glob.glob(os.path.join(path, '*.py'))

    modules = []
    for f in files:
        try:
            modulename, _ = os.path.splitext(os.path.basename(f))
            modules.append(importlib.import_module(modulename))
        except ImportError as e:
            logger.critical("Specified module file could not be loaded by importer ({}).".format(modulename))
            logger.exception(e)
            sys.exit(1)
        except SyntaxError as e:
            logger.critical("Specified module file contained syntax on import ({}).".format(modulename))
            logger.exception(e)
            sys.exit(1)

    candidates = []
    for module in modules:
        for c in dir(module):
            # Check if this Commander was explicitly exported in the module.
            if hasattr(module, '__all__') and not c in module.__all__: continue
            # Discard private classes or the base class.
            if c.startswith('__') or c == 'Commander': continue
            # Match the class by the specified sub-name.
            if classname is not None and classname not in c: continue

            # Now check it's the correct derived class...
            cls = getattr(module, c)
            try:
                if isclass(cls) and issubclass(cls, api.commander.Commander):
                    candidates.append(cls)
            except TypeError:
                pass

    if len(candidates) == 0:
        if name:
            if globbed:
                logger.error('Unable to find file in path containing specified class ({}).'.format(name))
            else:
                logger.error('Specified module file does not contain class matching name ({}).'.format(classname))
            flushLog(logger)
        else:
            logger.error('Unable to find any commanders on path {}'.format(path))
            flushLog(logger)
        return None
    elif len(candidates) > 1:
        logger.error('Found more than one commander: {}'.format([c.__name__ for c in candidates]))
        flushLog(logger)
        return None
    else:
        cls = candidates[0]
        logger.debug('Loading `{}` from {}'.format(cls.__name__, sys.modules[cls.__module__].__file__))
        flushLog(logger)
        return cls


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=False, default='.')                          # optional path to look in for commanders
    parser.add_argument('--name', required=False, default='')                           # optional path for name of client
    parser.add_argument('--host', required=False, default='localhost')
    parser.add_argument('--port', type=int, required=False, default=41041)
    parser.add_argument('--dev-visualizer', required=False, default=True, action='store_true')
    parser.add_argument('--dev-interpreter', required=False, default=False, action='store_true')
    args, remaining = parser.parse_known_args()

    if args.path:
        sys.path.insert(0, args.path)

    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(logging.WARNING)
    flushLog(logger)

    if not os.path.isabs(args.path):
        args.path = os.path.normpath(os.path.join(bootstrap.SBX_INITIAL_DIR, args.path))

    if not os.path.exists(args.path):
        logger.warning('WARNING: The specified path was not found on disk.')
    elif not os.path.isdir(args.path):
        logger.warning('WARNING: The specified path is not a directory.')

    commanderCls = getCommander(args.name, args.path)
    if not commanderCls:
        sys.exit(1)

    if remaining and remaining[0] in ("challenge", "match"):
        logger.debug('Server spawning on {}:{}'.format(args.host, args.port))

        if os.path.isabs(__file__):
            scriptFile = __file__
        else:
            scriptFile = os.path.normpath(os.path.join(bootstrap.SBX_INITIAL_DIR, __file__))

        simFile = os.path.join(os.path.dirname(scriptFile), "simulate.py")
        process = subprocess.Popen([sys.executable, simFile] + remaining)
        time.sleep(1.0)
        if not process.poll() is None:
            logger.warning('Server process failed with code {}.'.format(process.returncode))
            sys.exit(1)
    else:
        process = None

    logger.debug('Client initializing on {}:{}'.format(args.host, args.port))
    flushLog(logger)

    wrapper = client.NetworkClient((args.host, args.port), commanderCls, args.name, args.dev_visualizer, args.dev_interpreter)

    logger.info('Client starting...')
    flushLog(logger)

    try:
        wrapper.run()
    except client.DisconnectError:
        logger.debug('Client disconnected.')

    logger.info('Client finished!')

    if process and process.poll() is not None:
        process.wait()

    flushLog(logger)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
        for t in [t for t in threading.enumerate() if not t.daemon and t.name != "MainThread" and not t.name.startswith("pydevd.")]:
            logger.warning("The following thread is still running (stop it in your commander): %s" % t.name)
            os._exit(1)
    except Exception as e:
        raise

    sys.exit(0)
