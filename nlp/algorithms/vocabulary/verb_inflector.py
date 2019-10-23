#!/usr/bin/env python3
"""


OVERVIEW:



This module computes verb inflections from a given verb in base form. Base
form is also known as 'plain form', 'dictionary form', or the 'principal part'
of the verb. For example, here is a list of verbs and their base forms:

    Verb         Base Form
    -------      ---------
    running      run
    walks        walk
    eaten        eat
    were         be
 
It is not possible to unambiguously compute the base form of a verb from an
arbitrary inflected form. Observe:

    Verb        Possible Base Forms
    ------      -------------------

    clad        clad (to cover with material), clothe (to cover with clothes) 
    cleft       cleave (to split), cleft (separate important part of a clause)
    fell        fell (to make something fall), fall (to take a tumble)
    lay         lay (to set down), lie (to rest on a surface)

The only way to unambiguously recover the base form from an arbitrary
inflection is to supply additional information such as meaning, 
pronounciation, or something else. 

Lemmatizers attempt to solve this problem, but with decidedly mixed results. 
Neither the NLTK WordNet lemmatizer nor the Spacy lemmatizer worked reliably 
enough on this module's test data to allow users to input verbs in arbitrary
inflections.

Therefore we require the verb to be supplied in base form.

The algorithms in this module were derived from various web sites purporting
to list the rules for English spelling. Most of the sources consulted were
incomplete or had easily-discovered exceptions to their dogmatic assertions. 
The Wikipedia page on English verbs was very helpful. It can be found here:

    https://en.wikipedia.org/wiki/English_verbs



DEPENDENCIES:



This module requires the 'CMU Pronouncing Dictionary', since some verb 
inflections depend on whether vowels are long or short, and whether the
final syllable is stressed. This dictionary (cmudict) is supplied as a 
component of NLTK, but it first must be installed by running these commands
in a python shell:

    import nltk
    nltk.download('cmudict')




FUNCTIONS:


    get_inflections(base_form)


    Returns all inflections for the verb whose base form is given. The base
    form argument is a string.

    The inflections are returned as a five-element list with the following
    interpretation:

        element 0: [string] the base, dictionary, or bare infinitive form
        element 1: [list] third person singular present forms
        element 2: [list] present participle forms
        element 3: [list] simple past tense (preterite) forms
        element 4: [list] past participle forms

    Even if only a single variant exists for components 1-4, that variant
    is still returned as a single-element list, for consistency.

    Example:

        inflections = get_inflections('outdo')        
        # returns ['outdo',['outdoes'],['outdoing'],['outdid'],['outdone']]

        inflections = get_inflections('be')
        # returns ['be',['is'],['being'],['was','were'],['been']]



TESTING



Run the quick module self-tests from the command line as follows:

    python3 ./verb_inflector.py --selftest

Run more extensive tests using a set of nearly 1400 verbs, which includes all
of the irregular English verbs and the 1000 most common verbs (with duplicates
removed between the two sets):

    python3 ./verb_inflector.py -f inflection_truth_data.txt

Both tests should run to completion without any logout to the screen.

"""

import re
import os
import sys
import optparse
from nltk.corpus import wordnet
from nltk.corpus import cmudict
from claritynlp_logging import log, ERROR, DEBUG

try:
    from .irregular_verbs import VERBS as IRREGULAR_VERBS
except Exception as e:
    log(e)
    from irregular_verbs import VERBS as IRREGULAR_VERBS

VERSION_MAJOR = 0
VERSION_MINOR = 3

MODULE_NAME = 'verb_inflector.py'

TRACE = False

# cmudict phonemes for a 't' sound and an 'ee' sound
PHONEME_T  = 'T'
PHONEME_EE = 'IY'

cmu_dict = cmudict.dict()

# recognizes words ending in vowel followed by consonant, with exceptions
str_vc_ending = r'[aeiou][^aeiouhwxy]\Z'
regex_vc_ending = re.compile(str_vc_ending, re.IGNORECASE)

# recognizes words ending in two vowels followed by consonant, with exceptions
str_vvc_ending = r'[aeiou][aeiou][^aeiouhwxy]\Z'
regex_vvc_ending = re.compile(str_vvc_ending, re.IGNORECASE)

# recognizes words ending in vowel followed by 'y'
str_consonant_y_ending = r'[^aeiou]y\Z'
regex_consonant_y_ending = re.compile(str_consonant_y_ending, re.IGNORECASE)

