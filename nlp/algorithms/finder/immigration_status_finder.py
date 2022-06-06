#!/usr/bin/evn python3
"""
Module for finding someone's immigration status.
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
    

    

# US immigration status types
# (see https://lawyersimmigration.com/four-types-immigration-statuses/)
IMMIGRATION_STATUS_US_CITIZEN    = 'US Citizen'
IMMIGRATION_STATUS_US_RESIDENT   = 'US Resident'   # conditional and permanent residents (green card holders)
IMMIGRATION_STATUS_NON_IMMIGRANT = 'Non-Immigrant' # students, tourists, temp workers, other visa holders
IMMIGRATION_STATUS_UNDOCUMENTED  = 'Undocuented'
    
IMMIGRATION_TUPLE_FIELDS = [
    'sentence',
    'immigration_status' # one of the constants above
]

ImmigrationTuple = namedtuple('ImmigrationTuple', IMMIGRATION_TUPLE_FIELDS)
ImmigrationTuple.__new__.__defaults__ = (None,) * len(ImmigrationTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = True

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\s?(' + _str_word + r'){0,5}?'

# undocumented
_str_undocumented = r'\b(?P<undocumented>(illegal|undocumented|not a documented) (immigrant|alien|citizen))\b'
_regex_undocumented = re.compile(_str_undocumented, re.IGNORECASE)

# immigrant
_str_immigrant = r'\b(?P<immigrant>immigrant( from)?)\b'
_regex_immigrant = re.compile(_str_immigrant, re.IGNORECASE)

# US citizen
_str_us_citizen = r'\b(?<!not a )(is a )?(?P<uscitizen>us citizen)\b'
_regex_us_citizen = re.compile(_str_us_citizen, re.IGNORECASE)

# permanent resident
_str_perm_res1 = r'\b(?P<permres>(permanent|legal) resident of the US)\b'
_regex_perm_res1 = re.compile(_str_perm_res1, re.IGNORECASE)

_str_perm_res2 = r'\b(?<!not a )(with|has )?(?P<permres>us ((permanent|legal) resident|residency))\b'
_regex_perm_res2 = re.compile(_str_perm_res2, re.IGNORECASE)

# visa extension
_str_extend_visa1 = r'\bexten(d|sion)\b' + _str_words + r'\b(?P<visa>visa)\b'
_regex_extend_visa1 = re.compile(_str_extend_visa1, re.IGNORECASE)

_str_extend_visa2 = r'\b(?P<visa>visa)\b' + _str_words + r'\bexten(d|sion)\b'
_regex_extend_visa2 = re.compile(_str_extend_visa2, re.IGNORECASE)

_str_work_visa = r'(?P<visa>(\bvisa\b' + _str_words + r'\bwork(ers?)?\b)|(\bwork(ers?)?\b' + _str_words + r'\bvisa\b))'
_regex_work_visa = re.compile(_str_work_visa, re.IGNORECASE)

_str_visiting = r'(?P<visa>\b(visit(ing|or)?|tourist)\b' + _str_words + r'\bfrom)\b'
_regex_visiting = re.compile(_str_visiting, re.IGNORECASE)

_str_visa_days = r'\b(?P<visa>\d+ day visa)\b'
_regex_visa_days = re.compile(_str_visa_days, re.IGNORECASE)

_REGEXES = [
    _regex_undocumented,
    _regex_immigrant,
    _regex_perm_res1,
    _regex_perm_res2,

    _regex_extend_visa1,
    _regex_extend_visa2,
    _regex_work_visa,
    _regex_visiting,
    _regex_visa_days,
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

            print('\t' + match_text)
            

###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        DISPLAY(cleaned_sentence)

    candidates = _regex_match(cleaned_sentence, _REGEXES)


###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    SENTENCES = [
        
        # undocumented immigrant
        'Pt is from [**Country **], illegal immigrant, social work following.',
        'Pt is   undocumented immigrant, not eligible for Mass Health.',
        'SOCIAL:   PT IS AN ILLEGAL IMMIGRANT',
        'Pt reports he is an undocumented immigrant, originally from [**Country **].',
        'Social History: riginally from [**Country 3537**], is not a documented citizen',        
        
        # immigrant
        '45 year old man with DOE, blood tinged sputum.  immigrant from [**Country **]',
        'Mo. is a 23 y.o. sp-spking [**Known patient lastname 5241**] immigrant x 5 yrs. who lives w/ partner',
        'is the child of 20 y.o. sp-spking Guat. immigrant mo. who is currently s/p c/s, homeless',
        'Other: Jamaican immigrant',
        '20 YO PORTUGUESE SPEAKING BRAZILIAN IMMIGRANT ADMITTED TO HOSPITAL',
        'Social History: Russian immigrant',
        'Social History: Immigrant from [**Country 7824**]',
        'SOCIAL HISTORY:  The patient is a Russian immigrant, he is English speaking.',
        
        # not a US citizen
        'she is not a US citizen',
        'pt is not a US citizen',
        'Lives with his wife in a senior citizen center',
        'Other: lives in a senior citizen center',
        'lives alone in senior citizen   housing',
        'the patient is not a US citizen (Canadian)',
        'Social History: Divorced and lives alone in a senior citizen building',
        "SOCIAL HISTORY:  Lives by herself in a senior citizen's home.",        
        'doing senior citizen work',
        'She lives in a senior citizen center',
        'She is widowed, lives in senior citizen housing',
        'Social History: Pt lives as Winter Valley Senior Citizen Living',
        'Retired, lives in senior citizen apartment complex because of permanent disability',
        'SOCIAL HISTORY: Is that she lives in a Senior Citizen home',
        'Social History: Lives with husband in senior citizen complex',

        # US citizen or not
        'He has been in the U.S. for 23 years and is a citizen',        
        'Pt is an Indian citizen with US residency and lives here with nephew',
        'lives in Montreal, Canadian citizen, 3 children who live in the area',
        'The patient is a 24-year-old male, Irish citizen',
        'Social History: Pt is a Chinese citizen',
        'the patient is not a United States citizen or [**State **] resident',
        'Social History: The patient is originally from [**Country 9273**], immigrated [**3327**], now US citizen.',
        "given the patient's current status as a non US citizen",
        'She is currently not a legal citizen of the United States',

        # permanent resident (most negative)
        'HE is a permanent resident at [**Hospital1 605**]',
        'SOCIAL HISTORY:  The patient is a permanent resident at the [**Hospital3 8956**].',
        'The patient is to be discharged back to [**Hospital3 8956**] where she is a permanent resident.',
        'Other: Permanent resident of [**Hospital3 2716**] Manor',
        'This 83 year old woman with paranoid schizophrenia and permanent resident ' \
        'of the [**Hospital1 13136**] Nursing Health Center',
        'pt has been a permanent resident of the US since 2014',
        'Pt is an Indian citizen with US residency and lives here with nephew',
        
        # # green card or not
        # 'pt may be denied green card if dx known',
        # 'pt may be denied a Green Card upon receiving the diagnosis of schizophrenia',        
        # 'PT OFFERING TO SHOW HER GREEN CARD SO SHE COULD GO HOME',
        # 'she won a lottery for a Green Card',
        # 'required to get green card   from Kenyan embassy',
        # 'Pt fears that she was using him for a green card, as her behavior changed dramatically when she came to the US',

        # visa
        'an application to extend her visa',
        'will asssit with letter requesting extension of visa',
        'she has a visa to work in USa valid until',
        'pt has a temporary worker visa',
        'She is visiting here from   the [**Country 1168**] Republic',
        'he is a tourist from China',
        'this will enable her to stay for an additional x 30 day visa',
        
        # 'is unsure if he will be able to obtain a visa',
        # 'LETTER FOR FAMILY MEMBER GIVEN FOR VISA FROM [**Location (un) 5841**] AND TOBEGO',
        # 'British Mom with temporary Visa negotiating the maze of discharge planning',
        # 'SW will prepare letter requesting visa for MD signature',
        # 'SW consult for family regarding obtaining an   emergency visa for pt daughters',

        # # refugee
        # 'immigrated to the United States in [**3417**] as a refugee from   [**Country 287**]',
        # 'Pt is a Ukrainian refugee who immigrated to the US in [**3185**]',
        
        # # negative
        # 'R pupil greater than L at times visa versa, both reactive',
        # 'ESRD on HD, recent VISA bacteremia who has been intermittently CMO',
        # 'Formerly worked for the federal government as the Director of Refugee Resettlement',
        # 'They lived in a refugee camp until [**2629**] when they left for the [**Country 3118**] for 3 months',
    ]

    for sentence in SENTENCES:
        DISPLAY('\n' + sentence)
        run(sentence)

