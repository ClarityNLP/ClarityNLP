#!/usr/bin/env python3
"""

This is a module for finding and extracting Covid variants from text scraped
from the Internet.
"""

import os
import re
import csv
import sys
import json
import argparse
from collections import namedtuple

try:
    from algorithms.finder import finder_overlap as overlap
    #from algorithms.finder import text_number as tnum
except:
    this_module_dir = sys.path[0]
    pos = this_module_dir.find('/nlp')
    if -1 != pos:
        nlp_dir = this_module_dir[:pos+4]
        finder_dir = os.path.join(nlp_dir, 'algorithms', 'finder')
        sys.path.append(finder_dir)
        sys.path.append(nlp_dir)
    import finder_overlap as overlap
    #import text_number as tnum

# default value for all fields
EMPTY_FIELD = None

COVID_VARIANT_TUPLE_FIELDS = [
    'sentence',
    'covid',
    'possible',
    'related',
    'emerging',
    'spreading',
    'variant',
    'symptom',
    'severity',
    'case',
    'illness',
    'spike',
    'clade',
    'location',
    'setting',
    'pango',
    'british',
    'amino',
    'expr',
]
CovidVariantTuple = namedtuple('CovidVariantTuple', COVID_VARIANT_TUPLE_FIELDS)


_STATE_NAMES = [
    "Alaska", "Alabama", "Arkansas", "Arizona",
    "California", "Colorado", "Connecticut", "DC", "District of Columbia",
    "Delaware", "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois",
    "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland",
    "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana",
    "North Carolina", "North Dakota", "Nebraska", "New Hampshire",
    "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma",
    "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands",
    "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"
]
_str_states = r'\b(' + '|'.join(_STATE_NAMES) + r')'

_str_where = r'(count(y|ies)|residents?|person|people|brazil|' \
    r'india|(great )?britain|uk|' + _str_states + r')'

_str_tnum  = r'\b(one|two|three|four|five|six|seven|eight|nine|ten|' \
    r'eleven|twelve|twenty|thirty|forty|fifty|sixty|seventy|eighty|' \
    r'ninety|(a|one) hundred)'

# 'no' is needed for "no new cases" and similar
_str_enum = r'(first|second|third|fourth|fifth|sixth|seventh|eighth|' +\
    r'ninth|tenth|eleventh|twelfth|'                                  +\
    r'(thir|four|fif|six|seven|eight|nine)teenth|'                    +\
    r'1[0-9]th|[2-9]0th|[4-9]th|3rd|2nd|1st|'                         +\
    r'(twen|thir|for|fif|six|seven|eigh|nine)tieth)'

# Covid variants labeled with Greek letters
_GREEK_LETTERS = [
    'alpha', 'beta',  'gamma',  'delta',   'epsilon', 'zeta', 'eta',     'theta',
    'iota',  'kappa' ,'lambda', 'mu',      'nu',      'xi',   'omicron', 'pi',
    'rho',   'sigma', 'tau',    'upsilon', 'phi',     'chi',  'psi',     'omega'
]

_str_greek = r'\b(' + '|'.join(_GREEK_LETTERS) + r')\b'

_str_month = r'\b(january|february|march|april|may|june|july|august|'  \
    r'september|october|november|december|jan|feb|mar|apr|may|jun|jul|' \
    r'aug|sept|sep|oct|nov|dec)\b'


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 2

# set to True to enable debug output
_TRACE = False

# name of the file containing covid variant regexes
_VARIANT_REGEX_FILE = 'covid_variant_regexes.txt'

# regex for matching Covid-related clades (loaded at init)
_regex_clades = None

# regex for matching locations with known Covid variants (loaded at init)
_regex_locations = None

# regex for matching Covid variant lineages (loaded at init)
_regex_pango_lineage = None

# regex for matching amino acid mutations (loaded at init)
_regex_amino_mutations = None

# nongreedy word captures
_str_word = r'\s?[-a-z\'\d]+\s?'
_str_three_words = r'(' + _str_word + r'){3}'
_str_two_words   = r'(' + _str_word + r'){2}'
_str_one_word    = r'(' + _str_word + r'){1}'
_str_space       = r'\s?'
_str_words = r'(' + _str_three_words + r'|' + _str_two_words + \
    r'|' + _str_one_word + r'|' + _str_space + r')'

# integers, possibly including commas
# do not capture numbers in phrases such as "in their 90s", etc
# the k or m suffixes are for thousands and millions, i.e. 4k, 12m
_str_int = r'(?<!covid)(?<!covid-)(?<!\d)(\d{1,3}(,\d{3})+|' \
    r'(?<![,\d])\d+(k|m|\s?dozen)?(?!\d)(?!\'?s))'

# integer, numeric or textual
_str_num = r'(?<![-.])(' + _str_int + r'|' + _str_tnum + r')'