# recognizes words ending in vowel followed by 'o'
str_consonant_o_ending = r'[^aeiou]o\Z'
regex_consonant_o_ending = re.compile(str_consonant_o_ending, re.IGNORECASE)

# recognizes words ending in 'ee', 'oe', 'ye'
str_ee_oe_ye_ending = r'[eoy]e\Z'
regex_ee_oe_ye_ending = re.compile(str_ee_oe_ye_ending, re.IGNORECASE)

# recognizes words ending in vowel followed by l
str_vowel_l_ending = r'[aeiou]l\Z'
regex_vowel_l_ending = re.compile(str_vowel_l_ending, re.IGNORECASE)


###############################################################################
def is_irregular_verb(base_form):
    """
    Returns a Boolean indicating whether the given verb is irregular.
    """

    return base_form in IRREGULAR_VERBS


###############################################################################
def is_final_consonant_doubled(base):
    """
    Returns a list of single consonants (or ''), indicating the valid
    consonant doublings for the given base form verb.
    """

    if TRACE:
        log('calling is_final_consonant_doubled...')
    
    # if the base form ends in 'c', double by adding 'k'
    if base.endswith('c'):
        if TRACE: log("\tends with 'c'")
        # exceptions to the append 'k' rule
        if base == 'mic':
            return ['']
        elif base == 'spec':
            return ['c']
        elif base == 'sync':
            return ['h', '']
        return ['k']

    # if verb ends in two vowels plus consonant
    match = regex_vvc_ending.search(base)
    if match:
        if len(base) >= 4 and 'q' == base[-4] and 'u' == base[-3]:
            if TRACE: log('\tvvc ending with qu')
            # the qu acts like a qw, so really a q-consonant-vowel-consonant
            return base[-1]
        else:
            if TRACE: log('\tvvc ending, not qu-vowel-consonant')
            return []

    try:
        phoneme_lists = cmu_dict[base]
    except KeyError:
        # not in cmudict
        return []

    # different pronunciations can require different spellings
    characters = set()
    for phoneme_list in phoneme_lists:
        syllable_count = 0
        is_final_syllable = True
        is_final_syllable_stressed = False
        for phoneme in reversed(phoneme_list):
            n = phoneme[-1]
            if not n.isdigit():
                continue
            else:
                # count syllables by counting digits
                syllable_count += 1
                if is_final_syllable:
                    is_final_syllable = False
                    if 0 != int(n):
                        is_final_syllable_stressed = True

        # whether the verb ends with a silent t
        silent_t = base.endswith('t') and PHONEME_T != phoneme_lists[0][-1]
    
        # check for vowel-consonant ending
        result = ''
        match = regex_vc_ending.search(base)
        if match and not silent_t:
            if 1 == syllable_count:
                if TRACE: log('\tvc ending, single syllable, ' \
                                'double final consonant')
                result = base[-1]
            elif is_final_syllable_stressed:
                if TRACE: log('\tvc ending, multi-syllable, ' \
                                'stress on final, doubling final consonant')
                result = base[-1]

        characters.add(result)
                
    return list(characters)



###############################################################################
def regular_simple_past(base):
    """
    Returns a list of the simple past tense forms of the REGULAR verb 
    whose base form is given.

    Rules are taken from the Wikipedia article
    """

    if TRACE:
        log("calling regular_simple_past for verb '{0}'".format(base))

    if 0 == len(base):
        return []

    EXCEPTIONS_PAST_TENSE = {
        'arc':['arced', 'arcked', 'arked'],
        'benefit':['benefited', 'benefitted'],
        'bias':['biased', 'biassed'],
        'bus':['bussed', 'bused'],
        'develop':['developed', 'developt'],
        'equip':['equipped'],
        'mic':['miced'],
        'focus':['focused', 'focussed'],
        'saute':['sauteed'],
        'sky':['skied', 'skyed'],
        'spec':['specced'],
        'sync':['synched', 'synced'],
        'target':['targeted', 'targetted']
    }

    if base in EXCEPTIONS_PAST_TENSE:
        if TRACE: log('\tfound exception')
        return EXCEPTIONS_PAST_TENSE[base]
    
    if 0 == len(base):
        return []

    # if the base form ends in 'e' then add a 'd'
    if 'e' == base[-1]:
        if TRACE: log("\tends in 'e' so add 'd'")
        return [base + 'd']

    # if the base form ends in <consonant>y, change y to i and add 'ed'
    match = regex_consonant_y_ending.search(base)
    if match:
        if TRACE: log('\tends in <consonant>y')
        return [base[:-1] + 'ied']

    # If word ends in vowel-l, double the l prior to a suffix that begins
    # with a vowel to get the British spelling. American English does not
    # generally do this. Both forms are common, so return both. See this
    # page for more:
    #
    #     https://english.stackexchange.com/questions/338/when-is-l-doubled
    match = regex_vowel_l_ending.search(base)
    if match:
        if TRACE: log('\tfound vowel-l ending')
        american = base + 'ed'
        british = base + 'led'
        return [american, british]
    
    # check for pronounciation-dependent spellings via consonant doublings
    consonant_list = is_final_consonant_doubled(base)
    if len(consonant_list) > 0:
        results = []
        for c in consonant_list:
            results.append(base + c + 'ed')
        return results
        
    if TRACE: log("\tadding default 'ed' ending")
    return [base + 'ed']


