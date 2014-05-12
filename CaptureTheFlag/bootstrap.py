from __future__ import print_function

import sys
import os
import argparse
import inspect


if 'win32' in sys.platform and sys.maxsize > 2**32:
    print("ERROR: 64-bit Python is not supported.", file=sys.stderr)
    sys.exit(1)


# Configure the directory you installed The AI Sandbox into using this global
# variable.  You can also specify --sbxdir=~/TheAiSandbox on the command
# line, or use the AISANDBOX_DIR environment variable so it's found
# automatically for all applications.
SBX_WORKING_DIR = None
SBX_INITIAL_DIR = None

# The binary directory is most often detected automatically from the
# installation folder.  If you want to specify this manually, you can use
# this global variable, or the command parameter --sbxbin or the environment
# variable called AISANDBOX_BIN.
SBX_BINARY_DIR = None

# You need to have a version of The AI Sandbox that matches this SDK version
# number.  More recent versions of The AI Sandbox may work, but ideally you
# should use the update scripts or grab the newest versions from the
# http://aisandbox.com/ download page.
SBX_REQUIRED_VERSION = "1.2.%i"



def find_eggs(path):
    """Scan the specified directory for packaged EGG modules, and add them
    to the Python path so they can be imported as any other module."""

    eggs = []
    for folder, subs, files in os.walk(path):
        for filename in [f for f in files if f.endswith('.egg')]:
            eggs.append(os.path.join(folder, filename))
    sys.path.extend([os.path.abspath(e) for e in eggs])


def setup_paths(binaryDir, appDir):
    """Given a binary directory, add necessary paths to the Python system for
    importing modules and egg files."""

    paths = [
        binaryDir,
        os.path.join(binaryDir, 'scripts'),
        os.path.join(binaryDir, 'packages'),
    ]

    ## Only include binaries\\site for win32 (win32 pre-compiled libs like gevent live there)
    if 'win32' in sys.platform:
        paths.append(os.path.join(binaryDir, 'site'))

    ## Only include the shipped standard library if it's the shipped executable.
    if 'aisbx-' in sys.executable:
        paths.insert(1, os.path.join(binaryDir, 'lib'))

    ## Only include the shipped standard library if it's the shipped executable.
    if 'aisbx-' in sys.executable:
        paths.insert(1, os.path.join(binaryDir, 'lib'))

    ## Extend the path list from the front to force local libraries.
    sys.path = [os.getcwd()] + sys.path[:1] + [os.path.normpath(p) for p in paths] + sys.path[1:]

    find_eggs(paths[0])
    find_eggs(appDir)
    find_eggs(os.path.dirname(__file__))


def setup_directory(workDir, appDir):
    """Knowing the working directory, make sure this is active and tell the
    AI Sandbox module of the starting directory to find various data files."""

    global SBX_INITIAL_DIR
    SBX_INITIAL_DIR = os.getcwd()
    os.chdir(workDir)

    from inception.framework import ApplicationFramework
    ApplicationFramework.setInitialDirectory(appDir)


def select_working_folder(options):
    """Setup the working directory from one of multiple configurable sources.
    In order, the command line, manually specified global variables, the
    execution environment, and the current directory as a fallback."""

    def hasAllSubFolders(folder, sub):
        for f in sub:
            if not os.path.isdir(os.path.join(folder, f)):
                return False
        return True

    for folder in [os.path.abspath(os.path.expanduser(o)) for o in options if o is not None]:

        if not os.path.isdir(folder):
            continue

        if hasAllSubFolders(folder, ['binaries', 'output', 'config', 'cache']):
            return folder

    print("""\
ERROR: Cannot find The AI Sandbox installation folder on your computer.

Please specify any of the following:
    * Parameter --sbxdir=<DIR> on the command line.
    * A global variable at the top of bootstrap.py.
    * The environment variable AISANDBOX_DIR.
    * Set the current working directory to this location.

""", file=sys.stderr)
    sys.exit(-1)


