#!/usr/bin/evn python3
"""
Module for finding an individual's sexual orientation.
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
    

# sexual orientation types
SEXUAL_ORIENTATION_HETEROSEXUAL = 'heterosexual'
SEXUAL_ORIENTATION_HOMOSEXUAL   = 'homosexual'
SEXUAL_ORIENTATION_BISEXUAL     = 'bisexual'
SEXUAL_ORIENTATION_ASEXUAL      = 'asexual'

SEXUAL_ORIENTATION_FIELDS = [
    'sentence',
    'sexual_orientation'  # one of the constants above
]

SexualOrientationTuple = namedtuple('SexualOrientationTuple', SEXUAL_ORIENTATION_FIELDS)
SexualOrientationTuple.__new__.__defaults__ = (None,) * len(SexualOrientationTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = False

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\s?(' + _str_word + r'){0,5}?'

# sexual orientation - insert all entries into _normalization_map below
_str_orientation = r'\b(?P<orientation>(gay|lesbian|queer|(homo|hetero|bi|a)sexual))(?! friend)\b'
_regex_orientation = re.compile(_str_orientation, re.IGNORECASE)

# all orientations recognized by this regex go in this map
_normalization_map = {
    'gay'          : SEXUAL_ORIENTATION_HOMOSEXUAL,
    'lesbian'      : SEXUAL_ORIENTATION_HOMOSEXUAL,
    'queer'        : SEXUAL_ORIENTATION_HOMOSEXUAL,
    'homosexual'   : SEXUAL_ORIENTATION_HOMOSEXUAL,
    'heterosexual' : SEXUAL_ORIENTATION_HETEROSEXUAL,
    'bisexual'     : SEXUAL_ORIENTATION_BISEXUAL,
    'asexual'      : SEXUAL_ORIENTATION_ASEXUAL,
}

_str_identifies_as = r'\b((self[-\s])?identifies( (him|her)self)?|(came|coming) out) as\b' + _str_words + _str_orientation
_regex_identifies_as = re.compile(_str_identifies_as, re.IGNORECASE)

# Other: heterosexual
_str_header = r'\b(history of present illness|social history|underlying medical condition|other)\s?[-:]'
_str1 = _str_header + r'(\s?\d\d?)?' + _str_words + _str_orientation
_regex1 = re.compile(_str1, re.IGNORECASE)

# reports being gay
_str2 = r'\b(?<!not )(?<!denies )(being|is(?! not)|as)\b' + _str_words + _str_orientation
_regex2 = re.compile(_str2, re.IGNORECASE)

# heterosexual partner
_str3 = _str_orientation + _str_words + r'\b(partner|intercourse|sex)\b'
_regex3 = re.compile(_str3, re.IGNORECASE)

# relationship
_str4 = r'\b(?<!not )in( a)?' + _str_words + _str_orientation + r' relationship\b'
_regex4 = re.compile(_str4, re.IGNORECASE)

# 33 year old homosexual male
_str5 = r'\b\d\d? ' + _str_words + _str_orientation + r' ((fe)?male|(wo)?man)\b'
_regex5 = re.compile(_str5, re.IGNORECASE)

# risk factors
_str6 = r'\brisky? (behaviors?|factors?)[-:\s]+' + _str_words + _str_orientation
_regex6 = re.compile(_str6, re.IGNORECASE)

# homosexual orientation
_str7 = _str_orientation + _str_words + r'\b(orientation|prostitution)\b'
_regex7 = re.compile(_str7, re.IGNORECASE)

_REGEXES = [
    _regex_identifies_as,
    _regex1,
    _regex2,
    _regex3,
    _regex4,
    _regex5,
    _regex6,
    _regex7,
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

    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)

    # replace ' @ ' with ' at '
    sentence = re.sub(r'\s@\s', ' at ', sentence)

    # replace "->" with whitespace
    sentence = re.sub(r'\->', _CHAR_SPACE, sentence)

    # erase commas and apostrophes
    sentence = re.sub(r'[,\'`]', '', sentence)

    # replace other chars with whitespace
    sentence = re.sub(r'[-&(){}\[\]~/;]', _CHAR_SPACE, sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', _CHAR_SPACE, sentence)

    return sentence


###############################################################################
def _process_match(match, regex):

    # strip any trailing whitespace (invalidates match.end())
    match_text = match.group().rstrip()
    start = match.start()
    end = start + len(match_text)
    orientation = match.group('orientation')
    
    if _TRACE:
        DISPLAY('\t' + match_text)
        DISPLAY('\t' + orientation)

    # normalize
    if orientation in _normalization_map:
        normalized_orientation = _normalization_map[orientation]
    else:
        DISPLAY('*** sexual_orientation_finder: orientation "{0}" not in map ***'.format(orientation))
        normalized_orientation = orientation

    candidate = overlap.Candidate(start, end, match_text, regex, other=normalized_orientation)
    return candidate


###############################################################################
def _regex_match(sentence, regex_list):
    """
    """

    candidates = []
    for i, regex in enumerate(regex_list):
        iterator = regex.finditer(sentence)
        for match in iterator:
            candidate = _process_match(match, regex)
            candidates.append(candidate)

    # sort candidates in DECREASING order of length
    candidates = sorted(candidates, key=lambda x: x.end-x.start)

    if _TRACE:
        DISPLAY('\tCandidate matches: ')
        index = 0
        for c in candidates:
            regex_index = regex_list.index(c.regex)
            DISPLAY('\t[{0:2}] R{1:2}\t[{2},{3}): ->{4}<-'.
                  format(index, regex_index, c.start, c.end, c.match_text))
            index += 1
        DISPLAY()

    # keep the longest of any overlapping matches
    pruned_candidates = overlap.remove_overlap(candidates,
                                               False,
                                               keep_longest=True)

    if _TRACE:
        DISPLAY('\tCandidate matches after overlap resolution: ')
        index = 0
        for c in pruned_candidates:
            regex_index = regex_list.index(c.regex)
            DISPLAY('\t[{0:2}] R{1:2}\t[{2},{3}): ->{4}<-'.
                  format(index, regex_index, c.start, c.end, c.match_text))
            index += 1
        DISPLAY()
    
    return pruned_candidates    


###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        DISPLAY(cleaned_sentence)

    candidates = _regex_match(cleaned_sentence, _REGEXES)

    for c in candidates:
        orientation = c.other

        obj = SexualOrientationTuple(
            sentence = cleaned_sentence,
            sexual_orientation = orientation
        )

        results.append(obj)

    return json.dumps([r._asdict() for r in results], indent=4)    
    

###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    SENTENCES = [

        # bisexual
        'now he identifies as bisexual but has a preference for male relationships',
        'Other: bisexual, unmarried',
        'Not sexually active, is bisexual.',
        'The patient reports being bisexual but monogamous for over one year',
        'He recently came out as bisexual to his wife.',
        'Not sexually active now, bisexual, questionable adherence to protection.',

        # homosexual / gay / lesbian
        'that there is a degree of guilt about being gay and having contracted HIV',
        'searching for justification/support that would validate him being a gay man',
        'MOTHER STILL UNAWARE OF PT HIV STATUS AND BEING GAY.',
        'pt is a 30 year old Hispanic gay man who was admitted last night',
        'his not going to gym class (being gay, he feared that)',
        'Patient / Family Assessment: This 50 y/o SW gay male has been HIV infected',
        'Patient / Family Assessment: This 44 y/o SW gay male has made four suicide attempts',
        'Other: Gay male',
        'Other: Homosexual',
        'Social History: gay male and he has at this time a monogamous partner',
        "Family is not to know of pt's hiv status and that pt is gay.",
        "Father from [**Country **] who hasn't seen him in 10 years and does not know that he is gay",
        'reactions to learning that he is gay',
        'family reports that pt is gay but not currently in a romantic relationship',
        'Self-identifies as gay',
        'Patients wife stated they do not have a sexual relationship as patient is gay',

        'UNDERLYING MEDICAL CONDITION: 62 year homosexual male, unknown HIV status',
        'HISTORY OF PRESENT ILLNESS: The patient is a 33 year old homosexual male',
        'Social History: homosexual, has boyfriend',
        'Social History: BU student Homosexual (family not aware)',
        'Social History: Homosexual male who lives in [**Location 3564**]',
        'Mr. [**Known patient lastname 662**] is a homosexual male with 16 year hx. of HIV',
        'He is in a monogamous homosexual relationship.'
        'PT IS HOMOSEXUAL WHO WORKS AS A SOCIAL WORKER FOR HIV/AIDS PT',
        'he is homosexual',
        'he is a homosexual in a monogamous relationship',
        'he reports being homosexual',
        'the patient states that he is a homosexual',
        'Homosexual orientation with a negative human immunodeficiency virus test',
        'h/o homosexual prostitution to obtain drugs',
        'He identifies himself as a homosexual male',
        'RISKY BEHAVIOR -- unprotected homosexual relations',
        'In committed homosexual relationship for 20 years',
        'self-identifies as gay',

        'When coming out as a lesbian he was criticized',
        'She is in a supportive lesbian relationship currently',
        'she is in a lesbian relationship and she lives with her partner',
        'The patient reports her sexual orientation as being a lesbian but not currently sexually active',
        'identifies as a lesbian and recently split from her partner',

        # heterosexual
        'Other: heterosexual, condom use',
        'SOCIAL HISTORY: heterosexual',
        'Contracted HIV from intravenous drug abusing heterosexual partner',
        'He is heterosexual.',
        'the patient is heterosexual and is in a monogamous relationship',
        'He is sexually active and is heterosexual with one lifetime partner, which is his wife',
        'She has been in a monogamous, heterosexual relationship for the past 10 months.',
        'presumably secondary to heterosexual sex with wife',
        'No children. Not married. Heterosexual.',
        'Risk factor, heterosexual sex.',
        'presumably contracted via heterosexual intercourse',
        'stable heterosexual partner, lives with daughter',
        'risk factors included unprotected heterosexual sex as well as drug use',

        # asexual
        'She would describe her sexual orientation as asexual',
        
        # negative
        # BenGay ointment
        '[**Doctor First Name **] gay ordered and applied to pts neck',
        '[**Doctor First Name 466**]-GAY WITH GOOD EFFECT',
        # gay marriage
        'he and his partner do not believe in gay marriage',
        # gay friend
        'partner very involved as well as the father of the baby which is a gay friend of the family',
        # gay and lesbian
        'provided her with information re Gay and Lesbian Advocates',
        # not a lesbian relationship
        'she reports that this was not a lesbian relationship',
        # used to be
        'He has many relationships and used to be bisexual.',
    ]

    for sentence in SENTENCES:
        DISPLAY('\n' + sentence)
        json_result = run(sentence)
        json_data = json.loads(json_result)
        result_list = [SexualOrientationTuple(**d) for d in json_data]
        for r in result_list:
            DISPLAY('\t{0}'.format(r))
    