###############################################################################
def simple_past(base):
    """
    Returns the simple past tense form of the verb whose base form is given.
    """

    if 0 == len(base):
        return []
    
    if is_irregular_verb(base):
        return IRREGULAR_VERBS[base][0]
    else:
        return regular_simple_past(base)


###############################################################################
def past_participle(base):
    """
    Returns the past participle of the verb whose base form is given.
    """

    EXCEPTIONS_PAST_PART = {
        'carve':['carved', 'carven'],
        'shape':['shaped', 'shapen'],
    }
    
    if 0 == len(base):
        return []

    if base in EXCEPTIONS_PAST_PART:
        return EXCEPTIONS_PAST_PART[base]
    
    if is_irregular_verb(base):
        return IRREGULAR_VERBS[base][1]
    else:
        return regular_simple_past(base)


###############################################################################
def present_participle(base):
    """
    Returns the present participle of the verb whose base form is given.
    """

    EXCEPTIONS_PP = {
        'arc':['arcing', 'arcking'],              # multiple spellings
        'babysit':['babysitting'],                # cmudict: no final stress
        'be':['being'],                           # in a class by itself
        'beken':['bekenning'],                    # not in cmudict
        'beknit':['beknitting'],                  # not in cmudict
        'beware':[],                              # defective verb
        'benefit':['benefiting', 'benefitting'],  # multiple spellings
        'bus':['bussing', 'busing'],              # multiple spellings
        'can':['could'],                          # modal, irregular
        'crosscut':['crosscutting'],              # not in cmudict
        'focus':['focussing', 'focusing'],        # multiple spellings
        'foreken':['forekenning'],                # not in cmudict
        'forfret':['forfretting'],                # not in cmudict
        'grue':['gruing'],                        # not in cmudict
        'housesit':['housesitting'],              # not in cmudict
        'intercut':['intercutting'],              # not in cmudict
        'may':['might'],                          # modal, irregular
        'mishit':['mishitting'],                  # not in cmudict
        'misken':['miskenning'],                  # not in cmudict
        'misset':['missetting'],                  # not in cmudict
        'miswed':['miswedding'],                  # not in cmudict
        'must':[],                                # modal, irregular
        'ought':[],                               # auxiliary, needs another verb
        'outken':['outkenning'],                  # not in cmudict
        'outspin':['outspinning'],                # not in cmudict
        'outswim':['outswimming'],                # not in cmudict
        'overbid':['overbidding'],                # not in cmudict
        'overhit':['overhitting'],                # not in cmudict
        'overset':['oversetting'],                # not in cmudict
        'overwet':['overwetting'],                # not in cmudict
        'recut':['recutting'],                    # not in cmudict
        'resit':['resitting'],                    # not in cmudict
        'rewed':['rewedding'],                    # not in cmudict
        'shall':['should'],                       # modal, irregular
        'target':['targeting', 'targetting'],     # multiple spellings
        'underbet':['underbetting'],              # not in cmudict
        'underdig':['underdigging'],              # not in cmudict
        'underrun':['underrunning'],              # not in cmudict
        'will':['willing'],                       # modal, irregular
        'zinc':['zincing', 'zinking', 'zincking'] # multiple spellings
    }

    # all of these have multiple accepted spellings
    EXCEPTIONS_FINAL_E = {
        'age':['ageing', 'aging'],
        'binge':['bingeing', 'binging'],
        'birdie':['birdieing', 'birdying'],
        'blue':['blueing', 'bluing'],
        'eye':['eyeing', 'eying'],
        'luge':['luging', 'lugeing'],
        'ochre':['ochring', 'ochreing'],
        'queue':['queueing', 'queuing'],
        'rue':['ruing', 'rueing'],
        'sortie':['sortying', 'sortieing'],
        'swinge':['swinging', 'swingeing'],
        'tinge':['tinging', 'tingeing'],
        'twinge':['twingeing', 'twinging'],
        'whinge':['whingeing', 'whinging'],
    }

    EXCEPTIONS_PP_SILENT_E = ['cue', 'saute', 'singe', 'vogue']

    if TRACE:
        log("calling present_participle for verb '{0}'".format(base))

    if 0 == len(base):
        return []
        
    if base in EXCEPTIONS_PP:
        return EXCEPTIONS_PP[base]
    
    if base in EXCEPTIONS_FINAL_E:
        return EXCEPTIONS_FINAL_E[base]
    
    # change '-ie' to '-ying'
    if len(base) >= 2 and base.endswith('ie'):
        if TRACE: log('\treplacing -ie with -ying')
        return [base[:-2] + 'ying']

    # keep final 'e' if base form ends in 'ee', 'oe', or 'ye'
    match = regex_ee_oe_ye_ending.search(base)
    if match:
        if TRACE: log('\tends in ee, or, or ye')
        return [base + 'ing']

    # If word ends in vowel-l, double the l prior to a suffix that begins
    # with a vowel to get the British spelling. American English does not
    # generally do this. Both forms are common, so return both. See this
    # page for more:
    #
    #     https://english.stackexchange.com/questions/338/when-is-l-doubled
    match = regex_vowel_l_ending.search(base)
    if match:
        if TRACE: log('\tfound vowel-l ending')
        # if the vowel before the l is an 'i', the rule does not seem to apply
        # (sail -> sailing, tail -> tailing, etc.)
        if len(base) >= 2 and 'i' != base[-2]:
            american = base + 'ing'
            british = base + 'ling'
            return [american, british]
        else:
            return [base + 'ing']

    in_cmu_dict = True
    try:
        phoneme_lists = cmu_dict[base]
    except KeyError:
        in_cmu_dict = False
        if TRACE: log('\tnot in CMU dict')

    # check for silent-e ending
    if base.endswith('e'):
        if in_cmu_dict:
            results = set()
            for phoneme_list in phoneme_lists:
                silent_e = PHONEME_EE != phoneme_list[-1]
                if silent_e and base in EXCEPTIONS_PP_SILENT_E:
                    # retain the final e
                    if TRACE: log('\tsilent-e exception')
                    results.add(base + 'ing')
                else:
                    # drop the final e
                    if TRACE: log('\tdropping final e')
                    results.add(base[:-1] + 'ing')
            return list(results)
        else:
            # drop final e
            if TRACE: log('\tdropping final e')
            return [base[:-1] + 'ing']

    # check for pronounciation-dependent spellings via consonant doublings
    consonant_list = is_final_consonant_doubled(base)
    if len(consonant_list) > 0:
        results = set()
        for c in consonant_list:
            results.add(base + c + 'ing')
        return list(results)

    if TRACE: log('\tdefault -ing ending')
    return [base + 'ing']


