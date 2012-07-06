# -*- coding: utf-8 -*-

import sys
import optparse

class Matcher(object):
    """Quickly match a user agent string to a pattern or determine that
    no pattern matches.
    """
    
    def __init__(self, patterns):
        """Construct a new Matcher that will match each pattern in patterns.

        @param patterns: sequence of patterns to match
        @type patterns : iterable
        """

        self.wildcard_patterns = {}
        literals = []
        
        for j, pattern in enumerate(patterns):
            pattern = pattern.strip()
            wildcards = pattern.count('*')
            
            if wildcards == 0:
                literals.append(pattern)

            elif wildcards == 1:
                if not pattern.endswith('*'):
                    ve = "Pattern %i invalid: * can only appear at end of pattern." % j
                    raise ValueError(ve)

                self.add_wildcard_pattern(pattern)
                
            else:
                ve = "Pattern %i invalid: * can only appear once." % j
                raise ValueError(ve)

        self.literals = self.make_literal_set(literals)
        self.optimize_wildcard_patterns()
        self.pattern_lengths = sorted(self.wildcard_patterns.keys())

    def add_wildcard_pattern(self, pattern):
        """Index a wildcard pattern for fast lookup. The patterns are grouped
        by size.

        @param pattern: a textual pattern ending in *
        @type pattern : str
        """

        size = len(pattern)
        prefix = pattern[:-1]
        
        try:
            self.wildcard_patterns[size].append(prefix)
        except KeyError:
            self.wildcard_patterns[size] = [prefix]

    def optimize_wildcard_patterns(self):
        """Optimize the wildcard patterns structure by making pattern groups
        frozen sets for fast membership testing.
        """

        ct = 0
        for size in self.wildcard_patterns:
            self.wildcard_patterns[size] = self.make_literal_set(self.wildcard_patterns[size])
            ct += len(self.wildcard_patterns[size])

    def matchRegex(self, ua_string):
        """Try to pair a user agent with literal and wildcard patterns.

        Dictionary lookups and set membership tests are both fast operations
        in Python, with average-case time complexity of O(1). See
        http://wiki.python.org/moin/TimeComplexity for details.

        On average, the match operation should run in time O(n) where
        n is the number of distinct wildcard pattern prefix lengths, and the
        actual constant factor is small.

        TODO for further speed: based on real user agent distributions
        encountered in production, reorder the wildcard_pattern test loop to
        try most-likely first. This can be formulated as an online learning
        task instead of using static configuration values.

        @param ua_string: the user agent string to be matched
        @type ua_string : str
        @return: matching pattern | None
        @rtype : str | None
        """

        result = None

        if ua_string in self.literals:
            result = ua_string

        else:
            ua_size = len(ua_string)
            
            for pattern_size in self.wildcard_patterns:
                if pattern_size <= ua_size:
                    prefix = ua_string[:pattern_size - 1]
                    if prefix in self.wildcard_patterns[pattern_size]:
                        result = prefix + '*'
                        break

        return result

    def make_literal_set(self, literals):
        """Store literal patterns, without wildcard, in a frozen set for fast
        membership testing.

        @param literals: literal strings to be used as match-patterns
        @type literals : list
        @return: unique set of literal strings
        @rtype : frozenset
        """

        frozen = frozenset(literals)
        return frozen

def match_interactive(matcher):
    """Allow the user to test expressions interactively against a matcher.

    @param matcher: matcher containing patterns to test
    @type matcher : Matcher
    """
    
    print 'Try matchRegex("SomePattern") or type quit to quit.\n'

    matchRegex = matcher.matchRegex
    cmd = ""

    err_msg = "Bad input."

    while True:
        try:
            cmd = raw_input('> ').strip()
        except EOFError:
            sys.exit(0)
            
        if cmd == 'quit':
            sys.exit(0)

        elif cmd.startswith('matchRegex("'):
            try:
                result = eval(cmd)
                if result is None:
                    print "null"

                else:
                    print '"%s"' % result
            except:
                print err_msg

        else:
            print err_msg

if __name__ == '__main__':
    default_patterns = ['Ask',
                        'Ask*',
                        'Mozilla/1.0 (compatible; Ask Jeeves/Teoma*',
                        'Mozilla/2.0 (compatible; Ask Jeeves/Teoma*',
                        'Mozilla/2.0 (compatible; Ask Jeeves)',
                        'Baiduspider-image*',
                        'Baiduspider-ads*',
                        'Baiduspider-cpro*',
                        'Baiduspider-favo*']
    
    parser = optparse.OptionParser()

    parser.add_option("-p", "--pattern-file",
                      action="store", type="string", dest="pattern_file",
                      default="",
                      help="File containing patterns to match, one per line.")

    parser.add_option("--non-interactive",
                      action="store_false", dest="interactive",
                      default=True,
                      help="Don't go into interactive mode.")

    options, args = parser.parse_args()

    if options.pattern_file:
        try:
            m = Matcher(open(options.pattern_file))
            
        except IOError:
            sys.stderr.write("Can't load match patterns from %s.\n" % options.pattern_file)
            sys.exit(1)

        except ValueError, e:
            sys.stderr.write(e.args[0] + '\n')
            sys.exit(1)

    else:
        m = Matcher(default_patterns)

    if options.interactive:
        match_interactive(m)
