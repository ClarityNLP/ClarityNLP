import re
from multiprocessing import Pool
from data_access import BaseModel
import itertools
import util
try:
    from .vocabulary import get_related_terms
    from .context import *
    from .sec_tag import *
    from .segmentation import *
except Exception as e:
    from vocabulary import get_related_terms
    from context import *
    from sec_tag import *
    from segmentation import *


print('Initializing models for term finder...')
section_tagger_init()
c_text = Context()
segmentor = Segmentation()
print('Done initializing models for term finder...')


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
            return val
        else:
            return []
    else:
        return []


def get_matches(matcher, sentence: str, section='UNKNOWN', filters={}):
    matches = []
    match = matcher.search(sentence)
    temporality_filters = get_filter_values(filters, "temporality")
    experiencer_filters = get_filter_values(filters, "experiencer")
    negex_filters = get_filter_values(filters, "negex")

    if match:
        context_matches = c_text.run_context(match.group(0), sentence)
        term = IdentifiedTerm(sentence, match.group(), str(context_matches.negex.name),
                              str(context_matches.temporality.name), str(context_matches.experiencier.name),
                              section, match.start(), match.end())
        if (len(temporality_filters) == 0 or term.temporality in temporality_filters) and \
            (len(experiencer_filters) == 0 or term.experiencer in experiencer_filters) and \
                (len(negex_filters) == 0 or term.negex in negex_filters):
            matches.append(term)

    return matches


def get_full_text_matches(matchers, text: str, filters={}):
    found_terms = list()
    section_headers, section_texts = [UNKNOWN], [text]
    try:
        section_headers, section_texts = sec_tag_process(text)
    except Exception as e:
        print(e)
    for idx in range(0, len(section_headers)):
        section_text = section_texts[idx]
        sentences = segmentor.parse_sentences(section_text)
        # section_code = ".".join([str(i) for i in section_headers[idx].treecode_list])

        list_product = itertools.product(matchers, sentences)
        for l in list_product:
            found = get_matches(l[0], l[1], section_headers[idx].concept, filters)
            if found:
                found_terms.extend(found)
    return found_terms


class TermFinder(BaseModel):

    def __init__(self, match_terms,  include_synonyms=True,
                 include_descendants=False, include_ancestors=False,
                 vocabulary='SNOMED'):
        self.terms = match_terms
        self.matchers = []
        added = []
        if include_synonyms or include_descendants or include_ancestors:
            for term in self.terms:
                added.extend(get_related_terms(util.conn_string, term, vocabulary, include_synonyms,
                                               include_descendants, include_ancestors))
        # if len(added) > 0:
        #     print("added the following terms through vocab expansion %s" % str(added))
            self.terms.extend(added)
        # print("all terms to find %s" % str(self.terms))
        self.matchers = [re.compile(r"\b%s\b" % t, re.IGNORECASE) for t in self.terms]

    def get_term_matches(self, sentence: str, section='UNKNOWN'):
        term_matches = list()
        for m in self.matchers:
            cur = get_matches(m, sentence, section)
            term_matches.extend(cur)
        return term_matches

    def get_term_full_text_matches(self, txt: str, filters={}):
        return get_full_text_matches(self.matchers, txt, filters)


if __name__ == "__main__":
    stf = TermFinder(["heart", "cardiovascular"])
    terms = stf.get_term_matches("there is a heart in the cardiovascular system", "UNKNOWN")
    txt = "Admitting Diagnosis: CEREBRAL BLEED\n  REASON FOR THIS EXAMINATION:\n  assess for chf\n \n FINAL REPORT\n HX:  Trauma. SOB - assess for CHF. \n\n SUPINE AP CHEST AT 6:18 AM:  Given the supine examination performed at the\n bedside, the cardiovascular status is difficult to assess.  The heart and\n mediastinum is unchanged in appearance from the study one day ago. Bibasilar\n opacities, which may reflect atelectasis, are unchanged.  There are diffuse\n interstitial markings as described on the prior study, also unchanged.\n\n IMPRESSION: Allowing for technical differences, there is little change since\n the study of one day ago.  The cardiovascular status of the patient is\n difficult to assess."
    full_terms = stf.get_term_full_text_matches(txt)
    print(full_terms)
