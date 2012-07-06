# -*- coding: utf-8 -*-

import sys
import subprocess
import random
import time
import shlex
import unittest
import simplematch

class PerfTestCase(unittest.TestCase):
    
    def setUp(self):
        random.seed(1)
    
    def tearDown(self):
        pass

    def make_patterns(self, n, wildcard_fraction, agent_file='uagents.txt'):
        """Produce a mixture of literal and wildcard match-patterns based
        on random selections from agent_file.

        The agent file is a text file containing one literal user agent string
        per line.

        @param n: total number of patterns to create
        @type n : int
        @param wildcard_fraction: portion of patterns ending in wildcard, 0 to 1
        @type wildcard_fraction : float
        @param agent_file: name of text file containing user agent strings
        @type agent_file : str
        @return: randomly created literal and wildcard patterns
        @rtype : list
        """

        agents = [line.strip() for line in open(agent_file).readlines()]
        patterns = []

        for j in range(n):
            agent = random.choice(agents)
            wildcard = random.random() < wildcard_fraction

            if wildcard:
                cut_point = random.randint(1, len(agent))
                pattern = agent[:cut_point] + '*'
                patterns.append(pattern)

            else:
                patterns.append(agent)

        return patterns

    def time_matches(self, matcher, agents):
        """Measure the time elapsed for matcher to match/reject all agents.

        @param matcher: agent matcher to test
        @type matcher : simplematch.Matcher
        @param agents: user agent strings to test
        @type agents : list
        @return: elapsed time in seconds
        @rtype : float
        """

        t0 = time.time()

        for agent in agents:
            matcher.match(agent)

        elapsed = time.time() - t0

        return elapsed

    def test_time_scaling(self):
        #test match speed scaling as number of patterns increases

        def random_prefix():
            prefix = list("somerandomjunk")
            random.shuffle(prefix)
            return ''.join(prefix)

        times = []
        sizes = [1000, 10000, 100000, 1000000]
        test_iterations = 100000
        no_match_fraction = 0.2

        all_patterns = self.make_patterns(sizes[-1], 0.8)

        #create random user agent sequence, and ensure that some fraction
        #will not match
        test_patterns = self.make_patterns(test_iterations, 0.0)
        for j in range(len(test_patterns)):
            if random.random() < no_match_fraction:
                test_patterns[j] = random_prefix() + test_patterns[j]
                
        for size in sizes:
            m = simplematch.Matcher(all_patterns[:size])
            t = self.time_matches(m, test_patterns)
            times.append(t)

        scalings = []
        while len(times) > 1:
            t = times.pop(0)
            scaling = times[0] / t
            scalings.append(scaling)

        #slow scaling: adding 10 times the patterns increases lookup cost by
        #less than 30%, across 4 orders of magnitude
        for s in scalings:
            self.assertTrue(s < 1.3)

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

    def test_memory_trivial(self):
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
        result = runSuite(PerfTestCase, name = test_name)
        
    else:
        result = runSuite(PerfTestCase)

    return result

if __name__ == '__main__':
    runTests()
