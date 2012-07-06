# -*- coding: utf-8 -*-
#make sure PYTHONPATH includes ..

import sys
import unittest
import simplematch

class BasicTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_bad_patterns(self):
        #ensure rejection of bad wildcard patterns

        bad_patterns = ["Ask Jeeves**",
                        "A*k Jeeves"]

        for p in bad_patterns:
            self.assertRaises(ValueError, simplematch.Matcher, [p])

    def test_universal_pattern(self):
        #a wildcard-only pattern should match any non-empty string
        
        m = simplematch.Matcher(['*'])
        uagents = ['X', 'Ask', 'AskBot', 'Mozilla/2.0 (compatible; Ask Jeeves)',
                   'Baiduspider-adserver', 'Baiduspider-aserver',
                   'Mozilla/1.0 (compatible; Ask Jeeves',
                   'Baiduspider-favo', 'askbot']

        self.assertEqual(None, m.matchRegex(''))
        
        for ua in uagents:
            self.assertEqual('*', m.matchRegex(ua))
            
    def test_basic_patterns(self):
        #validate examples given from problem description
        
        basic_patterns = ['Ask',
                          'Ask*',
                          'Mozilla/1.0 (compatible; Ask Jeeves/Teoma*',
                          'Mozilla/2.0 (compatible; Ask Jeeves/Teoma*',
                          'Mozilla/2.0 (compatible; Ask Jeeves)',
                          'Baiduspider-image*',
                          'Baiduspider-ads*',
                          'Baiduspider-cpro*',
                          'Baiduspider-favo*']

        expected = {'Ask' : 'Ask',
                    'AskBot' : 'Ask*',
                    'Mozilla/2.0 (compatible; Ask Jeeves)' : 'Mozilla/2.0 (compatible; Ask Jeeves)',
                    'Baiduspider-adserver' : 'Baiduspider-ads*',
                    'Baiduspider-aserver' : None,
                    'Mozilla/1.0 (compatible; Ask Jeeves' : None,
                    'Baiduspider-favo' : None,
                    'askbot' : None
                    }

        matcher = simplematch.Matcher(basic_patterns)
        for agent in expected:
            result = matcher.matchRegex(agent)
            self.assertEqual(expected[agent], result)
        
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
