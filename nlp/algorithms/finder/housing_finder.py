#!/usr/bin/env python3
"""

Module for finding a patient's housing status.

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


HOUSING_TUPLE_FIELDS = [
    'sentence',
    'housing',   # type of housing
]

HousingTuple = namedtuple('HousingTuple', HOUSING_TUPLE_FIELDS)

# set default value of all fields to None
HousingTuple.__new__.__defaults__ = (None,) * len(HousingTuple._fields)
    

###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = False

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\b\s?(' + _str_word + r'){0,5}?'

_str_age = r'\b\d+\s?(year old|yrs?\.?|y[ /]?o(ld)?)\b'
_str_person = r'\b((fe)?male|(wo)?man|patient|pt\.?|person|individual|citizen|vet(eran)?|vagrant|[MW])\b'

_str_homeless1 = _str_age + _str_words + r'\bhomeless' + _str_words + _str_person
_regex_homeless1 = re.compile(_str_homeless1, re.IGNORECASE)

_str_homeless2 = r'\bhomeless\b' + _str_words + _str_age
_regex_homeless2 = re.compile(_str_homeless2, re.IGNORECASE)

_str_homeless3 = r'\bs?he' + _str_words + r'\bhomeless( shelter)?\b'
_regex_homeless3 = re.compile(_str_homeless3, re.IGNORECASE)

_str_homeless4 = _str_person + _str_words + r'\bhomeless\b'
_regex_homeless4 = re.compile(_str_homeless4, re.IGNORECASE)

_regex_homeless5 = re.compile(r'\bhomeless\b', re.IGNORECASE)

_GROUP_HOUSING = 'housing'
_str_housing = r'\b(?P<housing>(shelter|((halfway|sober) )?house|(group|communal) home|apartment|room|app?t\.?))\b'

_str_shelter1 = r'\b(resides|resident of|place(d|ment)|liv(ing|es)|renting|is)\b' + _str_words + _str_housing
_regex_shelter1 = re.compile(_str_shelter1, re.IGNORECASE)

_str_shelter2 = r'\b(assigned|admit(ted)?|discharged?|transfer(red)?|return(ed)?|necessary|needs|expects) ((back )?to|a)\b' + _str_words + _str_housing
_regex_shelter2 = re.compile(_str_shelter2, re.IGNORECASE)

#_str_shelter3 = r'\bat\b' + _str_words + _str_housing
#_regex_shelter3 = re.compile(_str_shelter3, re.IGNORECASE)

# pt lives alone in <housing>
_str_lives_alone_in = r'\blives alone in\b' + _str_words + _str_housing
_regex_lives_alone_in = re.compile(_str_lives_alone_in, re.IGNORECASE)

_HOMELESS_REGEXES = [
    _regex_homeless1,
    _regex_homeless2,
    _regex_homeless3,
    _regex_homeless4,
    _regex_homeless5,
]

_SHELTER_REGEXES = [
    _regex_shelter1,
    _regex_shelter2,
    #_regex_shelter3,
    _regex_lives_alone_in,
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

    # replace "d/c" with " discharge "
    sentence = re.sub(r'\bd/c\b', ' discharge ', sentence)

    # erase commas, apostrophes, and quotation marks
    sentence = re.sub(r'[,\'`\\""]', '', sentence)

    # replace other chars with whitespace
    sentence = re.sub(r'[-&(){}\[\]:~/;]', _CHAR_SPACE, sentence)

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

            #DISPLAY('\t{0}'.format(match_text))
            housing = None
            if _GROUP_HOUSING in match.groupdict():
                housing = match.group(_GROUP_HOUSING)
            
            candidates.append(overlap.Candidate(
               start, end, match_text, regex, other=housing
            ))

    # sort the candidates in DECREASING order of length
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

    candidates = _regex_match(cleaned_sentence, _HOMELESS_REGEXES)
    if len(candidates) > 0:
        obj = HousingTuple(
            sentence = cleaned_sentence,
            housing = 'homeless'
        )

        results.append(obj)
    else:
        # not homeless, so check for housing
        candidates = _regex_match(cleaned_sentence, _SHELTER_REGEXES)
        for c in candidates:
            assert c.other is not None
            housing = c.other

            if housing.startswith('apt') or housing.startswith('appt'):
                housing = 'apartment'

            obj = HousingTuple(
                sentence = cleaned_sentence,
                housing = housing
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
        # homeless
        'reports he has been homeless this time for about a year',
        'Per pt he is homeless and lives in [**Location **]',
        '45 yo homeless man, found intoxicated',
        '68-year-old male with increasing seizure, homeless',
        'Pt is known to be homeless',
        'This is a homeless 61 year old male',
        '54y/o homeless M with h/o HTN and ETOH abuse',
        'PMHx: homeless, ETOH abuse, biporlar disorder',
        '57 year old homeless man with CHF, afib, found unresponsive, now intubated',
        'Pt stated that he is homeless, usually living on streets',
        'she currently resides in homeless shelter',
        'Mom tearful and verbalized that she is homeless and making plans to find shelter',
        'PMHX: homeless',

        # shelter
        'possible TB exposure in shelter',
        'mom resides in shelter in [**Hospital1 2000**]',
        'Pt is a 32 year old divorced African-American woman who is living in a \"scattered site\" shelter',
        'recommended that mother apply for a \"Scattered Site Shelter\" which would provide her with her own apt vs living in the more typical family group home shelter',
        'mother is in shelter',
        'Social services in to arrange discharge to safe   shelter',
        'info necessary to find a shelter when discharged',
        'Mom repeated that she expects to be in a shelter by Saturday',
        'will return to the shelter in [**Location (un) 2334**] where she has been living',
        'assigned a room in a famly shelter',
        'she expects to be in a shelter by Saturday',
        'she is currently residing in a shelter that does not accomodate newborns',
        'Mom to meet with DTA housing worker tomorrow to initiate process for placement in shelter',        
        
        # halfway house
        'plan to d/c to halfway house',
        'she will not be accepted back to her halfway house due to pt continuing to OD',
        'found unresponsive at halfway house',
        'paranoid, thinks people are trying to harm her at her halfway house',
        'most likely will be transferred back to halfway house',
        'she lives in a multiple family house',

        'he is living in a group home',
        'note pt lives alone in an apartment at house a subsidized independent living building for seniors',
        
        # renting
        'Now renting a room   with friends',
        'They are renting appt in [**Location (un) 24**] at least into [**Month (only) **]',
        
    ]

    for sentence in SENTENCES:
        DISPLAY('\n' + sentence)
        json_result = run(sentence)
        json_data = json.loads(json_result)
        result_list = [HousingTuple(**d) for d in json_data]
        for r in result_list:
            DISPLAY('\t{0}'.format(r))
    
    
    # DTA = Department of Transitional Assistance
    # DHCD = Department of Housing and Community Development

    # avoid matching on:
    #       incarcerated (bowel|<wds> + hernia)
    
    """
    'mom now relying on family for housing',
    'mom to go to DTA office tomorrow for housing needs',
    'trying to facilitate housing for family',
    'talked about housing options in this area',
    'dad reports housing concerns to be his greatest worry at the moment',
    'it is unlikely that housing will be secured by month's end',
    'DTA will help mother access temporary housing',
    'mother could then remain there until permanent housing became available',
    'looking for alternative, less expensive housing',
    'a social worker who is assisting her with housing',
    'until she secures permanent housing',
    'pt has modest income, and has had unstable housing for nearly 3 years',
    'her goal is to get her own apartment',
    'mom to contact DTA worker today',
    'have arranged for them to meet with Community Resource Specialist [**First Name8 (NamePattern2) 1820**] [**Last Name (NamePattern1) 1706**] who will discuss various housing possibilities with them',

    'housing situation is unclear',
    'father expressed need for housing as they currently live in 1 bdrm apt',
    'mom must go to DTA office in order to be placed in shelter today',
    'mother says she may have found residential housing',
    'mother is living in one room of 4-bedroom apt.',
    'plan for discharge early so mom can arrange housing',
    'met with her yesterday to compete more applications for Sec.8 housing',
    'pt's wife continues search for new housing',
    'Housing Authority waived rent for [**Month (only) 1121**] as pt  is on section 8',
    'housing case worker',
    'speak with pt. and provide her with temporary housing resources',
    '72 year old female from senior housing found lethargic',
    'investigated possibilities for temporary housing with nothing available for several days',
    'did not notify any one of his hospitalization until he returned to his   home',
    'She plans to live with her parents until an apt becomes available thru subsidized housing.',
    'Mother is interested in going into a family shelter as she has no other viable housing options',
        
    """
