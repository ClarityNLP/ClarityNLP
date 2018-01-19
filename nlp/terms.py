import re


class SimpleTermFinder(object):

    terms = []
    matchers = []

    def __init__(self, terms):
        self.terms = terms
        self.matchers = [re.compile(r"\b%s\b" % t, re.IGNORECASE) for t in terms]

    def get_matches(self, sentence: str):
        matches = []
        for matcher in self.matchers:
            match = matcher.search(sentence)
            if match:
                matches.append(match)
        return matches