# spike protein
_str_spike = r'\bspike\s(glyco)?proteins?\b'
_regex_spike = re.compile(_str_spike, re.IGNORECASE)

# possible
_str_possible = r'\b(possible|potential(ly)?|probable|plausible|suspected|'   \
    r'suspicious|unexplained|((under|un)?reported|rumor(ed)?|report)s?( of)?|' \
    r'undisclosed|undetected|likely|may|alert)'
_regex_possible = re.compile(_str_possible, re.IGNORECASE)

# emerging
_str_emerging = r'\b(new|novel|unknown|myster(y|ious)|emerg(ed|ing)|' \
    r'emergen(t|ce)|detect(ed|ing)|appear(ed|ing)|detection of|'          \
    r'early stages of|appearance of|originat(ed|ing)|re-?emerge(d)?|' \
    r'(re-?)?activat(ed?|ing)|recurr(ing|ences?)|spotted|identified)'
_regex_emerging = re.compile(_str_emerging, re.IGNORECASE)

# related
_str_related = r'\b((related|linked|comparable) to|' \
    r'(relative|derivative|indicative|suggestive) of)'
_regex_related = re.compile(_str_related, re.IGNORECASE)

# spreading
_str_spread = r'\b(introduction|resurgen(ce|t)|surg(e|ing)|' \
    r'increase in frequency|increas(e[sd]|ing)|mutating|spread(ing)? widely|' \
    r'(wide|super-?)?spread(s|er|ing)?|becoming|' \
    r'(rapid|quick|exponential)ly( growing)?|on the rise|rise in|rise|ris(es|ing)|' \
    r'circulat(e[sd]|ing)|expand(s|ed|ing)|grow(n|s|ing)|progress(es|ing)|'  \
    r'ongoing|trend(s|ed|ing)|spark(s|ing)|balloon(s|ed|ing)|' \
    r'spill(ing|over)|sentinel|now in|'      \
    r'clustering|higher|greater|infectious)'
_regex_spread = re.compile(_str_spread, re.IGNORECASE)

# cases
_str_cases = r'\b(case (count|number)|case|cluster|outbreak|wave|infection|' \
    r'(pan|epi)demic|contagion|plague|disease|vir(us|al)|emergence|' \
    r'sickness|tested positive)s?'
_regex_cases = re.compile(_str_cases, re.IGNORECASE)

# severity
_str_severity = r'\b(more )?(antibody-?resistant|staggering|aggressive(ly)?|' \
    r'record-?breaking|severe|horrible situation|overwhelm(s|ed|ing)?|' \
    r'out of control|acute|uncontroll(ed|able)|tipping point|despair|'  \
    r'highly infectious|dangerous|deadl(y|ier)|transmissible' \
    r'contagious|spread(s|ing)? fast(er)?|increase(d| the) risk of death|' \
    r'deadly|cause(ed|ing|s)? (of )?concern|(major )?concerns?|ban travel|' \
    r'travel ban)'
_regex_severity = re.compile(_str_severity, re.IGNORECASE)

# symptoms
_str_symptoms = r'\b(cough(ing)?|fever(ish)?|chills?|respirat(ory|ion)|'      \
    r'short(ness)? of breath|difficulty breathing|fatigue|'    \
    r'(muscle|body) aches?|loss of (taste|smell)|sore throat|' \
    r'high temp\.?(erature)?|diarrhea|bluish|dyspnea|hypoxia|'   \
    r'respiratory failure|multiorgan dysfunction|complications)'
_regex_symptoms = re.compile(_str_symptoms, re.IGNORECASE)

# illness
_str_illness = r'\b(contracted|caught|c[ao]me down with|(fallen|fell|' \
    r'bec[ao]me) ill|ill(ness)?|developed)\b'
_regex_illness = re.compile(_str_illness, re.IGNORECASE)

# match mention of variants
_str_variants = r'\b(variants? of (concern|interest|high consequence)|'       \
    r'variant|mutation|mutant|strain|change|substitution|deletion|insertion|' \
    'stop\sgain(ed)?|(sub-?)?lineage|clade)s?'
_regex_variant = re.compile(_str_variants, re.IGNORECASE)

# find various forms of Covid-19
#    <covid names> SARS-CoV-2, hCoV-19, covid-19, coronavirus, ...
_str_covid = r'(sars-cov-2|hcov-19|covid([-\s]?19)?|(novel\s)?coronavirus)' \
    r'( virus)?'
_regex_covid = re.compile(_str_covid, re.IGNORECASE)

