import os
import shutil
import tempfile
import unittest
import subprocess
import bootstrap


class ClientTests(unittest.TestCase):


    def setUp(self):
        self.workdir = bootstrap.SBX_INITIAL_DIR
        self.tmpdir = tempfile.mkdtemp()
        os.chdir(self.tmpdir)


    def tearDown(self):
        os.chdir(self.workdir)
        shutil.rmtree(self.tmpdir)


    def call(self, *args):
        self.client = subprocess.Popen(['python', os.path.join(self.workdir, 'client.py')] + list(args),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return self.client.communicate()


class VerifyClientErrors(ClientTests):

    def setUp(self):
        ClientTests.setUp(self)


    def tearDown(self):
        ClientTests.tearDown(self)
        self.assertNotEqual(0, self.client.poll())


    def test_NoArguments(self):
        out, err = self.call()
        self.assertTrue("Unable to find any commanders on path" in err)


    def test_InvalidCommanderModule(self):
        _, err = self.call('--name=nocmd')
        self.assertTrue("Specified module file could not be loaded by importer (nocmd)." in err)


    def test_InvalidCommanderClass(self):
        _, err = self.call('--name=NoClass')
        self.assertTrue("Unable to find file in path containing specified class (NoClass)." in err)


    def test_InvalidModuleAndClass(self):
        _, err = self.call('--name=nocmd.NoClass')
        self.assertTrue("Specified module file could not be loaded by importer (nocmd)." in err)


    def test_ValidModuleInvalidClass(self):
        with open('mycmd.py', 'w') as out:
            out.write("import api.commander as cmd\nclass MyCmd(cmd.Commander): pass")
        _, err = self.call('--name=mycmd.NoClass')
        self.assertTrue("Specified module file does not contain class matching name (NoClass)" in err)


    def test_SyntaxError(self):
        with open('mycmd.py', 'w') as out:
            out.write("! % ^ &")
        _, err = self.call('--name=mycmd')
        self.assertNotEquals(err, "Specified module file contained syntax on import (mycmd)")


    def test_InvalidModuleImported(self):
        with open('mycmd.py', 'w') as out:
            out.write("import xxx\nimport api.commander as cmd\nclass MyCmd(cmd.Commander): pass")
        _, err = self.call('--name=mycmd.NoClass')
        self.assertTrue("Specified module file could not be loaded by importer (mycmd)." in err)


class VerifyClientCommands(ClientTests):

    def test_HelpCommandDisplaysInformation(self):
        out, err = self.call('--help')
        self.assertEquals(err, "")
        self.assertTrue("-h, --help" in out)
        self.assertTrue("show this help message and exit" in out)



if __name__ == '__main__':
    unittest.main(verbosity=2)
