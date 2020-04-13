#!/usr/bin/env python3
"""


OVERVIEW:


The code in this module loads sentences containing TNM staging codes and
returns a JSON result describing the prefixes, suffixes, and values for
each portion of the code.


OUTPUT:


The set of JSON fields present in the output for each code includes:


        text             text of the complete code
        start            offset of first char in the matching text
        end              offset of final char in the matching text + 1

        t_prefix         see comments for 'str_prefix_symbols' below
        t_code           X, is, 0, 1, 2, 3, 4
        t_certainty      see comments for 'str_certainty' below
        t_suffixes       a, b, c, d
        t_multiplicity   tumor multiplicity value

        n_prefix         see comments for 'str_prefix_symbols' below
        n_code           X, 0, 1, 2, 3
        n_certainty      see comments for 'str_certainty' below
        n_suffixes       a, b, c, d, mi, sn, i+, i-, mol+, mol-
        n_regional_nodes_examined   integer value
        n_regional_nodes_involved   integer value

        m_prefix         see comments for 'str_prefix_symbols' below
        m_code           X, 0, 1
        m_certainty      see comments for 'str_certainty' below
        m_suffixes       a, b, c, d, i+, mol+, cy+, PUL, OSS, HEP, BRA,
                         LYM, OTH, MAR, PLE, PER, ADR, SKI

        l_code           X, 0, 1
        g_code           X, 1, 2, 3, 4
        v_code           X, 0, 1, 2
        pn_code          X, 0, 1
        serum_code       X, 0, 1, 2, 3

        r_codes          X, 0, 1, 2
        r_suffixes       is, cy+
        r_locations      string

        stage_prefix     y, yp
        stage_number     0, 1, 2, 3, 4
        stage_letter     a, b, c, d


See the comments below for the meanings of each of these fields.

All JSON fields will be present in the output for each code. If a field should
be ignored it will have the value EMPTY_FIELD.


USAGE:


To use this code as an imported module, add the following lines to the
import list in the importing module:

        import json
        import tnm_stager as tnm

To find TNM codes in a sentence and capture the JSON result:

        json_string = tnm.run(sentence)

To unpack the JSON into a list of TnmCode namedtuples:

        json_data = json.loads(json_string)
        tnm_codes = [tnm.TnmCode(**m) for m in json_data]

To access the fields in each code:

        for c in tnm_codes:
            text  = c.text
            start = c.start
            end   = c.end

            if tnm.EMPTY_FIELD != c.t_prefix:
                t_prefix = c.t_prefix

            etc.

It is also possible to export the list 'TNM_FIELDS' (see below) to access the
components of a code:

        for c in tnm_codes:

        # for each field in the field list
        for f in tnm.TNM_FIELDS:

            # get the value of this field for this code c
            attr = getattr(c, f)

            # use the field if valid
            if tnm.EMPTY_FIELD != attr:
                log(attr)



Information on the TNM system was compiled from these sources:

1. Natural Language Processing in Determining Cancer Stage,
   Final Report, Regenstrief Institute, citation TBD

2. TNM Classification of Malignant Tumors, Eighth Edition, 
   ed. Brierly et. al., Wiley-Blackwell, 2017

3. TNM Supplement: A Commentary on Uniform Use, Fourth Edition, 
   ed. Wittekind et. al., Wiley-Blackwell, 2012

4. https://emedicine.medscape.com/article/2007800-overview

"""

import re
import os
import sys
import json
import optparse
from collections import namedtuple

VERSION_MAJOR = 0
VERSION_MINOR = 4

# The 'TnmCode' namedtuple is the JSON-serializable object emitted by this
# module. The fields in the JSON output are in the TNM_FIELDS list. Any
# field that has the value EMPTY_FIELD should be ignored.

EMPTY_FIELD = None
TNM_FIELDS = ['text', 'start', 'end',
              't_prefix', 't_code', 't_certainty', 't_suffixes', 't_mult',
              'n_prefix', 'n_code', 'n_certainty', 'n_suffixes',
              'n_regional_nodes_examined', 'n_regional_nodes_involved',
              'm_prefix', 'm_code', 'm_certainty', 'm_suffixes',
              'l_code', 'g_code', 'v_code', 'pn_code', 'serum_code',
              'r_codes', 'r_suffixes', 'r_locations', 
              'stage_prefix', 'stage_number', 'stage_letter']
