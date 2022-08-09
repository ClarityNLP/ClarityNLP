#!/usr/bin/evn python3
"""
Module for finding mentions of mental illness.
"""

import os
import re
import sys
import json
from collections import namedtuple

if __name__ == '__main__':
    # interactive testing
    match = re.search(r'nlp/', sys.path[0])
    if match:
        nlp_dir = sys.path[0][:match.end()]
        sys.path.append(nlp_dir)
    else:
        path, module_name = os.path.split(__file__)
        print('\n*** {0}: nlp dir not found ***\n'.format(module_name))
        sys.exit(0)
    
try:
    # interactive path
    import finder_overlap as overlap
    DISPLAY = print
except:
    # ClarityNLP path
    from claritynlp_logging import log, ERROR, DEBUG
    DISPLAY = log
    from algorithms.finder import finder_overlap as overlap

    
MENTAL_ILLNESS_FIELDS = [
    'sentence',
    'mental_illness'
]

MentalIllnessTuple = namedtuple('MentalIllnessTuple', MENTAL_ILLNESS_FIELDS)
MentalIllnessTuple.__new__.__defaults__ = (None,) * len(MentalIllnessTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = True

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\s?(' + _str_word + r'){0,5}?'

_str_mi = r'\bmental illness( diagnosis)?'

# history of mental illness
_str_history = r'\b((history|setting) of|struggl(ing|e[sd]?) with)'
#diagnos(is|ed)|known|have|has) '
_str_history =  _str_history + _str_words + _str_mi
_regex_history = re.compile(_str_history, re.IGNORECASE)

_str_diagnosis = r'\b(diagnos(is|ed)|chronic|known|have|has)' + _str_words + _str_mi
_regex_diagnosis = re.compile(_str_diagnosis, re.IGNORECASE)

# her mental illness
_str_her_mi = r'\b(patients|their|his|her)\b' + _str_words + _str_mi
_regex_her_mi = re.compile(_str_her_mi, re.IGNORECASE)

# Past Medical History: "Mental Illness"
_str_pmhx = r'\b(Past Medical History|pmhx):' + _str_words + _str_mi
_regex_pmhx = re.compile(_str_pmhx, re.IGNORECASE)

# negations
_str_neg = r'\b(denies|not|no( (evidence|mention))?)'
_regex_neg = re.compile(_str_neg, re.IGNORECASE)


_REGEXES = [
    _regex_history,
    _regex_diagnosis,
    _regex_her_mi,
    _regex_pmhx,
]

_CHAR_SPACE = ' '


###############################################################################
def _cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # convert to lowercase
    sentence = sentence.lower()

    # replace MIMIC [** ... **] anonymizations with whitespace
    sentence = re.sub(r'\[\*\*[^\]]+\]', _CHAR_SPACE, sentence)    

    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/', ' with ', sentence)

    # replace 'hx' with ' history '
    sentence = re.sub(r'\bhx\.?\b', ' history ', sentence)

    # replace 'dx' with diagnosis
    sentence = re.sub(r'\bdx\.?\b', ' diagnosis ', sentence)

    # replace 'sx' with significant
    sentence = re.sub(r'\bsx\.?', ' significant ', sentence)

    # replace "pt's" with 'patients' (no apostrophe)
    sentence = re.sub(r"\bpt\'?s", ' patients ', sentence)

    # replace 'pt' with 'patient
    sentence = re.sub(r'\bpt\b', ' patient ', sentence)

    # replace ' @ ' with ' at '
    sentence = re.sub(r'\s@\s', ' at ', sentence)

    # replace "->" with whitespace
    sentence = re.sub(r'\->', _CHAR_SPACE, sentence)

    # erase commas and apostrophes
    sentence = re.sub(r'[,\'`]', '', sentence)

    # replace other chars with whitespace
    sentence = re.sub(r'[-&(){}\[\]~/;"]', _CHAR_SPACE, sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', _CHAR_SPACE, sentence)

    sentence = sentence.strip()

    return sentence


###############################################################################
def _regex_match(sentence, regex_list):
    """
    """

    candidates = []
    for i, regex in enumerate(regex_list):
        iterator = regex.finditer(sentence)
        for match in iterator:
            # strip any trailing whitespace (invalidates match.end())
            match_text = match.group().rstrip()
            start = match.start()
            end = start + len(match_text)

            # check for negations *prior* to the match
            prior = sentence[:start]
            neg_match = _regex_neg.search(prior)
            if neg_match:
                continue
            
            if _TRACE:
                DISPLAY('\t' + match_text)


###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        DISPLAY(cleaned_sentence)

    candidates = _regex_match(cleaned_sentence, _REGEXES)

    # for c in candidates:
    #     immigration_status = c.other

    #     obj = ImmigrationTuple(
    #         sentence = cleaned_sentence,
    #         immigration_status = immigration_status
    #     )

    #     results.append(obj)

    # return json.dumps([r._asdict() for r in results], indent=4)


###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':
    
    SENTENCES = [
        'significant history of chronic pain and mental illness',
        'she has had a history of mental illness that went away at the onset of menopause',
        'struggling with mental illness',
        'Mother fearful that pt may not be taken seriously secondary to her mental illness dx',
        'Family recounts that pt has history of mental illness with one significant suicide attempt.',
        "Confused, poorly tracks thoughts, ?pt's baseline given hx of mental illness.",
        'She believes that pt lives on the street and has a history of mental illness ' \
        'although she is not sure of the specifics',
        "They located a suicide note that pt left and are appropriately tearful when " \
        "talking about pt's struggle with mental illness.",
        'Pt is nervous and has a history of mental illness',
        'likely complicated by his mental illness',
        'Pt with a lengthy history of alcohol abuse in the setting of mental illness.',
        'history of increasing agitation in setting of known mental illness',
        'history of chronic pain and mental illness',
        "Concerned re: severity of patient's mental illness/inability to receive meds",
        'he has poor insight into his own mental illness',
        'Pt w/ hx of mental illness and ETOH abuse', 
        'Pt has history of mental illness, ? diagnosis',
        '[**Name (NI) 5892**] is known to have a mental illness and he does not take his medication',
        'He is divorced, his ex wife also has mental illness',
        'chronic mental illness, limited social supports',
        'PMHx:   \"mental illness\" - on disability',
        'PAST MEDICAL HISTORY: -\"mental illness\"',
        'because of her history of malignancy and significant mental illness',
        'has major mental illness which is currently untreated',
        
        # # possible mental illness
        # 'There is also possibly a component of mental illness',
        # 'Pt states that there is a family hx of mental illness',
        # 'Social History: ? mental illness',
        
        # # somebody else
        # 'biggest concern was contacting his brother who is currently in CA and has ' \
        # 'recently been dx with some form of mental illness',
        # 'Daughter expresses concern that pts son, who has mental illness, may become agitated ',
        # 'DAUGHTER W/HX MENTAL ILLNESS PER HER HUSBAND',
        # 'for people with mental illness',
        # 'he patient was born and raised in [**Location (un) 86**] to parents who both had mental illness',
        # "son has hx of untreated mental illness, and cannot adequately provide for pt's needs",

        # negated
        'He was evaluated by psychiatry who did not feel that he had a mental illness',
        'and has not been found to have sx. major depression or other mental illness',
        'Yet there is no mention in Ms. [**Known patient lastname 9259**]s chart about any mental illness',
        'she has not been found to have a major mental illness incl. major depression, bipolar disorder or psychosis',
        'Patient denies family medical history of mental illness',
        'A psychiatric evaluation was performed, there was no evidence of mental illness ' \
        'other than severe alcohol dependence',
    ]
    
    
    for sentence in SENTENCES:
        DISPLAY('\n' + sentence)
        run(sentence)