_str_setting = r'\b(ship|boat|vessel|(nursing|care|retirement) home|hospital|'  \
    r'(long-?term|residential) care (facilit(y|ies)|home)|ltc|' \
    r'multicare (facilit(y|ies)|home)|skilled nursing facilit(y|ies)|' \
    r'congregate living (facilit(y|ies)|home)|' \
    r'assisted-?living (facilit(y|ies)|home)|alf|workplace|office|building|' \
    r'bus|ferry|train|jail|correctional facilit(y|ies)|prison|' \
    r'(child|day) care facilit(y|ies)|kindergarten|gym|fair|festival|concert|' \
    r'rave|club|preschool|daycare|k-12|' \
    r'hotel|motel|casino|bar|construction site|church|synagogue|temple|' \
    r'wedding|(bar|bat) mitzvah|reception|party|celebration|funeral|' \
    r'plant|warehouse|factory|industrial setting|' \
    r'school|college|university|campus|(air)?plane|flight|camp|hot spot)s?\b'
_regex_setting = re.compile(_str_setting, re.IGNORECASE)

# Lineage Nomenclature from Public Health England

# old format: V(UI|OC)-YYYYMM/NN, i.e. VUI-202101/01, # NN is a two-digit int
_str_british1 = r'\bv(oc|ui)\-?202[0-9](0[1-9]|1[1-2])/(0[1-9]|[1-9][0-9])'

# new format: V(UI|OC)-YYMMM-NN, i.e. VUI-21JAN-01
_str_british2 = r'\bv(oc|ui)\-?2[0-9]' \
    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\-(0[1-9]|[1-9][0-9])'

_str_british_lineage = r'((' + _str_british1 + r')|(' + _str_british2 + r'))'
_regex_british_lineage = re.compile(_str_british_lineage, re.IGNORECASE)

# month followed by number
_str_day_of_month = _str_month + r'\s?' + r'(' + _str_enum + r'|' + _str_num + r')'
_regex_day_of_month = re.compile(_str_day_of_month, re.IGNORECASE)

# simpler regex to identify pango lineage designations in the following regexes
str_lin = r'\b[a-z]{1,2}(\.\d+)*\b(?!%)'

#<num> <words> cases?
#_str0 = r'(from )?' + _str_num + _str_words + 'cases?' +
_str0 = r'(from )?' + _str_num + _str_words + _str_cases + \
    r'( to ' + r'(\d+|' + _str_tnum + r'))?'
_regex0 = re.compile(_str0, re.IGNORECASE)

#<num> <words> <covid-19> <variant|lineage>+ <words> in
_str1 = r'(\ba\b|' + _str_num + r')' + _str_words + _str_covid + r'\s?' + \
    r'(' + _str_variants + r'\s?|' + str_lin + r'\s?)' + \
    _str_words + r'\bin\b' + r'(' + _str_words + _str_where + r')?'
_regex1 = re.compile(_str1, re.IGNORECASE)

#<num> <words> cases? of <words> <covid-19> <variant|lineage>+
_str2 = r'(\ba\b|' + _str_num + r')' + _str_words + r'cases? of' + _str_words + \
    _str_covid + r'\s?' + \
    r'(' + _str_variants + r'\s?|' + str_lin + r'\s?)'
_regex2 = re.compile(_str2, re.IGNORECASE)

# <identified> <words> cases? of <words> variant
_str3 = r'\b(identified|found|detected|confirmed)' + _str_words + \
    r'cases? of' + _str_words + r'\bvariants?'
_regex3 = re.compile(_str3, re.IGNORECASE)

#<variant> <words> (identified|detected|found|discovered|reported|originated) in
# <words> (count(y|ies)|residents?)
_str4 = _str_variants + _str_words + r'(' + _str_covid + _str_words + r')?' \
    r'(found|(identifi|detect|discover|report|confirm|observ|originat|' \
    r'suspect|fear)ed) in' + r'(' + _str_words + _str_where + r')?'
_regex4 = re.compile(_str4, re.IGNORECASE)

#<num> <words> cases? of <words> <lineage> <variant>
_str5 = r'(\ba |' + _str_num + r')' + _str_words + r'cases? of' + _str_words + \
    str_lin + r'\s?' + _str_variants
_regex5 = re.compile(_str5, re.IGNORECASE)

#the <words> variant
_str6 = r'\bthe\b' + _str_words + _str_variants
_regex6 = re.compile(_str6, re.IGNORECASE)

# <related> <words> <variant>
_str7 = _str_related + _str_words + _str_variants
_regex7 = re.compile(_str7, re.IGNORECASE)

# <possible>? <spreading> <words> <variant>
_str8 = r'(' + _str_possible + r'\s?)?' + _str_spread + \
    _str_words + _str_variants
_regex8 = re.compile(_str8, re.IGNORECASE)

# first reported cases and similar
_str9 = _str_enum + _str_words + _str_cases
_regex9 = re.compile(_str9, re.IGNORECASE)

# severity of spread
_str10 = _str_spread + _str_words + _str_severity
_regex10 = re.compile(_str10, re.IGNORECASE)