TnmCode = namedtuple('TnmCode', TNM_FIELDS)

# Common prefixes for T, N, M codes:
#
#     c     clinical classification
#     p     pathological classification
#    yc     clinical classification peformed during multimodal therapy
#    yp     pathological classification performed during multimodal therapy
#     r     recurrent tumor
#    rp     recurrence after a disease free interval, designated at autopsy
#           (see TNM Supplement)
#     a     classification determined at autopsy
str_prefix_symbols  = r'(c|p|yc|yp|r|rp|a)?'

# Certainty factor (present in 4th through 7th editions of TNM, not in the 8th)
#
#     C1    evidence from standard diagnostic means (inspection, palpitation)
#     C2    evidence from special diagnostic means (CT, MRI, ultrasound)
#     C3    evidence from surgical exploration, including biopsy and cytology
#     C4    evidence from definitive surgery and pathological examination
#     C5    evidence from autopsy
str_certainty = r'(C[1-5])?'

# T - extent of primary tumor
#
# Values:  TX              primary tumor cannot be assessed
#          T0              no evidence of primary tumor
#          Tis             carcinoma in situ
#          T1, T2, T3, T4  increasing size and/or local extent of primary tumor
#
# For multiple tumors, indicate multiplicity via suffix, e.g. T1(m) or T2(3)
# Indicate anatomical subsites with suffixes a, b, c, d, e.g. T1a
# (TNM Supplement, ch. 1, p. 20): Recurrence in the area of a primary tumor
# is designated with the '+' suffix. 

T_SUFFIX_STRINGS = ['a', 'b', 'c', 'd'] # exclude multiplicity
str_t_suffixes = r'(a|b|c|d|\+|\(m\)|\(\d+\))*'
str_t = r'(?P<t_prefix>' + str_prefix_symbols + r')' +\
        r'T(?P<t_code>([0-4]|is|X))'                 +\
        r'(?P<t_certainty>' + str_certainty + r')'   +\
        r'(?P<t_suffixes>' + str_t_suffixes + r')'
regex_t = re.compile(str_t, re.IGNORECASE)

# use this to find multiplicity value
regex_t_mult = re.compile(r'(m|\d+)', re.IGNORECASE)

# N - regional lymph nodes
#
# Values:  NX             cannot be assessed
#          N0             no regional lymph node metastasis
#          N1, N2, N3     increasing involvement of regional lymph nodes
#
# Indicate anatomical subsites with suffixes a, b, c, d, e.g. N2a
# (TNM Supplement, ch. 1, p. 9): With only micrometastasis (smaller than
# 0.2cm), use suffix (mi), e.g. pN1(mi)
# Suffix (sn) indicates sentinel lymph node involvement:
#
#          pNX(sn)        sentinel lymph node involvement could not be assessed
#          pN0(sn)        no sentinel lymph node metastasis
#          pN1(sn)        sentinel lymph node metastasis
#
# Indicate examination for isolated tumor cells (ITC) with:
#
#          pN0(i-)        no histologic regional node metastasis,
#                         negative morphological findings for ITC
#          pN0(i+)        no histologic regional node metastasis,
#                         positive morphological findings for ITC
#          pN0(mol-)      no histologic regional node metastasis,
#                         negative non-morphological findings for ITC
#          pN0(mol+)      no histologic regional node metastasis,
#                         positive non-morphological findings for ITC
#
# Indicate ITC examination in sentinel lymph nodes with:
#
#          pN0(i-)(sn)    no histologic sentinel node metastasis,
#                         negative morphological findings for ITC
#          pN0(i+)(sn)    no histologic sentinel node metastasis,
#                         positive morphological findings for ITC
#          pN0(mol-)(sn)  no histologic sentinel node metastasis,
#                         negative non-morphological findings for ITC
#          pN0(mol+)(sn)  no histologic sentinal node metastasis,
#                         positive non-morphological findings for ITC
#
# The TNM supplement (ch. 1, p. 8) recommends adding the number of 'involved'
# and examined regional lymph nodes to the pN classification, e.g. pN1b(3/15).
# This notation means that 15 regional lymph nodes were examined and 3 were
# found to be involved.

# exclude multiplicity
N_SUFFIX_STRINGS = ['a', 'b', 'c', 'd', 'mi', 'sn', 'i+', 'i-',
                    'mol+', 'mol-']