###############################################################################
def third_person_singular_present(base):
    """
    Returns the 3rd person singular present of the verb whose base form
    is given.
    """

    EXCEPTIONS_3RD_PERSON = {
        'be':['is'],
        'beware':[],
        'bus':['busses', 'buses'],
        'can':['can'],
        'dare':['dare', 'dares'],
        'focus':['focuses', 'focusses'],
        'have':['has'],
        'may':['may'],
        'must':['must'],
        'ought':[],
        'shall':['shall'],
        'will':['will'],
    }
    
    if TRACE:
        log('calling third_person_singular_present...')

    if 0 == len(base):
        return []
        
    if base in EXCEPTIONS_3RD_PERSON:
        return EXCEPTIONS_3RD_PERSON[base]
    
    # <consonant>y ending changes 'y' to 'i' and adds 'es'
    match = regex_consonant_y_ending.search(base)
    if match:
        if TRACE: log('\tends in <consonant>y')
        return [base[:-1] + 'ies']

    # <consonant>o ending addes 'es'
    match = regex_consonant_o_ending.search(base)
    if match:
        if TRACE: log('\tends in <consonant>o')
        return [base + 'es']

    # check for base form ending in a sibilant sound:
    #     voiceless alveolar sibilant       phoneme 'S'
    #     voiced alveolar sibilant          phoneme 'Z'
    #     voiceless postalveolar fricative  phoneme 'SH'
    #     voiced postalveolar fricitave     phoneme 'ZH'
    #     voiceless postalveolar affricate  phoneme 'CH'
    #     voiced postalveolar affricate     phoneme 'JH'
    SIBILANT_PHONEMES = ['S', 'Z', 'SH', 'ZH', 'CH', 'JH']

    in_cmu_dict = True
    try:
        phoneme_lists = cmu_dict[base]
    except KeyError:
        in_cmu_dict = False

    if in_cmu_dict:
        results = set()
        for phoneme_list in phoneme_lists:
            ending = 's'
            if phoneme_list[-1] in SIBILANT_PHONEMES:
                # ends in a sibilant sound, check for silent-e ending
                if not base.endswith('e'):
                    if TRACE: log('\tends with sibilant sound, no silent-e')
                    ending = 'es'
            results.add(base + ending)
        return list(results)

    if TRACE: log("\tusing default 's' ending")
    return [base + 's']
                    

