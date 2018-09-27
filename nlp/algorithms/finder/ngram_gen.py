#!/usr/bin/env python3
"""


OVERVIEW:


Use this module to generate ngrams from the input files 'anatomic_sites.txt'
and 'medra_terms.txt' files. The ngrams are written to the output file
'clarity_ngrams.txt'. The ngrams are consumed by the subject finder app.

The code in this module loads the files, removes junk, extracts relevant data,
and groups entries into ngrams sorted in descending order of length.


USAGE:


        python3  ./ngram_gen.py

"""

import re

# version info
VERSION_MAJOR = 0
VERSION_MINOR = 1

# input and output files
ANATOMIC_FILE = 'anatomic_sites.txt'
MEDRA_FILE    = 'medra_terms.txt'
OUTPUT_FILE   = 'clarity_ngrams.txt'

# regexes needed to parse input files
regex_nos          = re.compile(r'(?P<words>[-\w\s\d]+)(nos|nec|of)\Z')
regex_code         = re.compile(r'(\w\w\d\d?|cfu-[a-z])')
regex_punct        = re.compile(r'[,()]')
regex_and_or       = re.compile(r'\A(?P<and>[-\w\s]+)\s+and/or\s+(?P<or>[-\w\s]+)')
regex_entire       = re.compile(r'\Aentire\s+')
regex_definition   = re.compile(r'(?P<acronym>[\w\s]+)\s+-\s+(?P<definition>[-\w\s]+)')
regex_structure_of = re.compile(r'\Astructure\s+of\s+')

# these survive the filters below, so manually exclude them;
# many of these are common English words
EXCLUDE_LIST = ['axis', 'gerl', 'smas', 'mass', 'carina', 'lateral', 'male',
                'skin', 'womb', 'roof', 'palm', 'hand', 'neck', 'nose', 'lung',
                'iris', 'lens', 'head', 'foot', 'face', 'bone', 'body', 'chin',
                'hair', 'cell', 'knee', 'dirt', 'nail', 'duct', 'limb', 'back',
                'ache', 'bite', 'pain', 'rash', 'heel', 'lice', 'calf',
                'liver', 'elbow', 'atlas', 'bowel', 'trunk', 'torso', 'gland',
                'mouth', 'teeth', 'cheek', 'olive', 'beard', 'nerve', 'skull',
                'floor', 'brain', 'thigh', 'colon', 'heart', 'thumb', 'bones',
                'ankle', 'waist', 'pupil', 'wrist', 'digit', 'spine', 'clone',
                'chest', 'tooth', 'attic', 'media', 'globe', 'anger', 'blind',
                'burns', 'cough', 'cramp', 'crust', 'death', 'dizzy', 'dwarf',
                'faint', 'felon', 'fever', 'fuzzy', 'itchy', 'jumpy', 'other',
                'scald', 'shock', 'snore', 'sting', 'tense', 'theft', 'thief',
                'warts', 'water', 'worms', 'worry', 'wound', 'edema']

ngram_dict = {}


###############################################################################
def count_words(ngram_token):
    """
    Count the number of words in an ngram and return the count.
    """

    words = ngram_token.split()
    return len(words)


###############################################################################
def process_anatomic_sites_file(input_file):
    """
    Extract ngrams from the input file 'anatomic_sites.txt'.
    """
    
    fin = open(input_file, 'rt')
    for line in fin:
        
        # convert to lower case and remove trailing newline
        lc = line.lower().rstrip()
        
        # ignore if starts with a quote (additions below include most of these)
        if lc.startswith("'") or lc.startswith('"'):
            continue

        # ignore if contains 'percent of body surface'
        if -1 != lc.find('percent of body surface'):
            continue
        
        # ignore if starts with '['
        if lc.startswith('['):
            continue
    
        # remove the prefix "structure of "
        match = regex_structure_of.match(lc)
        if match:
            lc = lc[match.end():]

        # remove the prefix "entire "
        match = regex_entire.match(lc)
        if match:
            lc = lc[match.end():]

        # separate acronyms from definitions (format: acronym - definition)
        match = regex_definition.match(lc)
        if match:

            acronym = match.group('acronym')
            definition = match.group('definition')

            # ignore any codes
            match_code = regex_code.match(acronym)
            if match_code:
                continue
            
            # ignore any acronym portions that contain 'levels of spine'
            if -1 != acronym.find('levels of spine'):
                continue

            # keep the acronym text for a few special cases
            if definition == 'human' or definition == 'stoma':
                ngram_dict[acronym] = count_words(acronym)
                continue

            # discard the acronym and keep the definition terms
            ngram_dict[definition] = count_words(definition)
            continue

        # split entries containing and/or into two pieces
        match = regex_and_or.search(lc)
        if match:
            and_part = match.group('and')
            or_part  = match.group('or')

            # ignore codes
            if regex_code.match(and_part) and regex_code.match(or_part):
                continue
            elif regex_code.match(and_part):
                ngram_dict[or_part] = count_words(or_part)
            elif regex_code.match(or_part):
                ngram_dict[and_part] = count_words(and_part)
            else:
                ngram_dict[and_part] = count_words(and_part)
                ngram_dict[or_part] = count_words(or_part)

            continue

        # ignore codes
        if regex_code.match(lc):
            continue

        # these are simple words or junk
        if len(lc) <= 3:
            continue
        
        # ngram is good, keep it
        ngram_dict[lc] = count_words(lc)


    fin.close()

