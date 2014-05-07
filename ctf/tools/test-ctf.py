#!/usr/bin/env python2.7
# This script is used to run automated tests on CaptureTheFlag after the build
# has succeeded.  It's used as part of the continuous integration of Trac/Bitten
# at http://dev.aisandbox.com/

import sys
import os

def run(category):
    """Run an automated test from the distutils script, assuming Bitten is
    installed to provide the `unittest` command.
    """
    os.system('python setup.py unittest --test-suite tests.'+category)


print "======================================================================"
print "= UNIT TESTS                                                         ="
print "======================================================================\n"
run('unit')
print

print "======================================================================"
print "= FUNCTIONAL TESTS                                                   ="
print "======================================================================\n"
run('func')
print

print "======================================================================"
print "= STRESS TESTS                                                       ="
print "======================================================================\n"
run('stress')
print