###############################################################################
def get_inflections(base):
    """
    Returns all inflections for the verb whose base form is given. Base form 
    is also known as 'dictionary' or 'bare infinitive' form. For instance,
    the base forms for these verbs are:

        going -> go
        ran   -> run
        walks -> walk

    The inflections are returned as a five-element list. Each element of the 
    list other than the first could also be a list, since English verbs often
    have multiple accepted spellings.

    The returned list components are interpreted as follows:

        element 0: [string] the base, dictionary, or bare infinitive form
        element 1: [list] third person singular present forms
        element 2: [list] present participle forms
        element 3: [list] simple past tense (preterite) forms
        element 4: [list] past participle forms

    Even if only a single variant exists for components 1-4, that variant
    is still returned as a single-element list, for consistency.

    Example:

        inflections = get_inflections('outdo')        
        # returns ['outdo',['outdoes'],['outdoing'],['outdid'],['outdone']]

        inflections = get_inflections('be')
        # returns ['be',['is'],['being'],['was','were'],['been']]
    """

    third     = third_person_singular_present(base)
    pres_part = present_participle(base)
    past      = simple_past(base)
    past_part = past_participle(base)

    return [base, third, pres_part, past, past_part]


###############################################################################
def check_for_errors(base, truth_third, truth_pres_part,
                     truth_past, truth_past_part):

    third     = third_person_singular_present(base)
    pres_part = present_participle(base)
    past      = simple_past(base)
    past_part = past_participle(base)

    has_error = False
    for v in truth_third:
        if v not in third:
            has_error = True
            break

    for v in truth_pres_part:
        if v not in pres_part:
            has_error = True
            break

    for v in truth_past:
        if v not in past:
            has_error = True
            break

    for v in truth_past_part:
        if v not in past_part:
            has_error = True
            break

    if has_error:
        log('base: {0}'.format(base))
        log('\t    truth_third: {0}, computed: {1}'.format(truth_third, third))
        log('\ttruth_pres_part: {0}, computed: {1}'.format(truth_pres_part, pres_part))
        log('\t     truth_past: {0}, computed: {1}'.format(truth_past, past))
        log('\ttruth_past_part: {0}, computed: {1}'.format(truth_past_part, past_part))