# named variants
_str11 = _str_greek + _str_words + _str_variants
_regex11 = re.compile(_str11, re.IGNORECASE)

_REGEXES = [
    _regex0,
    _regex1,
    _regex2,
    _regex3,
    _regex4,
    _regex5,
    _regex6,
    _regex7,
    _regex8,
    _regex9,
    _regex10,
    _regex11,
]


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def init():
    """
    Load the file containing regex strings for Covid variant clades, locations,
    and lineages. Return a Boolean indicating success or failure.
    """

    global _regex_clades
    global _regex_locations
    global _regex_pango_lineage
    global _regex_amino_mutations

    # construct path to the regex file to be loaded
    cwd = os.getcwd()
    filepath = os.path.join(cwd, _VARIANT_REGEX_FILE)
    if not os.path.isfile(filepath):
        # running ClarityNLP
        this_module_dir = sys.path[0]
        pos = this_module_dir.find('/nlp')
        if -1 != pos:
            nlp_dir = this_module_dir[:pos+4]
            finder_dir = os.path.join(nlp_dir, 'algorithms', 'finder')
            filepath = os.path.join(finder_dir, _VARIANT_REGEX_FILE)
    
    # load the regex file and compile the regexes for locations and lineages
    with open(filepath, 'rt') as infile:
        for line_idx, line in enumerate(infile):
            if 0 == len(line):
                continue
            text = line.strip()

            # line 0 is the 'clades' regex string
            # line 1 is blank
            # line 2 is the 'locations' regex string
            # line 3 is blank
            # line 4 is the pango lineage regex string
            # line 6 is the amino acid mutation string
            if 0 == line_idx:
                _regex_clades = re.compile(text, re.IGNORECASE)
            elif 2 == line_idx:
                _regex_locations = re.compile(text, re.IGNORECASE)
            elif 4 == line_idx:
                _regex_pango_lineage = re.compile(text, re.IGNORECASE)
            elif 6 == line_idx:
                _regex_amino_mutations = re.compile(text, re.IGNORECASE)

    if _regex_clades is None or _regex_locations is None or \
       _regex_pango_lineage is None or _regex_amino_mutations is None:
        return False

    return True
            

###############################################################################
def _erase(sentence, start, end):
    """
    Replace sentence[start:end] by whitespace.
    """

    chunk1 = sentence[:start]
    chunk2 = ' '*(end - start)
    chunk3 = sentence[end:]
    return chunk1 + chunk2 + chunk3


###############################################################################
def _split_at_positions(text, pos_list):
    """
    Split a string at the list of positions in the string and return a list
    of chunks.
    """

    chunks = []
    prev_end = 0
    for pos in pos_list:
        chunk = text[prev_end:pos]
        chunks.append(chunk)
        prev_end = pos
    chunks.append(text[prev_end:])
    return chunks


###############################################################################
def _cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # convert to lowercase
    sentence = sentence.lower()

    # insert a missing space prior to a virus-related word
    space_pos = []
    iterator = re.finditer(r'[a-z\d](covid|coronavirus)', sentence, re.IGNORECASE)
    for match in iterator:
        # position where the space is needed
        pos = match.start() + 1
        space_pos.append(pos)
    chunks = _split_at_positions(sentence, space_pos)
    sentence = ' '.join(chunks)
    
    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)

    # erase days of the month such as 'April 4'
    iterator = _regex_day_of_month.finditer(sentence)
    for match in iterator:
        sentence = _erase(sentence, match.start(), match.end())
        if _TRACE:
            print('{0}'.format(sentence))
    
    # erase certain characters
    #entence = re.sub(r'[\']', '', sentence)
    
    # replace selected chars with whitespace
    sentence = re.sub(r'[&{}\[\]:~@;?]', ' ', sentence)
    
    #sentence = _erase_dates(sentence)
    #sentence = _erase_time_expressions(sentence)
    
    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


###############################################################################
def _find_matches(sentence, regex, display_text):
    """
    Find all matches for the given regex and return a list of match objects.
    """

    matchobj_list = []
    
    iterator = regex.finditer(sentence)
    for match in iterator:
        match_text = match.group()
        matchobj_list.append(match)

    return matchobj_list
        

###############################################################################
def _to_result_string(matchobj_list):
    """
    Extract the matching text from a list of match objects and return a comma-
    separated string containing the *unique* texts.
    """

    texts = set()
    for obj in matchobj_list:
        text = obj.group()
        texts.add(text)

    texts = sorted(list(texts))
    return ','.join(texts)