str_n_suffixes = r'(a|b|c|d|mi|sn|i[-,+]|mol[-,+]|\(mi\)|\(sn\)|\(i[-,+]\)|' +\
                 r'\(mol[-,+]\)|\(\d+\s*/\s*\d+\))*'
str_n = r'(?P<n_prefix>' + str_prefix_symbols + r')' +\
        r'N(?P<n_code>([0-3]|X))'                    +\
        r'(?P<n_certainty>' + str_certainty + r')'   +\
        r'(?P<n_suffixes>' + str_n_suffixes + r')'
regex_n = re.compile(str_n, re.IGNORECASE)

# check for regional lymph node metastases
regex_regional_metastases = re.compile(r'\((?P<regionals_involved>\d+)' +\
                                       r'\s*/\s*(?P<regionals_examined>\d+)\)',
                                       re.IGNORECASE)

# M - distant metastasis
#
# Values:  MX              considered inappropriate, if metastasis can be
#                          evaluated based on physical exam alone; see TNM
#                          guide p. 24, TNM Supplement pp. 10-11.
#          M0              no distant metastasis
#          M1              distant metastasis
#         pMX              invalid category (TNM Supplement, ch. 1, p. 10)
#         pM0              only to be used after autopsy (TNM Supplement,
#                          ch. 1, p. 10)
#         pM1              distant metastasis microscopically confirmed
#
# M1 and pM1 subcategories may indicated by these optional suffixes:
#
#          PUL             pulmonary
#          OSS             osseous
#          HEP             hepatic
#          BRA             brain
#          LYM             lymph nodes
#          OTH             others
#          MAR             bone marrow
#          PLE             pleura
#          PER             peritoneum
#          ADR             adrenals
#          SKI             skin
#
# Indicate anatomical subsites with suffixes a, b, c, d.
# The suffix (cy+) is valid for M1 under certain conditions (TNM Supplement,
# ch. 1, p. 11)
# For isolated tumor cells found in bone marrow (TNM Supplement, ch. 1, p. 11):
#
#          M0(i+)          positive morphological findings for ITC
#          M0(mol+)        positive non-morphological findings for ITC

M_SUFFIX_STRINGS = ['a', 'b', 'c', 'd', 'i+', 'mol+', 'cy+',
                    'pul', 'oss', 'hep', 'bra', 'lym', 'oth',
                    'mar', 'ple', 'per', 'adr', 'ski']
str_m_suffixes = r'(a|b|c|d|i\+|mol\+|cy\+|\(i\+\)|\(mol\+\)|\(cy\+\)|' +\
                 r'PUL|OSS|HEP|BRA|LYM|OTH|MAR|PLE|PER|ADR|SKI)*'
str_m = r'(?P<m_prefix>' + str_prefix_symbols + r')'        +\
        r'M(?P<m_code>(0|1|X))'                             +\
        r'(?P<m_certainty>' + str_certainty + r')'          +\
        r'(?P<m_suffixes>' + r'\s*' + str_m_suffixes + r')'
regex_m = re.compile(str_m, re.IGNORECASE)

# R - residual metastases
#
# Values:
#
#          RX              presence of residual tumor cannot be assessed
#          R0 (location)   residual tumor cannot be detected by any
#                          diagnostic means
#          R1 (location)   microscopic residual tumor at the indicated location
#          R2 (location)   macroscopic residual tumor at the indicated location
#
# The TNM Supplement (ch. 1. p. 14) recommends annotating R with the location
# in parentheses, e.g.:
#
#          R1 (liver)
#
# Can have multiple R designations, for instance:
#
# "pT3pN1M1 colon cancer with resection for cure of both the primary tumor and
#  a liver metastasis; R0 (colon); R0 (liver)"
#
# The presence of non-invasive carcinoma at the resection margin should be
# indicated by the suffix (is). See TNM Supplement, ch. 1, p. 15.
#
# The suffix (cy+) for R1 is valid under certain conditions (see TNM
# supplement, ch. 1, p. 16).

R_SUFFIX_STRINGS = ['is', 'cy+']
str_r_suffixes = r'(is|cy\+|\(is\)|\(cy\+\))?'
str_r_loc      = r'(\((?P<r_loc>[a-z]+)\)[,;\s]*)*'
str_r = r'R(?P<r_code>(0|1|2|X))'                  +\
        r'(?P<r_suffixes>' + str_r_suffixes + r')' +\
        r'\s*' + str_r_loc
