# -*- coding: utf-8 -*-

import sys
import subprocess
import shlex
import unittest

class MemoryTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def measure_peak_memory(self, cmd):
        """Measure the maximum resident set size of a command executed in a
        subprocess, as reported by time -v.

        @param cmd: shell command to be measured
        @type cmd : str
        @return: maximum resident set size in kilobytes
        @rtype : int
        """

        instrumented_cmd = '/usr/bin/time -v %s' % cmd
        command = shlex.split(instrumented_cmd)

        p = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        #time reports statistics on stderr, one stat per line
        for line in stderr.split('\n'):
            if 'Maximum resident set size' in line:
                kilobytes = int(line.split(':')[-1])
                return kilobytes

    def test_trivial(self):
        kb = self.measure_peak_memory('python -c "2 ** 12345678"')
        self.assertTrue(kb < 40000)

def runSuite(cls, verbosity=2, name=None):
    """Run a unit test suite and return status code.

    @param cls: class that the suite should be constructed from
    @type cls : class
    @param verbosity: verbosity level to pass to test runner
    @type verbosity : int
    @param name: name of a specific test in the suite to run
    @type name : str
    @return: unit test run status code
    @rtype : int
    """
    
    try: 
        if name:
            suite = unittest.makeSuite(cls, name)
        else:
            suite = unittest.makeSuite(cls)
            
        return unittest.TextTestRunner(verbosity=verbosity).run(suite)
    
    except SystemExit:
        pass

def runTests():

    try:
        test_name = sys.argv[1]
        
    except IndexError:
        test_name = None

    if test_name:
        result = runSuite(MemoryTestCase, name = test_name)
        
    else:
        result = runSuite(MemoryTestCase)

    return result

if __name__ == '__main__':
    runTests()
