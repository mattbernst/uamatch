import hashlib

class Matcher(object):
    """Quickly match a user-agent string to a pattern or determine that
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
            wildcards = pattern.count('*')
            
            if wildcards == 0:
                literals.append(pattern)

            elif wildcards == 1:
                if not pattern.endswith('*'):
                    ve = "Pattern %i invalid: * can only appear at end of pattern." % j
                    raise ValueError(ve)

                self.add_wildcard_pattern(pattern)
                
            else:
                ve = "Pattern %i invalid: * can only appear once."
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

        for size in self.wildcard_patterns:
            self.wildcard_patterns[size] = self.make_literal_set(self.wildcard_patterns[size])

    def match(self, ua_string):
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
        task instead of baked in as configuration values.

        @param ua_string: the user-agent string to be matched
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

        
        
