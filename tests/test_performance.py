# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import random
import time
import shlex
import string
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
        patterns = set()

        for j in range(n):
            agent = random.choice(agents)
            wildcard = random.random() < wildcard_fraction

            if wildcard:
                cut_point = random.randint(1, len(agent))
                pattern = agent[:cut_point] + '*'
                while pattern in patterns:
                    pattern = pattern.replace('*', '%s*' % random.choice(string.ascii_letters))

                patterns.add(pattern)

            else:
                patterns.add(agent)

        return list(patterns)

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
            matcher.matchRegex(agent)

        elapsed = time.time() - t0

        return elapsed

    def test_memory_scaling(self):
        #test memory-consumption scaling as number of patterns increases

        wildcard_fraction = 0.9
        kilobytes = []
        scale_factor = 10
        sizes = [1000, 10000, 100000, 1000000]

        all_patterns = self.make_patterns(sizes[-1], wildcard_fraction)
        pattern_file = 'test_patterns.txt'
        
        for size in sizes:
            outfile = open(pattern_file, 'w')
            for pattern in all_patterns[:size]:
                outfile.write(pattern + '\n')

            cmd = "python simplematch.py -p %s --non-interactive" % pattern_file
            memory = self.measure_peak_memory(cmd)
            kilobytes.append(memory)

        scalings = []
        while len(kilobytes) > 1:
            kb = kilobytes.pop(0)
            scaling = kilobytes[0] / float(kb)
            scalings.append(scaling)

        #memory scales up faster than run time, but no worse than linear
        #N.B.: memory use expected to nearly double for 64 bit interpreter,
        #due to double pointer size
        try:
            for scaling in scalings:
                self.assertTrue(scaling < scale_factor)
        finally:
            os.unlink(pattern_file)

    def make_test_strings(self, n, no_match_fraction):
        """Produce a pseudorandom sequence of user agent strings for match
        testing.

        @param n: number of test strings to produce
        @type n : int
        @param no_match_fraction: fraction of strings that should fail to match
        @type no_match_fraction : float
        @return: test strings
        @rtype : list
        """

        def random_prefix():
            prefix = list("somerandomjunk")
            random.shuffle(prefix)
            return ''.join(prefix)

        test_patterns = self.make_patterns(n, 0.0)

        for j in range(len(test_patterns)):
            #add a random prefix to prevent matching anything: this will
            #yield the worst-case performance for the match attempt
            if random.random() < no_match_fraction:
                test_patterns[j] = random_prefix() + test_patterns[j]

        return test_patterns

    def test_speed(self):
        #show tests per second against pseudorandom user agent strings

        wildcard_fraction = 0.9
        no_match_fraction = 0.2
        num_patterns = 250000
        test_iterations = 100000
        all_patterns = self.make_patterns(num_patterns, wildcard_fraction)
        test_patterns = self.make_test_strings(test_iterations,
                                               no_match_fraction)
        
        m = simplematch.Matcher(all_patterns)
        t = self.time_matches(m, test_patterns)

        matches_per_second = test_iterations / t
        print "\nPerformed %.0f tests per second against matcher containing %i pseudorandom patterns" % (matches_per_second, num_patterns)
        
    
    def test_time_scaling(self):
        #test worst case match-speed scaling as number of patterns increases

        times = []
        sizes = [1000, 10000, 100000, 1000000]
        test_iterations = 100000
        no_match_fraction = 0.2
        wildcard_fraction = 0.9

        all_patterns = self.make_patterns(sizes[-1], wildcard_fraction)

        for size in sizes:
            m = simplematch.Matcher(all_patterns[:size])
            #worst performance case: '$' will never match, all tests must
            #be exhausted
            t = self.time_matches(m, ['$'] * test_iterations)
            times.append(t)

        scalings = []
        while len(times) > 1:
            t = times.pop(0)
            scaling = times[0] / t
            scalings.append(scaling)

        #slow scaling: adding 10 times as many patterns increases test cost by
        #less than 50%, across 4 orders of magnitude
        for s in scalings:
            self.assertTrue(s < 1.5)

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