regex_r = re.compile(str_r, re.IGNORECASE)

# G - histopathological grading
#
# Values:
#
#          GX          grade of differentiation cannot be assessed
#          G1          well differentiated
#          G2          moderately differentiated
#          G3          poorly differentiated
#          G4          undifferentiated
#
# G1 and G2 may be grouped together as G1-2 (TNM Supplement, ch. 1, p. 23)
# G3 and G4 may be grouped together as G3-4 (TNM Supplement, ch. 1, p. 23)
str_g = r'G(?P<g_code>(1-2|3-4|X|1|2|3|4))'
regex_g = re.compile(str_g, re.IGNORECASE)

# L - lymphatic invasion
#
# Values:
#
#          LX          lymphatic invasion cannot be assessed
#          L0          no lymphatic invasion
#          L1          lymphatic invasion
str_l = r'L(?P<l_code>(X|0|1))'
regex_l = re.compile(str_l, re.IGNORECASE)

# V - venous invasion
#
# Values:
#
#          VX          venous invasion cannot be assessed
#          V0          no venous invasion
#          V1          microscopic venous invasion
#          V2          macroscopic venous invasion
str_v = r'V(?P<v_code>(X|0|1|2))'
regex_v = re.compile(str_v, re.IGNORECASE)

# Perineural invasion
#
#        PnX           perineural invasion cannot be assessed
#        Pn0           no perineural invasion
#        Pn1           perineural invasion
str_pn = r'Pn(?P<pn_code>(X|0|1))'
regex_pn = re.compile(str_pn, re.IGNORECASE)

# Serum tumor markers
#
#        SX            marker studies not available or not performed
#        S0            marker study levels within normal limits
#        S1            markers are slightly raised
#        S2            markers are moderately raised
#        S3            markers are very high
str_serum = r'S(?P<serum_code>(X|0|1|2|3))'
regex_serum = re.compile(str_serum, re.IGNORECASE)

# Stage
#
# The stage designation can have 'y' or 'yp' prefixes
# (see TNM supplement, ch. 1, p. 18).
str_stage = r'(\(?stage\s*(?P<stage_prefix>(yp?)?)' +\
            r'(?P<stage_num>([0-4]|iv|iii|ii|i))'   +\
            r'\s*(?P<stage_letter>(a|b|c|d)?)\)?)?'
regex_stage = re.compile(str_stage, re.IGNORECASE)



# dict to convert roman numerals to decimal strings
stage_dict = {'i':'1', 'ii':'2', 'iii':'3', 'iv':'4'}

# matcher for words, including hyphenated words, abbreviations, and punctuation
str_words = r'((\b[-a-zA-Z]+[.,;\s]*)+)?'

# punctuation that can appear in a code
str_punct = r'[,;]'

# The TNM code consists of T, N, and M codes with optional spacing inbetween,
# optional punctuation after, optional words, then zero or more optional
# R, G, L, V, Pn, or serum (S) codes with optional spacing inbetween.
str_tnm_opt = r'((' + str_r + '|' + str_g + r'|' + str_l + r'|' + str_v      +\
              r'|' + str_pn + r'|' + str_serum + r')[\s,;]?\s*)*' + str_stage
str_tnm_code = str_t + r'\s*' + str_n + r'\s*' + str_m                       +\
               r'\s*' + r'(' + str_punct + r'\s*' + r')?'                    +\
               r'(?P<tnm_opt>' + str_tnm_opt + r')'
regex_tnm_code = re.compile(str_tnm_code, re.IGNORECASE)

match_groups = ['t_prefix', 't_code', 't_certainty', 't_suffixes',
                'n_prefix', 'n_code', 'n_certainty', 'n_suffixes',
                'm_prefix', 'm_code', 'm_certainty', 'm_suffixes',
                'tnm_opt']

# valid punctuation chars for a TNM code
PUNCT_CHARS = [',', ';']

STR_NONE = 'None'

###############################################################################
def get_certainty(text):
    """
    Return the certainty digit from a matching T, N, or M certainty factor.
    """

    certainty = None
    pos = text.find('C')
    if -1 != pos:
        certainty = text[pos+1]

    return certainty
                    
###############################################################################
def get_suffixes(suffix_list, text):
    """
    Check text for all suffixes in the suffix list. Return a list of all 
    suffixes found.
    """

    text_lc = text.lower()
    
    results = []
    for suffix in suffix_list:
        pos = text_lc.find(suffix)
        if -1 != pos:
            results.append(suffix)

    return results