###############################################################################
def run(sentence):
    """
    """

    cleaned_sentence = _cleanup(sentence)

    covid_matchobjs     = _find_matches(cleaned_sentence, _regex_covid, 'COVID')
    possible_matchobjs  = _find_matches(cleaned_sentence, _regex_possible, 'POSSIBLE')
    related_matchobjs   = _find_matches(cleaned_sentence, _regex_related, 'RELATED')
    emerging_matchobjs  = _find_matches(cleaned_sentence, _regex_emerging, 'EMERGING')
    spreading_matchobjs = _find_matches(cleaned_sentence, _regex_spread, 'SPREADING')
    variant_matchobjs   = _find_matches(cleaned_sentence, _regex_variant, 'VARIANT')
    symptom_matchobjs   = _find_matches(cleaned_sentence, _regex_symptoms, 'SYMPTOMS')
    severity_matchobjs  = _find_matches(cleaned_sentence, _regex_severity, 'SEVERITY')
    case_matchobjs      = _find_matches(cleaned_sentence, _regex_cases, 'CASES')
    illness_matchobjs   = _find_matches(cleaned_sentence, _regex_illness, 'ILLNESS')
    spike_matchobjs     = _find_matches(cleaned_sentence, _regex_spike, 'SPIKE')
    clade_matchobjs     = _find_matches(cleaned_sentence, _regex_clades, 'CLADE')
    location_matchobjs  = _find_matches(cleaned_sentence, _regex_locations, 'LOCATION')
    setting_matchobjs   = _find_matches(cleaned_sentence, _regex_setting, 'SETTING')
    pango_matchobjs     = _find_matches(cleaned_sentence, _regex_pango_lineage, 'PANGO')
    british_matchobjs   = _find_matches(cleaned_sentence, _regex_british_lineage, 'BRITISH')
    amino_matchobjs     = _find_matches(cleaned_sentence, _regex_amino_mutations, 'AMINO')

    str_covid    = _to_result_string(covid_matchobjs)
    str_possible = _to_result_string(possible_matchobjs)
    str_related  = _to_result_string(related_matchobjs)
    str_emerg    = _to_result_string(emerging_matchobjs)
    str_spread   = _to_result_string(spreading_matchobjs)
    str_var      = _to_result_string(variant_matchobjs)
    str_symptom  = _to_result_string(symptom_matchobjs)
    str_severity = _to_result_string(severity_matchobjs)
    str_case     = _to_result_string(case_matchobjs)
    str_ill      = _to_result_string(illness_matchobjs)
    str_spike    = _to_result_string(spike_matchobjs)
    str_clade    = _to_result_string(clade_matchobjs)
    str_loc      = _to_result_string(location_matchobjs)
    str_setting  = _to_result_string(setting_matchobjs)
    str_pango    = _to_result_string(pango_matchobjs)
    str_brit     = _to_result_string(british_matchobjs)
    str_amino    = _to_result_string(amino_matchobjs)

    
    candidates = []

    for i, regex in enumerate(_REGEXES):
        iterator = regex.finditer(cleaned_sentence)
        for match in iterator:
            match_text = match.group().rstrip()
            start = match.start()
            end = start + len(match_text)
            candidates.append(overlap.Candidate(start, end, match_text, regex, other=match))

            if _TRACE:
                print('[{0:2}]: [{1:3}, {2:3})\tMATCH TEXT: ->{3}<-'.
                      format(i, start, end, match_text))
                print('\tmatch.groupdict entries: ')
                for k,v in match.groupdict().items():
                    print('\t\t{0} => {1}'.format(k,v))
            
    # sort candidates in decreasing order of length
    candidates = sorted(candidates, key=lambda x: x.end-x.start, reverse=True)
    pruned_candidates = overlap.remove_overlap(candidates, _TRACE, keep_longest=True)

    pruned_candidates = sorted(pruned_candidates, key=lambda x: x.start)
    texts = [candidate.match_text for candidate in pruned_candidates]
    expr = ','.join(texts)
    
    obj = CovidVariantTuple(
        sentence  = sentence,
        covid     = str_covid,
        possible  = str_possible,
        related   = str_related,
        emerging  = str_emerg,
        spreading = str_spread,
        variant   = str_var,
        symptom   = str_symptom,
        severity  = str_severity,
        case      = str_case,
        illness   = str_ill,
        spike     = str_spike,
        clade     = str_clade,
        location  = str_loc,
        setting   = str_setting,
        pango     = str_pango,
        british   = str_brit,
        amino     = str_amino,
        expr      = expr,
    )

    # if _TRACE:
    #     objdict = obj._asdict()
    #     maxlen = max([len(k) for k in objdict.keys()])
    #     for k,v in objdict.items():
    #         if 'sentence' != k:
    #             print('\t{0:>{1}} : {2}'.format(k, maxlen, v))

    return json.dumps(obj._asdict(), indent=4)


###############################################################################
def _print_results(sentences):
    
    for i, sentence in enumerate(sentences):
        print('[[{0:4}]] '.format(i))
        print('{0}'.format(sentence))
        json_string = run(sentence)
        obj = json.loads(json_string)

        maxlen = max([len(k) for k in obj.keys()])
        for k,v in obj.items():
            if 'sentence' != k:
                print('\t{0:>{1}} : {2}'.format(k, maxlen, v))


