#!/usr/bin/env python3
"""

This is a module for finding and extracting Covid variants from text scraped
from the Internet.

Test the module by running the test suite in test_finder.py.
"""

import os
import re
import sys
import json
from collections import namedtuple

# try:
#     # for normal operation via NLP pipeline
#     from algorithms.finder.date_finder import run as \
#         run_date_finder, DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
#     from algorithms.finder import finder_overlap as overlap
#     from algorithms.finder import text_number as tnum
# except:
#     this_module_dir = sys.path[0]
#     pos = this_module_dir.find('/nlp')
#     if -1 != pos:
#         nlp_dir = this_module_dir[:pos+4]
#         finder_dir = os.path.join(nlp_dir, 'algorithms', 'finder')
#         sys.path.append(finder_dir)    
#     from date_finder import run as run_date_finder, \
#         DateValue, EMPTY_FIELD as EMPTY_DATE_FIELD
#     import finder_overlap as overlap
#     import text_number as tnum


# default value for all fields
EMPTY_FIELD = None

COVID_VARIANT_TUPLE_FIELDS = [
    'sentence',
    'text'
]
CovidVariantTuple = namedtuple('CovidVariantTuple',
                               COVID_VARIANT_TUPLE_FIELDS)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = True

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

# spike protein
_str_spike = r'\bspike\s(glyco)?proteins?'
_regex_spike = re.compile(_str_spike, re.IGNORECASE)

# emerging
_str_emerging = r'\b(new|novel|unknown|emerg(ed|ing)|emergen(t|ce))'
_regex_emerging = re.compile(_str_emerging, re.IGNORECASE)

# match mention of variants
_str_variants = r'\b(variants? of (concern|interest|high consequence)|' \
    r'variant|(missense\s)?mutation|strain|change|lineage|clade)s?'
_regex_variant = re.compile(_str_variants, re.IGNORECASE)

# find various forms of Covid-19
#    <covid names> SARS-CoV-2, hCoV-19, covid-19, coronavirus, ...
_str_covid = r'(sars-cov-2|hcov-19|covid([-\s]?19)?|(novel\s)?coronavirus)'
_regex_covid = re.compile(_str_covid, re.IGNORECASE)

# Lineage Nomenclature from Public Health England

# old format: V(UI|OC)-YYYYMM/NN, i.e. VUI-202101/01, # NN is a two-digit int
_str_british1 = r'\bv(oc|ui)\-?202[0-9](0[1-9]|1[1-2])/(0[1-9]|[1-9][0-9])'

# new format: V(UI|OC)-YYMMM-NN, i.e. VUI-21JAN-01
_str_british2 = r'\bv(oc|ui)\-?2[0-9]' \
    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\-(0[1-9]|[1-9][0-9])'

_str_british_lineage = r'((' + _str_british1 + r')|(' + _str_british2 + r'))'
_regex_british_lineage = re.compile(_str_british_lineage, re.IGNORECASE)


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
    
    # load the regex file and compile the regexes for locations and lineages
    with open(_VARIANT_REGEX_FILE, 'rt') as infile:
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
    else:
        return True
            
    
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
    iterator = re.finditer(r'[a-z\d](covid|coronavirus)',
                           sentence, re.IGNORECASE)
    for match in iterator:
        # position where the space is needed
        pos = match.start() + 1
        space_pos.append(pos)
    chunks = _split_at_positions(sentence, space_pos)
    sentence = ' '.join(chunks)
    
    # replace ' w/ ' with ' with '
    sentence = re.sub(r'\sw/\s', ' with ', sentence)

    # erase certain characters
    sentence = re.sub(r'[\']', '', sentence)
    
    # replace selected chars with whitespace
    sentence = re.sub(r'[&{}\[\]:~@;]', ' ', sentence)
    
    # # replace commas with whitespace if not inside a number (such as 32,768)
    # comma_pos = []
    # iterator = re.finditer(r'\D,\D', sentence, re.IGNORECASE)
    # for match in iterator:
    #     pos = match.start() + 1
    #     comma_pos.append(pos)
    # chunks = _split_at_positions(sentence, comma_pos)
    # # strip the comma from the first char of each chunk, if present
    # for i in range(len(chunks)):
    #     if chunks[i].startswith(','):
    #         chunks[i] = chunks[i][1:]
    # sentence = ' '.join(chunks)

    #sentence = _erase_dates(sentence)
    #sentence = _erase_time_expressions(sentence)
    
    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    if _TRACE:
        #print('\tsentence after cleanup: "{0}"'.format(sentence))
        print('{0}'.format(sentence))
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
        #if _TRACE:
        #    print('\t{0}: "{1}"'.format(display_text, match_text))
        matchobj_list.append(match)

    return matchobj_list
        