###############################################################################
def process_medra_file(input_file):
    """
    Extract ngrams from the file 'medra_terms.txt'.
    """
    
    fin = open(input_file, 'rt')
    for line in fin:
        
        # convert to lower case and remove trailing newline
        lc = line.lower().rstrip().lstrip()

        # if line ends in a period, remove it
        if lc.endswith('.'):
            lc = lc[:-1]
        
        # keep everything up to the first comma or open parenthesis
        pos = lc.find(',')
        if -1 != pos:
            lc = lc[:pos].rstrip()
            
        pos = lc.find('(')
        if -1 != pos:
            lc = lc[:pos].rstrip()

        # ignore if '/'; relevant entries included in add_extra_ngrams below
        if -1 != lc.find('/'):
            continue
            
        match = regex_nos.search(lc)
        if match:
            ngram = match.group('words').rstrip().lstrip()
            ngram_dict[ngram] = count_words(ngram)
            continue

        # these are nearly all junk
        if len(lc) <= 4:
            continue
        
        ngram_dict[lc] = count_words(lc)

    fin.close()
    
###############################################################################
def add_extra_ngrams(ngram_dict):
    """
    Explicit insertion of ngrams into the main data structure.
    """

    # taken from the input files, easier to just list them here
    ngram_dict['focus of enhancement'] = 3
    ngram_dict['interpolar left kidney'] = 3
    ngram_dict['interpolar right kidney'] = 3
    ngram_dict['left main bronchus'] = 3
    ngram_dict['right main bronchus'] = 3
    ngram_dict['left main stem bronchus'] = 4
    ngram_dict['right main stem bronchus'] = 4
    ngram_dict['upper pole of left kidney'] = 5
    ngram_dict['upper pole of right kidney'] = 5
    ngram_dict['middle pole of left kidney'] = 5
    ngram_dict['middle pole of right kidney'] = 5
    ngram_dict['mid pole of left kidney'] = 5
    ngram_dict['mid pole of right kidney'] = 5
    ngram_dict['lower pole of left kidney'] = 5
    ngram_dict['lower pole of right kidney'] = 5
    ngram_dict['myelin figure'] = 2
    ngram_dict['fascia of forearm'] = 3
    ngram_dict['fascia of head'] = 3
    ngram_dict['fascia of orbit'] = 3
    ngram_dict['fascia of neck'] = 3
    ngram_dict['fascia of hand'] = 3
    ngram_dict['fascia of finger'] = 3
    ngram_dict['intervertebral disc'] = 2
    ngram_dict['articular surface'] = 2
    ngram_dict['paratracheal lymph node'] = 3
    ngram_dict['gastric corpus'] = 2
    ngram_dict['gastric antrum'] = 2
    ngram_dict['gastric fundus'] = 2
    ngram_dict['lacrimal artery'] = 2
    ngram_dict['pellicle'] = 1
    ngram_dict['lymphoblast'] = 1
    ngram_dict['multivesicular body'] = 2
    ngram_dict['secretory granule'] = 2
    ngram_dict['left vocal cord'] = 3
    ngram_dict['right vocal cord'] = 3
    ngram_dict['retroperitoneal region'] = 2
    ngram_dict['basal lamina']  = 2
    ngram_dict['hypothenar muscle'] = 2
    ngram_dict['metacarpophalangeal joint'] = 2
    ngram_dict['carpometacarpal joint'] = 2
    ngram_dict['tarsometatarsal joint'] = 2
    ngram_dict['extensor tendon sheath'] = 3
    ngram_dict['flexor tendon sheath'] = 3
    ngram_dict['premature fetus'] = 2
    ngram_dict['premature foetus'] = 2
    ngram_dict['ulnar nerve'] = 2
    ngram_dict['adductor muscle of hip'] = 4
    ngram_dict['adductor muscle of thigh'] = 4
    ngram_dict['proximal interphalangeal joint'] = 3
    ngram_dict['distal interphalangeal joint']  = 3
    ngram_dict['vagus nerve']  = 2
    ngram_dict['common bile duct'] = 3
    ngram_dict['lymphatic vessel of nose'] = 4
    ngram_dict['lymphatic vessel of face'] = 4
    ngram_dict['lymphatic vessel of lip'] = 4
    ngram_dict['gastrointestinal tract'] = 2
    ngram_dict['metacarpal bone'] = 2
    ngram_dict['spinal cord'] = 2
    ngram_dict['diabetic retinopathy'] = 2
    ngram_dict['alveolar artery'] = 2
    ngram_dict['superior alveolar artery'] = 3
    ngram_dict['inferior alveolar artery'] = 3
    ngram_dict['brodmann area'] = 2
    ngram_dict['mucous membrane'] = 2
    ngram_dict['skin-associated mucous membrane'] = 3
    ngram_dict['synovial structure'] = 2
    ngram_dict['tendon synovial structure'] = 3
    ngram_dict['percent of body surface'] = 4
    ngram_dict['adult t-cell lymphoma'] = 3
    ngram_dict['adult t-cell leukaemia'] = 3
    ngram_dict['apolipoprotein b'] = 2
    ngram_dict['apolipoprotein a-1 ratio'] = 3
    ngram_dict['atypical teratoid'] = 2
    ngram_dict['rhabdoid tumor'] = 2
    ngram_dict['b-cell chronic lymphocytic leukaemia'] = 4
    ngram_dict['b-cell chronic lymphocytic leukemia'] = 4
    ngram_dict['prolymphocytic leukaemia'] = 2
    ngram_dict['prolymphocytic leukemia'] = 2
    ngram_dict['small lymphocytic lymphoma'] = 3
    ngram_dict['blood protein'] = 2
    ngram_dict['albumin'] = 1
    ngram_dict['blood urea nitrogen/creatinine ratio'] = 4
    ngram_dict['calcium/creatinine ratio'] = 2
    ngram_dict['cd4/cd8 ratio'] = 2
    ngram_dict['deoxypyridinoline/creatinine ratio'] = 2
    ngram_dict['extranodal nk/t-cell lymphoma'] = 3
    ngram_dict['hdl/cholesterol ratio'] = 2
    ngram_dict['kappa/lambda light chain ratio'] = 4
    ngram_dict['ldl/hdl ratio'] = 2
    ngram_dict['lip and oral cavity cancer'] = 5
    ngram_dict['lip or oral cavity cancer'] = 5
    ngram_dict['lymphoplasmacytoid lymphoma'] = 2
    ngram_dict['immunocytoma'] = 1
    ngram_dict['malignant melanoma'] = 2
    ngram_dict['mycosis fungoides/sezary syndrome'] = 3
    ngram_dict['optic nerve cup/disc ratio'] = 4
    ngram_dict['pao2/fio2 ratio'] = 2
    ngram_dict['precursor b-lymphoblastic lymphoma'] = 3
    ngram_dict['precursor b-lymphoblastic leukaemia'] = 3
    ngram_dict['precursor b-lymphoblastic leukemia'] = 3
    ngram_dict['tingling feet/hands'] = 2
    ngram_dict['tingling feet'] = 2
    ngram_dict['tingling hands'] = 2
    ngram_dict['tonic/clonic convulsions'] = 2
    ngram_dict['tonic convulsions'] = 2
    ngram_dict['clonic convulsions'] = 2
    ngram_dict['total cholesterol/hdl ratio'] = 3
    ngram_dict['urinary 6 beta hydroxycortisol/cortisol ratio'] = 5
    ngram_dict['urine albumin/creatinine ratio'] = 3
    ngram_dict['urine calcium/creatinine ratio'] = 3
    ngram_dict['urine cortisol/creatinine ratio'] = 3
    ngram_dict['urine protein/creatinine ratio'] = 3
    ngram_dict['ventilation/perfusion scan'] = 2
    ngram_dict['ventilation scan'] = 2
    ngram_dict['perfusion scan'] = 2

    # extra ngrams from testing
    ngram_dict['calculi'] = 1
    ngram_dict['node'] = 1
    ngram_dict['hilar node'] = 2
    ngram_dict['hyperechoic focus'] = 2
    ngram_dict['bronchus intermedius'] = 2
    
###############################################################################    
if __name__ == '__main__':

    fout = open(OUTPUT_FILE, 'wt')
    
    process_anatomic_sites_file(ANATOMIC_FILE)
    process_medra_file(MEDRA_FILE)

    # insert additional ngrams not in the file
    add_extra_ngrams(ngram_dict)
    
    # get the different ngram lengths
    ngram_lengths = sorted(set(ngram_dict.values()))
    
    for n in reversed(ngram_lengths):
        
        # get all ngrams of length n
        ngrams_length_n = []
        for key, val in ngram_dict.items():
            if val != n:
                continue
            ngrams_length_n.append(key)
            
        # sort the ngrams of length n by length, longest to shortest
        ngrams_sorted_by_len = sorted(ngrams_length_n, key=len, reverse=True)
            
        # write to file
        fout.write('# length: {0}\n'.format(n))
        for ngram in ngrams_sorted_by_len:
            if not ngram in EXCLUDE_LIST:
                if len(ngram) >= 4:
                    fout.write(ngram + '\n')


    fout.close()