###############################################################################
def _run_tests():

    SENTENCES = [
        'The B.1.1.7, B.1.351, P.1, B.1.427, and B.1.429 variants '      \
        'circulating in the United States are classified as variants '   \
        'of concern.',
        
        'To date, no variants of high consequence have been identified ' \
        'in the United States.',

        'In laboratory studies, specific monoclonal antibody treatments ' \
        'may be less effective for treating cases of COVID-19 caused by ' \
        'variants with the L452R or E484K substitution in the spike protein.',

        'L452R is present in B.1.526.1, B.1.427, and B.1.429.',
        'E484K is present in B.1.525, P.2, P.1, and B.1.351, but only some ' \
        'strains of B.1.526 and B.1.1.7.',

        'This variant is a cluster of B.1.1.7 (VOC202012/01) that contains ' \
        'E484K and is associated with the Bristol area',

        'An unknown Covid-19 variant has emerged in the latest survey',

        'At this moment, major clades from 2020 onwards are: 20I/501Y.V1: ' \
        'derived from 20B bearing S 501Y, S 570D, S 681H, ORF8 27*, ' \
        'concentrated in the United Kingdom.',

        'Alternatively, Nextstrain divides the SARS-CoV-2 strains into 19A, ' \
        '19B, 20A, 20B, 20C, 20D, 20E, 20F, 20G, 20H, 20I, 20 J. ',

        'Within these clades, 19B is the original reference strain. ' \
        '20I/501Y.V1 refers to the B.1.1.7 variant that originated in ' \
        'Britain; 20H/501Y.V2 refers to the B.1.351 strain that originated ' \
        'in South Africa; and 20J/501Y.V3 refers to the P.1 strain that ' \
        'originated and spread from Brazil.',

        'new outbreak of covid cases in Brazil',
        'authorities reported the appearance of two distinct clusters of suspected Covid-19',
        'rumors of a suspected covid outbreak have residents worried',
        'potential novel SARS-CoV-2 variant of interest identified in Germany',
        'reports of rising case counts of an unknown respiratory illness',

        'First reported cases of SARS-CoV-2 sub-lineage B.1.617.2 in Brazil: ' \
        'an outbreak in a ship and alert for spread',
        
        'concerned about a possible COVID-19 outbreak after two coaches ' \
        'tested positive for the virus',

        'Proposal of two new lineages from B.1.1 that seem to rapidly ' \
        'increase in frequency in Russia proposed ',

        'A New Potential lineage (T.1) specifically located in Campania, ' \
        'Italy, is spreading exponentially.',

        'Possible new emerging sub-lineage under recently designated lineage B.1.617',
        'Sublineage of B.1.351 spreading rapidly in Bangladesh',

        'DHSS and the CDC are responding to an outbreak of respiratory disease ' \
        'caused by a novel (new) coronavirus ',

        'hawaii has gone from one covid-19 variant case to twelve',

        'two cases of brazil covid-19 variant found in louisiana baton rouge, ' \
        'la.-- the louisiana department of health confirmed on thursday two ' \
        'identified cases of the sars-cov-2 virus known as the brazil ' \
        'p.1 variant in louisiana.',

        'sentinel testing found a case of the p.1 variant in pennington county.',
        
        'First reported cases of SARS-CoV-2 sub-lineage B.1.617.2 in Brazil: ' \
        'an outbreak in a ship and alert for spread',

        'B.1.617.2 subclade with N:G215C; may be spreading more aggressively ' \
        'than the rest of B.1.617.2.',

        'The delta variant has grown at the fastest rate of any of the other ' \
        'variants that have appeared.',

        'The new outbreak has been traced to a wedding from four weeks ago',

        '21 infected in 8 new coronavirus outbreaks at schools, says ' \
        'Michigan’s June 7 and March 8th school outbreak report',

        'A rapidly growing outbreak of variant COVID-19 among people ' \
        r'in Carver County',
    ]

    _print_results(SENTENCES)
    