def select_binary_folder(options):
    """Setup the binaries folder in a similar fashion.  Either the command
    line, a manually specified global variable, the execution environment,
    or a directory specified in config/environment.pth."""

    for folder in [o for o in options if o is not None]:
        if inspect.isfunction(folder):
            try:
                folder = folder()
            except Exception:
                continue
        folder = os.path.abspath(os.path.expanduser(folder))

        if not os.path.isdir(folder):
            continue

        if os.path.isdir(os.path.join(folder, 'inception')):
            return folder

    print("""\
ERROR: Cannot find a valid binaries folder for The AI Sandbox.

Make sure the files are installed correctly.  Alternatively, specify:
    * Parameter --sbxbin=<DIR> on the command line.
    * A global variable at the top of bootstrap.py.
    * The environment variable AISANDBOX_BIN.
    * A file called binaries.pth in the 'config' directory.

""", file=sys.stderr)
    sys.exit(-1)


def initialize():
    """The main entry point of the bootstrap module, used to setup everything
    from paths to working directories and platform versions."""

    # Check for command line arguments if there are any.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--sbxdir')
    parser.add_argument('--sbxbin')
    args, _ = parser.parse_known_args()

    # First find the installation directory of The AI Sandbox for these options.
    workDir = select_working_folder([
        args.sbxdir,
        SBX_WORKING_DIR,
        os.getcwd(),
        os.path.normpath(os.path.join(os.getcwd(), '..')),
        os.environ.get('AISANDBOX_DIR', None),
        '/opt/aigamedev/aisbx/',
    ])

    # Then try to deduce the binaries folder, given the versioning system.
    binDir = select_binary_folder([
        args.sbxbin,
        SBX_BINARY_DIR,
        os.path.join(workDir, 'binaries'),
        lambda: os.path.join(workDir, open(os.path.join(workDir, 'config', 'environment.pth'), 'r').readline().rstrip()),
        os.environ.get('AISANDBOX_BIN', None),
    ])

    boxDir = os.path.join(os.path.split(os.path.abspath(sys.argv[0]))[0], '')

    if os.path.isdir(os.path.join(workDir, 'source', 'platform')):
        sys.path.append(os.path.join(workDir, 'source', 'platform'))

    # To find the dynamic libraries like Ogre, we need to set the path manually.
    if 'linux' in sys.platform and binDir not in os.environ.get('LD_LIBRARY_PATH', ''):
        # Check if a debugger is installed, but assume profiling modules are OK.  The user must set this before
        # starting a debug session on Linux since os.execv below will disconnect the debugger.
        assert not sys.gettrace() or 'trace' in sys.modules, "ERROR: You must set LD_LIBRARY_PATH before debugging."

        if 'LD_LIBRARY_PATH' in os.environ:
            os.environ['LD_LIBRARY_PATH'] += ":" + binDir
        else:
            os.environ['LD_LIBRARY_PATH'] = binDir

        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except OSError:
            print("ERROR: Fatal problem configuring the dynamic library path.", file=sys.stderr)
            sys.exit(-1)

    if 'win32' in sys.platform and binDir not in os.environ.get('PATH', ''):
        os.environ['PATH'] += ';' + binDir
        # on some systems setting the PATH isn't picked up by DLL search
        # we use WinAPI's SetDllDirectory to add modify DLL search path
        import ctypes
        ctypes.windll.kernel32.SetDllDirectoryA(binDir)

    setup_paths(binDir, boxDir)
    setup_directory(workDir, boxDir)

    # On Windows, the binary modules shipped depend on 2.7.5 or greater, for example greenlet.pyd.
    # If you see this error, please update your copy of Python.
    import platform
    version = '.'.join(platform.python_version_tuple())
    if 'win32' in sys.platform and version < '2.7.5':
        print("ERROR: Unsupported version of Python installed (%s)." % version, file=sys.stderr)
        sys.exit(1)


# When importing this module, presumably first, it performs initialization by default.
initialize()

# some more additional settings
import warnings
warnings.filterwarnings('ignore', message=r'Module .* was already imported from .*, but .* is being added to sys\.path', append=True)