###############################################################################
def _to_result_string(matchobj_list):
    """
    Extract the matching text from a list of match objects and return a comma-
    separated string containing the texts.
    """

    texts = []
    for obj in matchobj_list:
        text = obj.group()
        texts.append(text)

    return ','.join(texts)


###############################################################################
def run(sentence):
    """
    """

    cleaned_sentence = _cleanup(sentence)

    covid_matchobjs = _find_matches(cleaned_sentence, _regex_covid, 'COVID')
    emerging_matchobjs = _find_matches(cleaned_sentence, _regex_emerging, 'EMERGING')
    variant_matchobjs = _find_matches(cleaned_sentence, _regex_variant, 'VARIANT')
    spike_matchobjs = _find_matches(cleaned_sentence, _regex_spike, 'SPIKE')
    clade_matchobjs = _find_matches(cleaned_sentence, _regex_clades, 'CLADE')
    location_matchobjs = _find_matches(cleaned_sentence, _regex_locations, 'LOCATION')
    pango_matchobjs = _find_matches(cleaned_sentence, _regex_pango_lineage, 'PANGO')
    british_matchobjs = _find_matches(cleaned_sentence, _regex_british_lineage, 'BRITISH')
    amino_matchobjs   = _find_matches(cleaned_sentence, _regex_amino_mutations, 'AMINO')

    str_covid = _to_result_string(covid_matchobjs)
    str_emerg = _to_result_string(emerging_matchobjs)
    str_var   = _to_result_string(variant_matchobjs)
    str_spike = _to_result_string(spike_matchobjs)
    str_clade = _to_result_string(clade_matchobjs)
    str_loc   = _to_result_string(location_matchobjs)
    str_pango = _to_result_string(pango_matchobjs)
    str_brit  = _to_result_string(british_matchobjs)
    str_amino = _to_result_string(amino_matchobjs)

    obj = {
        'sentence' : sentence,
        'covid'    : str_covid,
        'emerging' : str_emerg,
        'variant'  : str_var,
        'spike'    : str_spike,
        'clade'    : str_clade,
        'location' : str_loc,
        'pango'    : str_pango,
        'british'  : str_brit,
        'amino'    : str_amino,        
    }

    if _TRACE:
        maxlen = max([len(k) for k in obj.keys()])
        for k,v in obj.items():
            if 'sentence' != k:
                print('\t{0:>{1}} : {2}'.format(k, maxlen, v))
    
    
###############################################################################
if __name__ == '__main__':

    
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
    ]

    if not init():
        print('*** init() failed ***')
        sys.exit(-1)

    # find <location> variant, i.e. <South African> variant
    #   search for place name with variant|strain|mutation
    # 'mink' is also important to search for
    # spike protein substitutions (E484K and others)

    for i, sentence in enumerate(SENTENCES):
        print('[{0:3}]: '.format(i))
        print('{0}'.format(sentence))
        run(sentence)
    
"""

    References:
    https://en.wikipedia.org/wiki/Variants_of_SARS-CoV-2
    https://www.gov.uk/government/publications/covid-19-variants-genomically-confirmed-case-numbers/variants-distribution-of-cases-data
    https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/979818/Variants_of_Concern_VOC_Technical_Briefing_9_England.pdf
    https://cov-lineages.org/index.html
    https://github.com/phe-genomics/variant_definitions

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

"""
