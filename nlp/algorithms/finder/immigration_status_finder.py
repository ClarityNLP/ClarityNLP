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
    

# US Citizen
# Legal Permanent Resident (Green Card)
# Conditional Permanent Resident
# Asylee or Refugee
# Non-immigrant visa (student, visitor, temporary worker, etc.)
# Undocumented
    
IMMIGRATION_TUPLE_FIELDS = [
    'sentence',
    'immigration_status'
]

ImmigrationTuple = namedtuple('ImmigrationTuple', IMIGRATION_TUPLE_FIELDS)
ImmigrationTuple.__new__.__defaults__ = (None,) * len(ImmigrationTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = False


###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    SENTENCES = [

        # immigrant
        '45 year old man with DOE, blood tinged sputum.  immigrant from [**Country **]',
        'Mo. is a 23 y.o. sp-spking [**Known patient lastname 5241**] immigrant x 5 yrs. who lives w/ partner',
        'Pt is from [**Country **], illegal immigrant, social work following.',
        'is the child of 20 y.o. sp-spking Guat. immigrant mo. who is currently s/p c/s, homeless',
        'Pt is   undocumented immigrant, not eligible for Mass Health.',
        'Pt reports he is an undocumented immigrant, originally from [**Country **].',
        'SOCIAL:   PT IS AN ILLEGAL IMMIGRANT',
        'Other: Jamaican immigrant',
        '20 YO PORTUGUESE SPEAKING BRAZILIAN IMMIGRANT ADMITTED TO HOSPITAL',
        'Social History: Russian immigrant',
        'Social History:\nImmigrant from [**Country 7824**]',
        'SOCIAL HISTORY:  The patient is a Russian immigrant, he is\nEnglish speaking.',

        # citizen
        'Wife is not US citizen; husband is US citizen',
        'she is not a US citizen',
        'She is visiting here from   the [**Country 1168**] Republic',
        'pt is not a US citizen',
        'Lives with his wife in a senior citizen center',
        'Other: lives in a senior citizen center',
        'Pt is an Indian citizen with US residency and lives here with nephew',
        'lives alone in senior citizen   housing',
        'lives in Montreal, Canadian citizen, 3 children who live in the area',
        'the patient is not a US citizen (Canadian)',
        'The patient is a 24-year-old male, Irish citizen',
        'Social History: Divorced and lives alone in a senior citizen building',
        'Social History: Pt is a Chinese citizen',
        'He has been in the U.S. for 23 years and is a citizen',
        "SOCIAL HISTORY:  Lives by herself in a senior citizen's home.",
        'the patient is not a United States citizen or [**State **] resident',
        'doing senior citizen work',
        'She lives in a senior citizen center',
        'She is widowed, lives in senior citizen housing',
        'Social History: Pt lives as Winter Valley Senior Citizen Living',
        'Retired, lives in senior citizen apartment complex because of permanent disability',
        'SOCIAL HISTORY: Is that she lives in a Senior Citizen home',
        'Social History: Lives with husband in senior citizen complex',
        'Social History: riginally from [**Country 3537**], is not a documented citizen',
        'Social History: The patient is originally from [**Country 9273**], immigrated [**3327**], now US citizen.',
        "given the patient's current status as a non US citizen",
        'She is currently not a legal citizen of the United States',

        # green card
        'pt may be denied green card if dx known',
        'PT OFFERING TO SHOW HER GREEN CARD SO SHE COULD GO HOME',
        'she won a lottery for a Green Card',
        'pt may be denied a Green Card upon receiving the diagnosis of schizophrenia',
        'required to get green card   from Kenyan embassy',
        'Pt fears that she was using him for a green card, as her behavior changed ' \
        'dramatically when she came to the US',

        # permanent resident (most negative)
        'HE is a permanent resident at [**Hospital1 605**]',
        'SOCIAL HISTORY:  The patient is a permanent resident at the [**Hospital3 8956**].',
        'The patient is to be discharged back to [**Hospital3 8956**] where she is a permanent resident.',
        'Other: Permanent resident of [**Hospital3 2716**] Manor',
        'This 83 year old woman with paranoid schizophrenia and permanent resident ' \
        'of the [**Hospital1 13136**] Nursing Health Center',
        'pt has been a permanent resident of the US since 2014',
        'pt. is legal resident',
        'Pt is an Indian citizen with US residency and lives here with nephew',

        # visa
        'this will enable her to stay for an additional x 30 day visa',
        'she has a visa to work in USa valid until',
        'an application to extend her visa',
        'will asssit with letter requesting extension of visa',        
        'is unsure if he will be able to obtain a visa',
        "the pt's wife did receive a visa and is making arrangements to fly to",
        'LETTER FOR FAMILY MEMBER GIVEN FOR VISA FROM [**Location (un) 5841**] AND TOBEGO',
        'British Mom with temporary Visa negotiating the maze of discharge planning',
        'Mom in Bermuda re travel visa',
        'SW will prepare letter requesting visa for MD signature',
        'SW consult for family regarding obtaining an   emergency visa for pt daughters',

        # refugee
        'immigrated to the United States in [**3417**] as a refugee from   [**Country 287**]',
        'Pt is a Ukrainian refugee who immigrated to the US in [**3185**]',
        
        # negative
        'R pupil greater than L at times visa versa, both reactive',
        'ESRD on HD, recent VISA bacteremia who has been intermittently CMO',
        'Formerly worked for the federal government as the Director of Refugee Resettlement',
        'They\nlived in a refugee camp until [**2629**] when they left for the [**Country 3118**] for 3 months',
    ]
