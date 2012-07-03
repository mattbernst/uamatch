# -*- coding: utf-8 -*-

import sys
import unittest

class BasicTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

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
        result = runSuite(BasicTestCase, name = test_name)
        
    else:
        result = runSuite(BasicTestCase)

    return result

if __name__ == '__main__':
    runTests()