###############################################################################
def run_tests():

    # base, 3rd person singular present, present part, past, past part

    verb_inflections = [

        # base form ends with consonant followed by 'y'
        ('try',      ['tries'],      ['trying'],      ['tried'],      ['tried']),
        ('carry',    ['carries'],    ['carrying'],    ['carried'],    ['carried']),
        ('identify', ['identifies'], ['identifying'], ['identified'], ['identified']),

        # base form ends with consonant followed by 'o'
        ('echo',     ['echoes'],     ['echoing'],     ['echoed'],     ['echoed']),
        ('outdo',    ['outdoes'],    ['outdoing'],    ['outdid'],     ['outdone']),
        ('radio',    ['radios'],     ['radioing'],    ['radioed'],    ['radioed']),

        # base form ends with 'ie'
        ('belie',   ['belies'],  ['belying'],     ['belied'],            ['belied']),
        ('die',     ['dies'],    ['dying'],       ['died'],              ['died']),
        ('tie',     ['ties'],    ['tying'],       ['tied'],              ['tied']),
        ('birdie',  ['birdies'], ['birdieing', 'birdying'], ['birdied'], ['birdied']), 
        ('sortie',  ['sorties'], ['sortying', 'sortieing'], ['sortied'], ['sortied']),
        
        # base form ends with 'c'
        ('panic',    ['panics'],  ['panicking'],   ['panicked'],   ['panicked']),
        ('spec',     ['specs'],   ['speccing'],    ['specced'],    ['specced']),
        ('mic',      ['mics'],    ['micing'],      ['miced'],      ['miced']),
        ('sync',     ['syncs'],   ['synching', 'syncing'],
            ['synched', 'synced'], ['synched', 'synced']),
        ('arc',      ['arcs'],    ['arcing', 'arcking'],
            ['arced', 'arcked', 'arked'], ['arced', 'arcked', 'arked']),

        # base form ends in single vowel followed by consonant in [hwxy]
        # (cannot find any regular verbs ending in single vowel followed by h...)
        ('avow',     ['avows'],      ['avowing'],     ['avowed'],     ['avowed']),
        ('renew',    ['renews'],     ['renewing'],    ['renewed'],    ['renewed']),
        ('annex',    ['annexes'],    ['annexing'],    ['annexed'],    ['annexed']),
        ('perplex',  ['perplexes'],  ['perplexing'],  ['perplexed'],  ['perplexed']),
        ('key',      ['keys'],       ['keying'],      ['keyed'],      ['keyed']),
        ('destroy',  ['destroys'],   ['destroying'],  ['destroyed'],  ['destroyed']),
        ('survey',   ['surveys'],    ['surveying'],   ['surveyed'],   ['surveyed']),

        # base form ends in single vowel followed by consonant not in [hwxy]
        ('ship',    ['ships'],    ['shipping'],    ['shipped'],    ['shipped']),
        ('catalog', ['catalogs'], ['cataloging'],  ['cataloged'],  ['cataloged']),
        ('format',  ['formats'],  ['formatting'],  ['formatted'],  ['formatted']),
        ('program', ['programs'], ['programming'], ['programmed'], ['programmed']),
        ('pyramid', ['pyramids'], ['pyramiding'],  ['pyramided'],  ['pyramided']),

        # base form ends in two vowels followed by consonant in [hwxy]
        ('aah',      ['aahs'],       ['aahing'],      ['aahed'],      ['aahed']),
        ('ooh',      ['oohs'],       ['oohing'],      ['oohed'],      ['oohed']),
        ('view',     ['views'],      ['viewing'],     ['viewed'],     ['viewed']),
        ('meow',     ['meows'],      ['meowing'],     ['meowed'],     ['meowed']),
        ('hoax',     ['hoaxes'],     ['hoaxing'],     ['hoaxed'],     ['hoaxed']),
        ('okay',     ['okays'],      ['okaying'],     ['okayed'],     ['okayed']),

        # base form ends in two vowels followed by consonant not in [hwxy]
        ('wheel',     ['wheels'],     ['wheeling'],     ['wheeled'],     ['wheeled']),
        ('treat',     ['treats'],     ['treating'],     ['treated'],     ['treated']),
        ('partition', ['partitions'], ['partitioning'], ['partitioned'], ['partitioned']),
        ('pour',      ['pours'],      ['pouring'],      ['poured'],      ['poured']),

        # base form ends in a silent 't'
        ('crochet', ['crochets'], ['crocheting'],  ['crocheted'],  ['crocheted']),
        ('debut',   ['debuts'],   ['debuting'],    ['debuted'],    ['debuted']),

        # base form ends in a voiced 't'
        ('trot',    ['trots'],    ['trotting'],    ['trotted'],    ['trotted']),
        ('comment', ['comments'], ['commenting'],  ['commented'],  ['commented']),
        ('entreat', ['entreats'], ['entreating'],  ['entreated'],  ['entreated']),

        # base form ends in a silent 'e'
        ('canoe',   ['canoes'],   ['canoeing'],    ['canoed'],     ['canoed']),
        ('cache',   ['caches'],   ['caching'],     ['cached'],     ['cached']),
        ('grue',    ['grues'],    ['gruing'],      ['grued'],      ['grued']),
        ('saute',   ['sautes'],   ['sauteing'],    ['sauteed'],    ['sauteed']),
        ('toe',     ['toes'],     ['toeing'],      ['toed'],       ['toed']),
        ('vogue',   ['vogues'],   ['vogueing'],    ['vogued'],     ['vogued']),
        ('prune',   ['prunes'],   ['pruning'],     ['pruned'],     ['pruned']),
        ('value',   ['values'],   ['valuing'],     ['valued'],     ['valued']),
        ('stripe',  ['stripes'],  ['striping'],    ['striped'],    ['striped']),
        ('dine',    ['dines'],    ['dining'],      ['dined'],      ['dined']),

        # base form ends in 'ee', 'oe', 'ye'
        ('see',     ['sees'],     ['seeing'],           ['saw'],     ['seen']),
        ('agree',   ['agrees'],   ['agreeing'],         ['agreed'],  ['agreed']),
        ('dye',     ['dyes'],     ['dyeing'],           ['dyed'],    ['dyed']),
        ('eye',     ['eyes'],     ['eyeing', 'eying'],  ['eyed'],    ['eyed']),
        ('hoe',     ['hoes'],     ['hoeing'],           ['hoed'],    ['hoed']),
        ('tiptoe',  ['tiptoes'],  ['tiptoeing'],        ['tiptoed'], ['tiptoed']),
        
        # verbs ending in a sibilant sound, either with or without a silent 'e'
        ('guess',      ['guesses'],     ['guessing'],     ['guessed'],     ['guessed']),
        ('distress',   ['distresses'],  ['distressing'],  ['distressed'],  ['distressed']),
        ('wheeze',     ['wheezes'],     ['wheezing'],     ['wheezed'],     ['wheezed']),
        ('buzz',       ['buzzes'],      ['buzzing'],      ['buzzed'],      ['buzzed']),
        ('homogenize', ['homogenizes'], ['homogenizing'], ['homogenized'], ['homogenized']),
        ('flourish',   ['flourishes'],  ['flourishing'],  ['flourished'],  ['flourished']),
        ('unleash',    ['unleashes'],   ['unleashing'],   ['unleashed'],   ['unleashed']),
        ('rouge',      ['rouges'],      ['rouging'],      ['rouged'],      ['rouged']),
        ('sabotage',   ['sabotages'],   ['sabotaging'],   ['sabotaged'],   ['sabotaged']),
        ('arbitrage',  ['arbitrages'],  ['arbitraging'],  ['arbitraged'],  ['arbitraged']),
        ('itch',       ['itches'],      ['itching'],      ['itched'],      ['itched']),
        ('watch',      ['watches'],     ['watching'],     ['watched'],     ['watched']),
        ('research',   ['researches'],  ['researching'],  ['researched'],  ['researched']),
        ('barge',      ['barges'],      ['barging'],      ['barged'],      ['barged']),
        ('singe',      ['singes'],      ['singeing'],     ['singed'],      ['singed']),
        ('splurge',    ['splurges'],    ['splurging'],    ['splurged'],    ['splurged']),
        ('swinge',     ['swinges'],     ['swinging', 'swingeing'], ['swinged'], ['swinged']),
        ('tinge',      ['tinges'],      ['tinging',  'tingeing'],  ['tinged'],  ['tinged']),
        ('twinge',     ['twinges'],     ['twingeing', 'twinging'], ['twinged'], ['twinged']),
        ('whinge',     ['whinges'],     ['whingeing', 'whinging'], ['whinged'], ['whinged']),
        
        # unstressed final syllable
        ('fathom',  ['fathoms'],  ['fathoming'],  ['fathomed'],   ['fathomed']),
        ('listen',  ['listens'],  ['listening'],  ['listened'],   ['listened']),
        ('happen',  ['happens'],  ['happening'],  ['happened'],   ['happened']),

        # copular verb 'be'
        ('be',      ['is'],       ['being'],      ['was', 'were'], ['been']),

        # modals, auxiliaries, etc.
        ('can',     ['can'],      ['could'],      ['could'],    []),
        ('may',     ['may'],      ['might'],      ['might'],    []),
        ('shall',   ['shall'],    ['should'],     ['should'],   []),
        ('will',    ['will'],     ['willing'],    ['would'],    []),
        ('must',    ['must'],     [],             [],           []),
        ('ought',   [],           [],             [],           []),
        ('need',    ['needs'],    ['needing'],    ['needed'],   ['needed']),
        ('dare',    ['dares'],    ['daring'],     ['dared'],    ['dared']),
        ('use',     ['uses'],     ['using'],      ['used'],     ['used']),
        ('better',  ['betters'],  ['bettering'],  ['bettered'], ['bettered']),
        ('have',    ['has'],      ['having'],     ['had'],      ['had']),
        ('do',      ['does'],     ['doing'],      ['did'],      ['done']),

        # doubling the final consonant
        ('enrol',     ['enrols'],     ['enrolling'],    ['enrolled'],    ['enrolled']),
        ('enroll',    ['enrolls'],    ['enrolling'],    ['enrolled'],    ['enrolled']),
        ('befit',     ['befits'],     ['befitting'],    ['befitted'],    ['befitted']),
        ('offer',     ['offers'],     ['offering'],     ['offered'],     ['offered']),
        ('prefer',    ['prefers'],    ['preferring'],   ['preferred'],   ['preferred']),
        ('profit',    ['profits'],    ['profiting'],    ['profited'],    ['profited']),
        ('discomfit', ['discomfits'], ['discomfiting'], ['discomfited'], ['discomfited']),
        
        # defective
        ('beware',  [], [], [], []), 
        
        # other
        ('fruit',   ['fruits'],  ['fruiting'],   ['fruited'],    ['fruited']),
        ('install', ['installs'],['installing'], ['installed'],  ['installed']),
        ('feed',    ['feeds'],   ['feeding'],    ['fed'],        ['fed']),
        ('clad',    ['clads'],   ['cladding'],   ['clad'],       ['clad']),
        ('bias',    ['biases'],  ['biasing'],    ['biased', 'biassed'], ['biased', 'biassed']),
        ('strip',   ['strips'],  ['stripping'],  ['stripped', 'stript'], ['stripped', 'stript']),
        ('bus',     ['busses', 'buses'], ['bussing', 'busing'], ['bussed', 'bused'], ['bussed', 'bused']),
        ('combat',  ['combats'], ['combatting', 'combating'],['combatted', 'combated'], ['combatted', 'combated']),
        ('focus',   ['focuses', 'focusses'], ['focusing', 'focussing'],
                    ['focused', 'focussed'], ['focused', 'focussed']),

        # junk, not in CMU dict, should still return logical result
        ('zzz',     ['zzzs'],    ['zzzing'],      ['zzzed'],      ['zzzed']),
        ('',        [],          [],              [],             [])
    ]

    for vi in verb_inflections:
        base            = vi[0]
        truth_third     = vi[1]
        truth_pres_part = vi[2]
        truth_past      = vi[3]
        truth_past_part = vi[4]

        check_for_errors(base, truth_third, truth_pres_part,
                               truth_past,  truth_past_part)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)
        
