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
    import finder_overlap as overlap
except:
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
_TRACE = True


# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\s?(' + _str_word + r'){0,5}?'


_str_religions = r'\b(?P<religion>(jehovah?s witness|pentecostal|buddhist|' +\
    r'jew(ish|daism)?|muslim|islam|christian(ity)?))\b'

_str_header = r'\b(religion|social( history)?|other)\s?[:= ]'

_str_religion1 = _str_header + _str_words + _str_religions
_regex_religion1 = re.compile(_str_religion1, re.IGNORECASE)


_REGEXES = [
    _regex_religion1,
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

            print('\t{0}'.format(match_text))
            
            
###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        print(cleaned_sentence)

    candidates = _regex_match(cleaned_sentence, _REGEXES)
    

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
        'Social History: Homeless, retired Operating Room nurse, Buddhist monk',
        'Other: from [**Country **], devout muslim, non-english speaking',
    ]

    for sentence in SENTENCES:
        print('\n' + sentence)
        run(sentence)

    """
        'Religion is buddist and if pt should expire family requesting that body NOT go to morgue',
        'Pt is Buddhist and of Thai/Laotian descent',        
        'Dad stated that he is Buddhist',        
        'She is a Johovahs witness , she will not accept PRBC, platelets,  or FFP',        
        'they are Muslim and its against their culture and religion to use substances',
        
        'medical examiner denied examination. per rabi due to religion',
        'wants to be visited by catholic priest to change her religion to catholic',
        'Coping with religion, Pentecostal, requested we read her a couple of scripture passages',
        'THIS GOES AGAINST THE GUIDELINES OF HER RELIGION, [**Doctor First Name **] SCIENTIST',
        'She is married to a Pentecostal minister',
        'I have been told that the familys religion, which is [**Doctor First Name 6219**] Orthodox',
        "PT'S DESIRE TO AVOID BLOOD TRANSFUSIONS DUE TO RELIGION",
        'PLAN WAS TO REMOVE LIFESUPPORT ONCE MUSLIM CLERGY SAW PATIENT',
        'all questions answered, patient muslim religion',
        'a statement in reference to her Muslim faith and to the support that she receives from prayer',
        'Muslim clergy member notified and still awaiting visit',
        'Family made pt DNR and wish for blessing from Muslim holy person to bless pt before withdrawing care',
        'changed her name when she became a practicing Muslim',
        'lives in [**Hospital1 240**] by himself-Muslim-no tobacco or etoh use as per son',
        'single but has support from her parents as well as elders within her Jehova witness community',
        'contacting funeral home as well as Buddhist clergy',
        'had pastoral support from their own church and are following Buddhist traditions',
        'Buddhist monk and nun in with daughter and grand daughter in at bedside',
        'praying throughout day at Buddhist temple in [**Hospital1 **] and are \"hoping for a miracle.\"',
        'Son and Buddhist Monk visited in pm.',
        'HAVE DECLINED A BUDDHIST PRIEST AT THIS TIME.',
        'She states that family is Buddhist, but she declines contacting any clergy',
        'Retired Buddhist priest',
        'The patient is a 79 year old Vietnamese-speaking Buddhist monk',
        'EtOH: quit 30 years ago celibate Buddhist monk.',
        '88 YO non English speaking Hindu pt',
        'Practices Russian Christianity',
        

        # negatives
        'Patient is Hindu speaking only',
        'pt speaks Hindu only',
    """