###############################################################################
def get_t_suffixes(group_name, text, code_dict):
    """
    Extract all T code suffixes and multiplicity values, if any.
    """

    suffixes = get_suffixes(T_SUFFIX_STRINGS, text)
    if len(suffixes) > 0:
        code_dict[group_name] = suffixes

    # check also for matching multiplicity
    iterator = regex_t_mult.finditer(text)
    for match in iterator:
        multiplicity = match.group()
        code_dict['t_mult'] = match.group()

###############################################################################
def get_n_suffixes(group_name, text, code_dict):
    """
    Extract all N code suffixes and multiplicity values, if any.
    """

    suffixes = get_suffixes(N_SUFFIX_STRINGS, text)
    if len(suffixes) > 0:
        code_dict[group_name] = suffixes

    # check for regional metastases
    match = regex_regional_metastases.search(text)
    if match:
        code_dict['n_regional_nodes_involved'] = match.group('regionals_involved')
        code_dict['n_regional_nodes_examined'] = match.group('regionals_examined')

###############################################################################
def get_m_suffixes(group_name, text, code_dict):
    """
    Extract all M code suffixes, if any.
    """

    suffixes = get_suffixes(M_SUFFIX_STRINGS, text)
    if len(suffixes) > 0:
        code_dict[group_name] = suffixes

###############################################################################
def extract_r(text, code_dict):
    """
    Extract all R code suffixes, if any.
    """

    r_codes     = []
    r_suffixes  = []
    r_locations = []
    
    iterator = regex_r.finditer(text)
    for match in iterator:

        # get R code
        r_codes.extend(match.group('r_code'))
        
        # get R suffixes
        suffixes = get_suffixes(R_SUFFIX_STRINGS, match.group())
        if 0 == len(suffixes):
            suffixes = [STR_NONE]
        r_suffixes.extend(suffixes)

        # get R locations
        loc = match.group('r_loc')
        if loc:
            r_locations.append(loc)
        else:
            r_locations.append(STR_NONE)

    if len(r_codes) > 0:
        code_dict['r_codes'] = r_codes
        code_dict['r_suffixes'] = r_suffixes
        code_dict['r_locations'] = r_locations

###############################################################################
def get_code(code_name, code_dict, regex, text):

    match = regex.search(text)
    if match:
        code_dict[code_name] = match.group(code_name)

###############################################################################
def get_stage(code_dict, text):
    
    match_stage = regex_stage.search(text)
    if match_stage:
        stage_prefix = match_stage.group('stage_prefix')
        stage_num    = match_stage.group('stage_num')
        stage_letter = match_stage.group('stage_letter')
        
        if stage_prefix:
            code_dict['stage_prefix'] = stage_prefix
            
        if stage_num:
            key = stage_num.lower()
            if key in stage_dict:
                code_dict['stage_number'] = stage_dict[key]
            else:
                code_dict['stage_number'] = stage_num
            
        if stage_letter:
            code_dict['stage_letter'] = stage_letter.lower()

###############################################################################
def run(sentence):
    """
    Search the sentence for all occurrences of a TNM code. Decode any that are
    found and serialize results to JSON.
    """

    results = []

    iterator = regex_tnm_code.finditer(sentence)
    for match in iterator:

        # each TNM code gets its own dict of match items
        code_dict = {}

        # initialize all fields to empty to begin...
        for field in TNM_FIELDS:
            code_dict[field] = EMPTY_FIELD

        # strip any whitespace or trailing punctuation
        match_text = match.group().strip()
        if len(match_text) > 0 and match_text[-1] in PUNCT_CHARS:
            match_text = match_text[:-1]

        code_dict['text']  = match_text
        code_dict['start'] = match.start()
        code_dict['end']   = match.start() + len(match_text)

        for group_name in match_groups:
            if match.group(group_name):
                group_text = match.group(group_name)
                if 'tnm_opt' == group_name:
                    get_code('l_code',     code_dict, regex_l,     group_text)
                    get_code('g_code',     code_dict, regex_g,     group_text)
                    get_code('v_code',     code_dict, regex_v,     group_text)
                    get_code('pn_code',    code_dict, regex_pn,    group_text)
                    get_code('serum_code', code_dict, regex_serum, group_text)
                    get_stage(code_dict, group_text)

                    # can have multiple R groups
                    extract_r(group_text, code_dict)
                    
                elif 't_suffixes' == group_name:
                    get_t_suffixes(group_name, group_text, code_dict)
                elif 'n_suffixes' == group_name:
                    get_n_suffixes(group_name, group_text, code_dict)
                elif 'm_suffixes' == group_name:
                    get_m_suffixes(group_name, group_text, code_dict)
                elif -1 != group_name.find('certainty'):
                    code_dict[group_name] = get_certainty(group_text)
                else:
                    code_dict[group_name] = group_text

        results.append(code_dict)
    
    return json.dumps(results, indent=4)