###############################################################################
def show_help():
    log(get_version())
    log("""
    USAGE: python3 ./{0} -f <filename>  [-hvs]

    OPTIONS:

        -f, --file <quoted string>  path to truth data file, for testing

    FLAGS:

        -h, --help           log this information and exit.
        -v, --version        log version information and exit.
        -s, --selftest       Run self-tests and exit

    """.format(MODULE_NAME))
                    
###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-f', '--file', action='store',
                         dest='filepath')
    optparser.add_option('-v', '--version',  action='store_true',
                         dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true',
                         dest='show_help', default=False)
    optparser.add_option('-s', '--selftest', action='store_true',
                         dest='selftest')

    opts, other = optparser.parse_args(sys.argv)

    # show help if no command line arguments
    if opts.show_help or 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    if opts.get_version:
        log(get_version())
        sys.exit(0)

    if opts.selftest:
        run_tests()
        sys.exit(0)
        
    try:
        infile = open(opts.filepath, 'r')
    except Exception as e:
        log(e)
        sys.exit(-1)

    with infile:
        for line in infile:
            inflections = line.strip()
            pieces      = inflections.split(',')
            base        = pieces[0]

            # extract truth data
            truth_third     = pieces[1].split()
            truth_pres_part = pieces[2].split()
            truth_past      = pieces[3].split()
            truth_past_part = pieces[4].split()

            check_for_errors(base, truth_third, truth_pres_part,
                                   truth_past,  truth_past_part)
