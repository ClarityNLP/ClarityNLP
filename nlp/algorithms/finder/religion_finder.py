#!/usr/bin/env python3
"""

Module for finding a patient's primary language.

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


RELIGION_TUPLE_FIELDS = [
    'sentence',
    'religion',
]

ReligionTuple = namedtuple('ReligionTuple', RELIGION_TUPLE_FIELDS)

# set default value of all fields to None
ReligionTuple.__new__.__defaults__ = (None,) * len(ReligionTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = False

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\s?(' + _str_word + r'){0,5}?'


_str_religions = r'\b(?<!\bspeaks )(?P<religion>(j(e|o)hovah?s? witness|pentecostal|buddh?ist|catholic|' +\
    r'jew(ish|daism)?|muslim|islam|mormon|hindu|lds(?! dimished bases)|christian(ity)?))\b' +\
    r'(?! (speaking|speaker))'

_str_header = r'\b(religion|social( history)?|other)\s?[:= ]?'

# contains some non-person entries also, since these give clues about the religion
_str_who = r'\b(patient|pt\.?|parents|clergy|rabb?i|minister|priest|reverend|preacher|monk|' +\
    r'they|family|mother|father|mom|dad|she|he|holy person|imam|temple|synagogue|traditions)\b'

_str_practices = r'\b(are|is|were|was|bec(oming|ame)|convert(ed)?|practic(ing|es))\b'

_str_official = r'\b(imam|rabb?i)\b'
_regex_official = re.compile(_str_official, re.IGNORECASE)

_str_religion1 = _str_header + _str_words + _str_religions
_regex_religion1 = re.compile(_str_religion1, re.IGNORECASE)

_str_religion2 = _str_religions + _str_words + r'\b(religio(us|n)|faith)\b'
_regex_religion2 = re.compile(_str_religion2, re.IGNORECASE)

_str_religion3 = _str_who + _str_words + _str_practices + _str_words + _str_religions
_regex_religion3 = re.compile(_str_religion3, re.IGNORECASE)

_str_religion4 = _str_religions + _str_words + _str_who
_regex_religion4 = re.compile(_str_religion4, re.IGNORECASE)

_str_religion5 = _str_practices + _str_words + _str_religions
_regex_religion5 = re.compile(_str_religion5, re.IGNORECASE)

_str_religion6 = _str_religions
_regex_religion6 = re.compile(_str_religion6, re.IGNORECASE)


_REGEXES = [
    _regex_religion1,
    _regex_religion2,
    _regex_religion3,
    _regex_religion4,
    _regex_religion5,
    _regex_religion6,
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

            religion_text = match.group('religion').strip()
            candidates.append(overlap.Candidate(
                start, end, match_text, regex, other=religion_text
            ))


    # if no matches, try to infer religion from presence of religious official(s)
    if 0 == len(candidates):
        match = _regex_official.search(sentence)
        if match:
            match_text = match.group().strip()
            start = match.start()
            end = start + len(match_text)
            
            religion_text = None
            if 'imam' in match_text:
                religion_text = 'islam'
            elif 'rabbi' in match_text or 'rabi' in match_text:
                religion_text = 'judaism'

            if religion_text is not None:
                candidates.append(overlap.Candidate(
                    start, end, match_text, regex, other=religion_text
                ))
            
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
        religion_text = c.other

        obj = ReligionTuple(
            sentence = cleaned_sentence,
            religion = religion_text
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

        # header present
        "Religion=Jehovah's Witness",
        'Farsi speaking only Religion: Muslim',
        'SOCIAL HISTORY:  He is a Muslim.',
        'social: Buddhist nun was visiting pt last night.',        
        'RELIGION: JEHOVAS WITNESS ( DOES NOT ACCEPT BLOOD TRANSFUSION)',
        'Religion is buddist and if pt should expire family requesting that body NOT go to morgue',
        'Social History: Homeless, retired Operating Room nurse, Buddhist monk',
        'Other: from [**Country **], devout muslim, non-english speaking',
        'Other: Non smoker, no etoh, no drug use. Mormon, very religious.',

        # <who> is <religion>
        'Pt is Buddhist and of Thai/Laotian descent',        
        'Dad stated that he is Buddhist',
        'Clergy Contact: Name: Pt is LDS, says her family will contact',
        'She is a Johovahs witness , she will not accept PRBC, platelets,  or FFP',        
        'they are Muslim and its against their culture and religion to use substances',
        'The parents are of the Mormon Faith',
        'all questions answered, patient muslim religion',
        'changed her name when she became a practicing Muslim',
        'Mormon faith and religious perspective',
        'She states that family is Buddhist, but she declines contacting any clergy',
        'a statement in reference to her Muslim faith and to the support that she receives from prayer',
        '88 YO non English speaking Hindu pt',
        'Buddhist monk and nun in with daughter and grand daughter in at bedside',
        'Retired Buddhist priest',
        'Muslim clergy member notified and still awaiting visit',
        'She is married to a Pentecostal minister',
        'Family made pt DNR and wish for blessing from Muslim holy person to bless pt before withdrawing care',
        'Son and Buddhist Monk visited in pm.',
        'EtOH: quit 30 years ago celibate Buddhist monk.',
        'PLAN WAS TO REMOVE LIFESUPPORT ONCE MUSLIM CLERGY SAW PATIENT',
        'wants to be visited by catholic priest to change her religion to catholic',
        'contacting funeral home as well as Buddhist clergy',
        'The patient is a 79 year old Vietnamese-speaking Buddhist monk',
        'Practices Russian Christianity',
        'HAVE DECLINED A BUDDHIST PRIEST AT THIS TIME.',

        # other
        'Coping with religion, Pentecostal, requested we read her a couple of scripture passages',
        'lives in [**Hospital1 240**] by himself-Muslim-no tobacco or etoh use as per son',        
        'single but has support from her parents as well as elders within her Jehova witness community',
        'family is praying at the Jewish temple',
        'had pastoral support from their own church and are following Buddhist traditions',
        'praying throughout day at Buddhist temple in [**Hospital1 **] and are \"hoping for a miracle.\"',
        'medical examiner denied examination. per rabi due to religion',        
        
        # negatives
        'Patient is Hindu speaking only',
        'pt speaks Hindu only',
        'lds dimished bases',
        'THIS GOES AGAINST THE GUIDELINES OF HER RELIGION, [**Doctor First Name **] SCIENTIST',
        'I have been told that the familys religion, which is [**Doctor First Name 6219**] Orthodox',
        "PT'S DESIRE TO AVOID BLOOD TRANSFUSIONS DUE TO RELIGION",        
    ]

    for sentence in SENTENCES:
        DISPLAY('\n' + sentence)
        json_result = run(sentence)
        json_data = json.loads(json_result)
        result_list = [ReligionTuple(**d) for d in json_data]
        for r in result_list:
            DISPLAY('\t{0}'.format(r))