###############################################################################
if __name__ == '__main__':

    if not init():
        print('*** init() failed ***')
        sys.exit(-1)
        
    parser = argparse.ArgumentParser(
        description='Run tests on the Covid variant finder module')

    parser.add_argument('-v', '--version',
                        help='show version and exit',
                        action='store_true')

    parser.add_argument('-d', '--debug',
                        help='print debug information to stdout',
                        action='store_true')

    parser.add_argument('-f', '--file',
                        help='path to Covid scraper CSV result file',
                        dest='filepath')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    if 'debug' in args and args.debug:
        enable_debug()

    _run_tests()
    sys.exit(0)
        
    if args.filepath is None:
        print('\n*** Missing --file argument ***')
        sys.exit(-1)

    filepath = args.filepath
    if not os.path.isfile(filepath):
        print('\n*** File not found: "{0}" ***'.format(filepath))
        sys.exit(-1)

    unique_sentences = set()
    with open(filepath, newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            sentence = row['sample_sentence']
            cleaned_sentence = _cleanup(sentence)
            unique_sentences.add(cleaned_sentence)

    sentences = sorted(list(unique_sentences), key=lambda x: len(x), reverse=True)
    _print_results(sentences)
    

    # find <location> variant, i.e. <South African> variant
    #   search for place name with variant|strain|mutation
    # 'mink' is also important to search for
    # spike protein substitutions (E484K and others)


"""

    References:
    https://en.wikipedia.org/wiki/Variants_of_SARS-CoV-2
    https://www.gov.uk/government/publications/covid-19-variants-genomically-confirmed-case-numbers/variants-distribution-of-cases-data
    https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/979818/Variants_of_Concern_VOC_Technical_Briefing_9_England.pdf
    https://cov-lineages.org/index.html
    https://github.com/phe-genomics/variant_definitions
    virological.org

    This page has everything:
        https://nextstrain.org/ncov/global?f_pango_lineage=A

    <covid names> SARS-CoV-2, hCoV-19, covid-19, coronavirus, ...

    VOC = variants? of concern
    VUI = variants? under investigation

    new format: V(UI|OC)-YYMMM-NN, i.e. VUI-21JAN-01; NN is a sequential two-digit number
    r'v(oc|ui)\-(2[0-9])(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\-(0[1-9]|[1-9][0-9])'

    old format: V(UI|OC)-YYYYMM/NN, i.e. VUI-202101/01
    r'v(oc|ui)\-202[0-9])(0[1-9]|1[1-2])/(0[1-9]|[1-9][0-9])'

    VOC-20DEC-01
    VOC-20DEC-02
    VUI-21JAN-01
    VOC-21JAN-02
    VUI-21FEB-01
    VOC-21FEB-02
    VUI-21FEB-03
    VUI-21FEB-04
    VUI-21MAR-01
    VUI-21MAR-02
    VUI-21APR-01
    VUI-21APR-03
    VUI-21APR-03

    VOC-202012/01
    VOC-202012/02
    VUI-202101/01
    VOC-202101/02
    VUI-202102/01
    VOC-202102/02
    VUI-202102/03
    VUI-202102/04

    Lineages:

    A.27
    B.1
    B.1.1 with L452Q and F490S
    B.1.240
    B.1.429
    B.1.608
    B.1.1.7
    B.1.1.7 with S494P
    B.1.1.7 with Q677H
    B.1.1.28 with N501T and E484Q
    B.1.1.144
    B.1.1.222
    B.1.351
    B.1.1.7 with E484K
    B.1.1.318
    B.1.324.1 with E484K
    B.1.525 (previously UK1188)
    B.1.526
    B.1.617.1 with E484Q
    B.1.617.2
    B.1.617.3
    B.1.429
    B.1.214.2
    501Y.V2
    P.2
    P.1
    P.3
    A.23.1 with E484K
    R.1
    C.36
    AV.1
    R346K
    T478R
    E484K (catchall for sequences with the E484K spike variant)
    

    20I/501Y.V1 == VOC 202012/01 == B.1.1.7
    20H/501Y.V2 == B.1.351
    20J/501Y.V3 == P.1 (Brazil variant)
    B.1.1.207 lineage
    SARS-CoV-2 501Y.V2
    SARS-CoV-2 VOC†202012/01†(B.1.1.7)

    SARS-CoV-2 Strain Surveillance (“NS3”)

    SARS-CoV-2
    coronavirus 2
    severe acute respiratory syndrome-related

    SARS-CoV-2 spike
    SARS-CoV-2 spike protein variants

    spike D614G

    SARS-CoV-2 variant(s)
    resistance of SARS-CoV-2 variants B.1.351 and B.1.1.7
    neutralization of SARS-CoV-2 lineage B.1.1.7 pseudovirus
    Novel SARS-CoV-2 variant of concern
    spike protein
    multiple spike mutations
    reinfection case with E484K SpikeMutation
    spike mutation D614G alters SARS-CoV-2 fitness
    spike E484K mutation
    N501Y mutant SARS-CoV-2
    N501Y mutant strains of SARS-CoV-2 in the United Kingdom

    <SARS-CoV-2 in sentence> .... worldwide emerging P681H
    emergence of a highly fit SARS-CoV-2 variant
    emergence of SARS-CoV-2 B.1.1.7 lineage
    emergence of VUI-NP13L 
    emergent SARS-CoV-2 lineage in Manaus
    emerging SARS-CoV-2 variants
    transmission of E484K
    mutations arising in SARS-CoV-2 spike
    mutation in the receptor binding domain (RBD) of the spike protein
    SARS-CoV-2 RBD mutations
    RBD and HR1 mutations associated with SARS-CoV-2 spike glycoprotein

    detection of SARS-CoV-2 P681H spike protein variant in Nigeria

    variant of concern (VOC)
    identified another new variant of coronavirus
    highly contagious COVID-19 variant
    infection with B.1.1.7 variant 
    S-variant SARS-CoV-2
    S-variant SARS-CoV-2 lineage B1.1.7
    SARS-CoV-2 lineage B.1.1.7 (VOC 2020212/01)
    SARS-CoV-2 lineage B.1.526
    variants of SARS-CoV-2
    novel SARS-CoV-2 spike variant
    a SARS-CoV-2 lineage a variant (A.23.1) with altered spike
    genetic variants of SARS-CoV-2
    screen for SARS-COV-2 B.1.1.7, B.1.351, and P.1 variants of concern

    SARS-CoV-2 501Y.V2
    new coronavirus variant
    SARS-CoV-2 strain
    SARS-CoV-2 strain of P.1 lineage
    SARS-CoV-2 variants carrying E484K 
    SARS-CoV-2 spike D614G change
    a B.1.526 variant containing an E484K mutation in New York State
    a novel SARS-CoV-2 variant of concern, B.1.526, identified in new york
    SARS-CoV-2 variants
    SARS-CoV-2 B.1.1.7
    SARS-CoV-2 B.1.1.7 variant
    SARS-CoV-2 lineage B.1.1.7
    SARS-CoV-2 variant VOC-202012/01
    SARS-CoV-2 variants B.1.351 and B.1.1.248
    SARS-CoV-2 B.1.1.7 and B.1.351 spike variants
    SARS-CoV-2 mutations
    SARS-CoV-2 variants bearing mutations in the RdRp gene
    new SARS-CoV-2 variant discovered in Japan
    multiple lineages of SARS-CoV-2 Spike protein variants

    the trajectory of the B.1.1.7 variant
    in this model, B.1.1.7 prevalence is initially low
    evidence that D614G increases infectivity of the COVID-19 virus

  
    find mention of <covid>
    find mention of <variant, mutation, strain>
    find mention of <lineage>
    find mention of <amino acid change>

    (possible|potential) <new> <emerging> <lineage, sub-lineage, sublineage, clade, subclade>
    (introduction|emergence|resurgence) (and spread of )?<covid> in <location>
    spread of endemic <covid>
    (spreading|spotted|circulating|(rapidly )?growing|(currently )?expanding) <exponentially>? in <location>
    local cluster in <location>
    <number> of cases in less than <timespan>
    <covid> reinfection by <variant> in <location>
    early stages of <covid> outbreak
    <covid> spikes
    detection of <lineage, covid, variant> in <location>


    <num> == one, two, first, second, etc.

    <num> <words> <covid-19> <variant|lineage>+ <words> in
    <num> <words> cases?
    <num> <words> cases? of <words> <covid-19> <variant|lineage>+
    <num> <words> cases? of <words> <covid-19> <variant|lineage>+ <words> in

    cases? of <words> <covid-19> <variant|lineage>+

    identified <words> variant

    covid-19 surge
    record-breaking outbreak
    multiple variants of concern
    circulating in
    new variant(s)
    new variant of coronavirus
    indian variant
    united kingdom variant
    brazillian covid-19 variant
    <location variant> of covid-19
    antibody-resistant variant of covid-19
    covid-19 variant detected in <location>
    covid-19 variant identified in <location>
    found a case of the p.1 variant
    new variant found in mesa county

    *one case of a covid-19 variant found in india has been identified
    *two cases of brazil covid-19 variant found in <location>
    *two identified cases of the sars-cov-2 virus known as the brazil p.1 variant in <location>
    *first known case of india covid variant
    #two cases of sars-cov-2 b.1.617 were found in iowa
    first reported indian covid-19 variant detected in louisiana
    first two identified cases
    identified the first two cases of the covid-19 variant first seen in india
    first of the brazilian variant
    identified a variant
    identified a variant thats similar to
    predominant strain
    more contagious covid-19 variant from <location>
    *identified first cases of <indian variant>
    *identified the states first two cases of a covid-19 variant


    detected in <location>
    a case of the covid-19 variant first identified in brazil has been detected in elmore county
    brazilian covid-19 variant detected in milam county
    india variant of covid-19 confirmed in two iowa residents
    india covid-19 variant found in ada county resident
    11 variants have been discovered in maine
    has been found in <location> county
 
    spread to other countries
    spreads? easier
    spreading to
    spreads faster
    spread widely
    spread of variants
    likely circulating
    seen a rise in cases
    devastating rise in infections
    significantly more contagious
    overwhelm healthcare systems
    coronavirus spike


"""
