import re


class SimpleTermFinder(object):

    terms = []
    matchers = []

    def __init__(self, terms):
        self.terms = terms
        self.matchers = [re.compile("\\b%s\\b" % t, re.IGNORECASE) for t in terms]

    def get_matches(self, sentence: str):
        matches = []
        for matcher in self.matchers:
            match = matcher.match(sentence)
            if match is not None:
                matches.append(match)
        return matches
