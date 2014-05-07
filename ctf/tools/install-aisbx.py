#!/usr/bin/env python2.7
# This script is used to download and install The AI Sandbox on its target
# platform.  It's used as part of the automated tests managed by Trac/Bitten
# at http://dev.aisandbox.com/

import os
import sys
import shutil
import tempfile

if 'linux' in sys.platform:
    platform, _, _, _, architecture = os.uname()
    postfix = {'x86_64': 'amd64', 'i686': 'i386'}
    filename = "aisbx_preview_" + postfix[architecture] + ".deb"
    os.chdir(tempfile.gettempdir())
    os.system("wget -q -N http://releases.aisandbox.com/"+filename)
    os.system("sudo dpkg --remove aisbx")
    os.system("sudo dpkg --purge aisbx")
    try:
        shutil.rmtree("/opt/aigamedev")
    except OSError:
        pass
    os.system("sudo dpkg --install " + filename)

if 'win32' in sys.platform:
    os.chdir(tempfile.gettempdir())
    import urllib2
    response = urllib2.urlopen('http://releases.aisandbox.com/aisbx_preview_win32.exe')
    with open('install.exe', 'wb') as f:
        f.write(response.read())
    try:
        shutil.rmtree(os.path.expandvars("%LocalAppData%\\AiGameDev.com"))
    except OSError:
        pass
    os.system('install.exe -ai0')

