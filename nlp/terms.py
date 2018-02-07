import re
import util
try:
    from .vocabulary import get_related_terms
except Exception as e:
    print(e)
    from vocabulary import get_related_terms


class SimpleTermFinder(object):

    terms = []
    matchers = []

    def __init__(self, terms, include_synonyms=False, include_descendants=False, include_ancestors=False):
        self.terms = terms
        added = []
        for term in self.terms:
            added.extend(get_related_terms(util.conn_string, term, include_synonyms, include_descendants,
                                           include_ancestors, True))
        if len(added) > 0:
            print("added the following terms through vocab expansion %s" % str(added))
            self.terms.extend(added)
        print("all terms to find %s" % str(self.terms))
        self.matchers = [re.compile(r"\b%s\b" % t, re.IGNORECASE) for t in terms]

    def get_matches(self, sentence: str):
        matches = []
        for matcher in self.matchers:
            match = matcher.search(sentence)
            if match:
                matches.append(match)
        return matches