###############################################################################
def get_version():
    return 'tnm_stager {0}.{1}'.format(VERSION_MAJOR, VERSION_MINOR)
        
###############################################################################
def show_help():
    print(get_version())
    print("""
    USAGE: python3 ./tnm_stager.py -s <sentence>  [-hvz]

    OPTIONS:

        -s, --sentence <quoted string>  Sentence to be processed.

    FLAGS:

        -h, --help           log this information and exit.
        -v, --version        log version information and exit.
        -z, --test           Disable -s option and use internal test sentences.

    """)
                    
###############################################################################
if __name__ == '__main__':

    # some examples taken from the TNM Supplement, 4th ed.
    TEST_STRINGS = [
        'The tumor code is pT0pN1M0.',
        'Another tumor code is pT1pN1bM0, taken from a relevant document.',
        'The code pT1pNXM0, R1 indicates residual metastasis.',
        'This code ypT0pN0M0, R0 indicated no residual metastasis.',
        'Here is another code: pT2cN1cM0.',
        'This code indicates staging: pT4bpN1bM0 (stage IIIC).',
        'The tumor code pT4bpN1bM0 (stage IIIC) also has a stage indication.',
        'pT2bpN1M0 (stage IIIC)',
        'pT3pN2M1, stage IV',
        'T0NXM1, stage IV',
        'T4a N1a M1pul L1 SX',
        'pT3pN1M1; S2 R0is (colon); R1cy+ (liver)',
        'pT1bpN0(0/34) pM1 LYM',
        'ypT2C4(3) N1(2/16) pM1 G1-2VX L1 Pn0; R0 (liver), R1(cy+) (lung)',

        # multiple codes per sentence
        'The first code is pT1bpN0(0/34) pM1 LYM and the second code is '   +\
        'pT2bpN1M0 (stage IIIC).',
        'Tumor A has code ypT2C4(3) N1(2/16) pM1 G1-2VX L1 Pn0; R0 (liver)' +\
        ', R1(cy+) (lung) and tumor B has code pT3pN1M1; S2 R0is (colon); ' +\
        'R1cy+ (liver).',
    ]
        
    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-s', '--sentence', action='store',
                         dest='sentence')
    optparser.add_option('-v', '--version',  action='store_true',
                         dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true',
                         dest='show_help', default=False)
    optparser.add_option('-z', '--test',     action='store_true',
                         dest='use_test_sentences', default=False)

    opts, other = optparser.parse_args(sys.argv)

    sentence = opts.sentence
    use_test_sentences = opts.use_test_sentences
    
    if 1 == len(sys.argv) and not use_test_sentences:
        show_help()
        sys.exit(0)

    if opts.show_help:
        show_help()
        sys.exit(0)

    if opts.get_version:
        print(get_version())
        sys.exit(0)
    
    if not sentence and not use_test_sentences:
        print('Error: sentence not specified...')
        sys.exit(-1)

    sentences = []
    if use_test_sentences:
        sentences = TEST_STRINGS
    else:
        sentences.append(sentence)

    # end of setup

    for sentence in sentences:
        
        if use_test_sentences:
            print('Sentence: ' + sentence)

        # decode results and log only valid fields
        json_string = run(sentence)
        json_data = json.loads(json_string)
        tnm_codes = [TnmCode(**c) for c in json_data]

        # get the length of the longest field name
        max_len = max([len(f) for f in TNM_FIELDS])

        for c in tnm_codes:
            for f in TNM_FIELDS:
                # get the value of this field for code c
                val = getattr(c, f)

                # if not empty, log it
                if EMPTY_FIELD != val:
                    INDENT = ' '*(max_len - len(f))
                    print('{0}{1}: {2}'.format(INDENT, f, val))
            print()
