import os
import sys

folder = os.path.dirname(os.path.abspath(__file__))

if 'unittest' in sys.argv and not sys.gettrace():
    # When run as an automated test with Bitten's `unittest' command, keep
    # output quiet and focused on test results!
    sys.argv.insert(1, '--quiet')

    # Create a specific folder for code coverage results, as expected by
    # Trac's continuous integration.
    build_dir = os.path.join(folder, 'build')
    try:
        os.mkdir(build_dir)
    except OSError:
        pass

    # Determine filename of the output coverage files.
    category = 'test'
    for arg in sys.argv:
        if 'tests.' in arg:
            category = arg.split('.')[-1]
            break

    test_prefix = os.path.join(build_dir, 'test')
    sys.argv.extend([
        "--xml-output={}_{}.xml".format(test_prefix, category),
        "--coverage-dir={}_{}.cov".format(test_prefix, category),
        "--coverage-summary={}_{}.trace".format(test_prefix, category),
        "--coverage-method=trace"
    ])

    # The `trace` code coverage tool fails on certain files, especially
    # those imported from installed .egg files.  Suppress those warnings!
    class silencer(object):
        def __init__(self, stderr):
            self.stderr = stderr
            self.blocked = False

        def write(self, line):
            if self.blocked and line == "\n":
                self.blocked = False
            elif "Not printing coverage data" in line:
                self.blocked = True
            else:
                self.stderr.write(line)

    sys.stderr = silencer(sys.stderr)


from setuptools import setup, find_packages

try:
    setup(
        name='impl',
        version='2.0',
        packages=[p for p in find_packages() if 'ctf' in p]
    )
except:
    if '--verbose' in sys.argv:
        import traceback
        traceback.print_exc()
    sys.exit(1)

