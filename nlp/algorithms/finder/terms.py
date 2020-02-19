from data_access import BaseModel
import itertools
import util
from algorithms.vocabulary import get_related_terms
from algorithms.context import *
from algorithms.sec_tag import *
from algorithms.segmentation import *
from cachetools import cached, LRUCache
from claritynlp_logging import log, ERROR, DEBUG
import regex
import string

log('Initializing models for term finder...')
try:
    section_tagger_init()
except Exception as ex1:
    log('Error initializing sed tagger', ERROR)
    log(ex1, ERROR)
c_text = Context()
segmentor = Segmentation()
spacy = segmentation_init()
log('Done initializing models for term finder...')
regex_cache = LRUCache(maxsize=1000)


class IdentifiedTerm(BaseModel):

    def __init__(self, sentence, term, negex, temporality, experiencer, section, start, end):
        self.sentence = sentence
        self.term = term
        self.negex = negex
        self.temporality = temporality
        self.experiencer = experiencer
        self.section = section
        self.start = start
        self.end = end


def get_filter_values(filters, key):
    if key in filters:
        val = filters[key]
        if val is not None:
            t = type(val)
            if t is list or t is set:
                return [str(x).strip().lower() for x in val]
            elif t is str:
                return [val.strip().lower()]
            elif t is int or t or float or t is complex or t is bool:
                return [str(val)]
            else:
                return val

        else:
            return []
    else:
        return []


def filter_match(lookup, filters):
    if filters is None or len(filters) == 0:
        return True
    else:
        lookup_str = lookup.strip().lower()
        return lookup_str in filters


def get_matches(matcher, sentence: str, section='UNKNOWN', filters=None):
    matches = list()
    match = matcher.search(sentence)
    match_ = matcher.match(sentence)
    findall = matcher.findall(sentence)

    if match:
        if filters is None:
            filters = dict()

        temporality_filters = get_filter_values(filters, "temporality")
        experiencer_filters = get_filter_values(filters, "experiencer")
        negex_filters = get_filter_values(filters, "negex")
        section_filters = get_filter_values(filters, "sections")

        context_matches = c_text.run_context(match.group(0), sentence)
        term = IdentifiedTerm(sentence, match.group(), str(context_matches.negex.name),
                              str(context_matches.temporality.name), str(context_matches.experiencier.name),
                              section, match.start(), match.end())
        if filter_match(term.temporality, temporality_filters) and filter_match(term.negex, negex_filters) \
                and filter_match(term.experiencer, experiencer_filters) and filter_match(term.section, section_filters):
            matches.append(term)

    return matches


def get_full_text_matches(matchers, text: str, filters=None, section_headers=None, section_texts=None,
                          excluded_matchers=None, strip_punct=False):
    if filters is None:
        filters = {}
    if section_headers is None:
        section_headers = [UNKNOWN]
    if section_texts is None:
        section_texts = [text]
    has_exclusions = excluded_matchers and len(excluded_matchers) > 0

    found_terms = list()

    for idx in range(0, len(section_headers)):
        section_text = section_texts[idx]
        sentences_raw = segmentor.parse_sentences(section_text, spacy=spacy)
        sentences = list()
        if strip_punct:
            for s in sentences:
                sentences.append(s.lower().translate(str.maketrans('', '', string.punctuation)))
        else:
            sentences = sentences_raw
        # section_code = ".".join([str(i) for i in section_headers[idx].treecode_list])

        list_product = itertools.product(matchers, sentences)

        for l in list_product:
            found = get_matches(l[0], l[1], section_headers[idx], filters)
            if found:
                excluded = False
                if has_exclusions:
                    for e in excluded_matchers:
                        if not excluded:
                            found_excluded = get_matches(e, l[1], section_headers[idx], filters)
                            if found_excluded:
                                excluded = True
                                break
                if not excluded:
                    found_terms.extend(found)
    return found_terms


@cached(regex_cache)
def get_matcher(t, max_errors=0):
    if all(x.isalpha() or x.isspace() for x in t):
        if max_errors > 0:
            return regex.compile(r'\b(%s)\b{e<=%d}' % (t, max_errors), flags=re.IGNORECASE)
        else:
            return regex.compile(r'\b({0})\b'.format(t), flags=re.IGNORECASE)
    else:
        return regex.compile("(%s){e<=%d}" % (t, max_errors), regex.IGNORECASE)


class TermFinder(BaseModel):

    def __init__(self, match_terms,  include_synonyms=False,
                 include_descendants=False, include_ancestors=False,
                 vocabulary='SNOMED', filters=None, excluded_terms=None,
                 max_errors=0):
        if filters is None:
            self.filters = {}
        else:
            self.filters = filters

        self.terms = list()
        for s in match_terms:
            s = s.replace("\r", " ").replace("\n", " ").strip()
            self.terms.append(s.lower())
        self.terms = list(set(self.terms))
        self.matchers = []
        added = []
        self.max_errors = max_errors
        if include_synonyms or include_descendants or include_ancestors and len(util.conn_string) > 0:
            for term in self.terms:
                added.extend(get_related_terms(util.conn_string, term, vocabulary, include_synonyms,
                                               include_descendants, include_ancestors))
            self.terms.extend(added)
        self.matchers = [get_matcher(t, max_errors=max_errors) for t in self.terms]
        self.secondary_matchers = list()
        for t in self.terms:
            if len(t) > 5:
                get_matcher(t, max_errors=self.max_errors+1)
        self.excluded_matchers = list()
        self.excluded_terms = list()
        if excluded_terms and len(excluded_terms) > 0:
            for s in excluded_terms:
                s = s.replace("\r", " ").replace("\n", " ").trim()
                self.excluded_terms.append(s.lower())
                self.excluded_terms.append(s.lower().translate(str.maketrans('', '', string.punctuation)))
        self.excluded_terms = list(set(self.excluded_terms))
        self.excluded_matchers = [get_matcher(t) for t in self.excluded_terms]

    def get_term_matches(self, sentence: str, section='UNKNOWN'):
        term_matches = list()
        for m in self.matchers:
            cur = get_matches(m, sentence, section)
            term_matches.extend(cur)
        return term_matches

    def get_term_full_text_matches(self, full_text: str, section_headers=None, section_texts=None):
        if section_headers is None:
            section_headers = [UNKNOWN]
        if section_texts is None:
            section_texts = [full_text]
        ft_matches = get_full_text_matches(self.matchers, full_text, self.filters, section_headers, section_texts,
                                           excluded_matchers=self.excluded_matchers)
        if ft_matches and len(ft_matches) > 0:
            return ft_matches
        else:
            return list()


if __name__ == "__main__":
    from xml.sax import saxutils as su
    stf = TermFinder(["Stroke",], excluded_terms=[], max_errors=2)
    txt = '''
   Assessment and Plan: 55 yo RHM with a left hemiparesis (leg&gt;arm, no
   facial weakness, and slightly slower production of speech, but no
   aphasia), who has a probable RIGHT ACA stroke Leg&gt;arm, face not
   involved, or a lacunar infarct. The stroke is unlikely to be a pontine
   lesion. His source is likely to be cardioembolic, since he has known AF
   and was subtherapeutic on Coumadin. 
    '''
    txt = su.unescape(txt)
    full_terms = stf.get_term_full_text_matches(txt)
    for ft in full_terms:
        log('', DEBUG)
        log(ft, DEBUG)

