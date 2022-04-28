#!/usr/bin/evn python3
"""
Module for finding someone's education level.
"""

import os
import re
import sys
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
    

EDUC_ELEM         = 'less than high school'
EDUC_SOME_HS      = 'some high school'
EDUC_HS_GED       = 'high school diploma or GED'
EDUC_SOME_COLLEGE = 'some college'
EDUC_COLLEGE_DEG  = 'college degree'
    
EDUC_TUPLE_FIELDS = [
    'sentence',
    'education_level'
]

EducTuple = namedtuple('EducTuple', EDUC_TUPLE_FIELDS)
EducTuple.__new__.__defaults__ = (None,) * len(EducTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 2

# set to True to enable debug output
_TRACE = False

#_str_degrees = r'\b(?P<degree>(ged|(ph|sc)\.?d\.?|[bm]\.?[asd]\.?|s\.?[bm]\.?)|masters?|batchelors?|doctor(al|s))\b'
# regex capture group names
_DEG_DOCTORAL   = 'doctoral'
_DEG_MASTERS    = 'masters'
_DEG_BATCHELORS = 'batchelors'
_DEG_GED        = 'ged'
_str_doctoral = r'\b(doctor(al|ate|s)|(ph|sc)\.?d\.?|m\.?d\.?)\b'
_str_masters = r'\b(masters?|m\.?[as]\.?|s\.?[bm]\.?)\b'
_str_batchelors = r'\b(batchelors?|b\.?[as]\.?|s\.?[ab]\.?)\b'
_str_ged = r'\bged\b'
_str_degrees = r'(' + r'(?P<doctoral>' + _str_doctoral + r')|' +\
    r'(?P<masters>' + _str_masters + r')|' +\
    r'(?P<batchelors>' + _str_batchelors + r')|' +\
    r'(?P<ged>(' + _str_ged + r')))'
_regex_degrees = re.compile(_str_degrees, re.IGNORECASE)

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\b\s?(' + _str_word + r'){0,5}?'
_str_one_or_more_words = r'(' + _str_word + r'){1,5}?'

# words used to state that somebody does NOT have a degree
# (apostrophes are removed in _cleanup)
_str_neg_words = r'\b(without|other than|lacks|understands neither|unable to|cannot|cant|not|non?)\b'
_str_neg_degree = _str_neg_words + _str_words + _str_degrees
_regex_neg_degree = re.compile(_str_neg_degree, re.IGNORECASE)


_str_elem = r'\b(kindergarten|elementary|preparatory|parochial|day) school\b'
_str_hs = r'\b((high|h\.?)\s?(school|s\.?)|school)\b'
_str_jhs = r'\b(junior|j\.?r\.?) ' + _str_hs
_str_college = r'\b(college|university|grad(uate)? school)\b'
_str_named_year = r'\b(fresh(man)?|soph(o?more)?|(junior|j\.?r)|(senior|s\.?r))\.?\b'

#_str_school = r'(?P<school>(' + _str_college + r'|' + _str_hs + r'|' + _str_jhs + r'|' + _str_elem + r'))'
# regex capture group names
_SCHOOL_COLLEGE = 'college'
_SCHOOL_HS      = 'hs'
_SCHOOL_ELEM    = 'elem'
_str_school = r'(' + r'(?P<college>' + _str_college + r')|' +\
    r'(?P<hs>' + _str_hs + r')|' +\
    r'(?P<elem>' + r'(' + _str_jhs + r')|(' + _str_elem + r')))'

# some school
_str_some1 = r'\b(attend(ing|ed|s)|began|dropped out|(never|did not|didnt) finish(ed)?|some|in)' +\
    _str_words + _str_school
_regex_some1 = re.compile(_str_some1, re.IGNORECASE)

# ...is a junior in hs...
_str_some2 = _str_named_year + _str_words + _str_school
_regex_some2 = re.compile(_str_some2, re.IGNORECASE)

# ...is a high school junior
_str_some3 = _str_school + r' ' + _str_named_year
_regex_some3 = re.compile(_str_some3, re.IGNORECASE)

# ... is a school student...
_str_some4 = _str_school + _str_words + r'\bstudent\b'
_regex_some4 = re.compile(_str_some4, re.IGNORECASE)

# ...high school dropout...
_str_drop1 = _str_school + _str_words + r'\bdropout\b'
_regex_drop1 = re.compile(_str_drop1, re.IGNORECASE)

# ...dropped out of college...
_str_dropped_out = r'\b(dropped out of|did not (complete|finish)|quit|left)\b'
_str_drop2 = _str_dropped_out + _str_words + _str_school + r'(' + _str_words + _str_named_year + r'( year)?' + r')?'
_regex_drop2 = re.compile(_str_drop2, re.IGNORECASE)

# ...graduated from high school...
_str_grad1 = r'\b(?<!never )(graduated( from)?|completed|finished)(?! some)\b' + _str_words + _str_school
_regex_grad1 = re.compile(_str_grad1, re.IGNORECASE)

# ...is a college graduate...
_str_grad2 = r'\bis a\b' + _str_words + _str_school + _str_words + r'\bgraduate\b'
_regex_grad2 = re.compile(_str_grad2, re.IGNORECASE)

# ...received a college degree...
_str_received = r'\b(received|recieved|earned|completed|finished|obtained|did get|getting|got|has|with)(?! some)\b'
_str_grad3 = _str_received + _str_words +\
    _str_school + _str_words + r'\b(degree|diploma|education|certificat(ion|e))s?\b'
_regex_grad3 = re.compile(_str_grad3, re.IGNORECASE)

# ...received a <specific degree>...
_str_grad4 = _str_received + _str_words + _str_degrees
_regex_grad4 = re.compile(_str_grad4, re.IGNORECASE)

# Education: GED
_str_terse = r'\b(education|social history) ' + _str_degrees
_regex_terse = re.compile(_str_terse, re.IGNORECASE)


# ...went to <college> for <degree>
_str_specific_degree = r'\b(went to|attended|enrolled (at|in)|graduated from)\b' + _str_words + _str_college + _str_words + _str_degrees
_regex_specific_degree = re.compile(_str_specific_degree, re.IGNORECASE)

_REGEXES_SOME_SCHOOL = [
    _regex_some1,
    _regex_some2,
    _regex_some3,
    _regex_some4,

    _regex_drop1,
    _regex_drop2,
]

_REGEXES_GRADUATED = [
    _regex_grad1,
    _regex_grad2,
    _regex_grad3,
    _regex_grad4,
    _regex_terse,
    _regex_specific_degree,
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
    sentence = re.sub(r'[-&(){}\[\]:~/;]', _CHAR_SPACE, sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', _CHAR_SPACE, sentence)

    return sentence


###############################################################################
def _regex_match(sentence, regex_list):
    """
    """

    sentence_save = sentence
    
    candidates = []
    for i, regex in enumerate(regex_list):
        iterator = regex.finditer(sentence)
        for match in iterator:
            # strip any trailing whitespace (invalidates match.end())
            match_text = match.group().rstrip()
            start = match.start()
            end = start + len(match_text)

            # isolate the school, if any
            school_text = None
            if _SCHOOL_COLLEGE in match.groupdict() and match.group(_SCHOOL_COLLEGE) is not None:
                school_text = _SCHOOL_COLLEGE
            elif _SCHOOL_HS in match.groupdict() and match.group(_SCHOOL_HS) is not None:
                school_text = _SCHOOL_HS
            elif _SCHOOL_ELEM in match.groupdict() and match.group(_SCHOOL_ELEM) is not None:
                school_text = _SCHOOL_ELEM

            degree_text = None
            #if 'degree' in match.groupdict():
            #    degree_text = match.group('degree').strip()
            if _DEG_DOCTORAL in match.groupdict() and match.group(_DEG_DOCTORAL) is not None:
                degree_text = _DEG_DOCTORAL
            elif _DEG_MASTERS in match.groupdict() and match.group(_DEG_MASTERS) is not None:
                degree_text = _DEG_MASTERS
            elif _DEG_BATCHELORS in match.groupdict() and match.group(_DEG_BATCHELORS) is not None:
                degree_text = _DEG_BATCHELORS
            elif _DEG_GED in match.groupdict() and match.group(_DEG_GED) is not None:
                degree_text = _DEG_GED

            info_dict = {
                'school' : school_text,
                'degree' : degree_text,
            }
            
            candidates.append(overlap.Candidate(
                start, end, match_text, regex, other=info_dict
            ))

    # sort the candidates in DECREASING order of length
    candidates = sorted(candidates, key=lambda x: x.end-x.start)
    return candidates

    if _TRACE:
        print('\tCandidate matches: ')
        index = 0
        for c in candidates:
            regex_index = regex_list.index(c.regex)
            print('\t[{0:2}] R{1:2}\t[{2},{3}): ->{4}<-'.
                  format(index, regex_index, c.start, c.end, c.match_text))
            index += 1
        print()

    # keep the longest of any overlapping matches
    pruned_candidates = overlap.remove_overlap(candidates,
                                               False,
                                               keep_longest=True)

    if _TRACE:
        print('\tCandidate matches after overlap resolution: ')
        index = 0
        for c in pruned_candidates:
            regex_index = regex_list.index(c.regex)
            print('\t[{0:2}] R{1:2}\t[{2},{3}): ->{4}<-'.
                  format(index, regex_index, c.start, c.end, c.match_text))
            index += 1
        print()
    
    return pruned_candidates


###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        print(cleaned_sentence)

    candidates1 = _regex_match(cleaned_sentence, _REGEXES_SOME_SCHOOL)
    print('SOME SCHOOL: ')
    for c in candidates1:
        print('\t{0}, {1}'.format(c.match_text, c.other))

    candidates2 = _regex_match(cleaned_sentence, _REGEXES_GRADUATED)
    print('GRADUATED: ')
    for c in candidates2:
        print('\t{0}, {1}'.format(c.match_text, c.other))

    # determine the highest level of education
    
        
###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':


    # some school, either attending or dropped out
    SENTENCES_1 = [
        'lives at home and attends [**Location (un) 1375**] High School',
        'Pt is a senior at [**Location (un) **] High School',
        'in high school and lives in [**Location 3356**] with his brother',
        'This is an 18yr old high school senior admitted to 11R',        
        "I'm only in High School",
        'Pt is an 18 year old college student',        
        'Mother also attends high school in [**Name (NI) 21**] and is in the 11th grade',        
        'Mom is [**Initials (NamePattern4) **] [**Last Name (NamePattern4) 1486**] ' \
        'in high school and plans to get a home tutor',
        'Employment status: Employed. Pt is high school student',        
        'Pt lives with her dtr, [**Name (NI) 500**], who is [**Initials (NamePattern4) **] ' \
        '[**Last Name (NamePattern4) 3066**] in high school (attending night school)',
        'senior in high school at [**Location (un) 4358**] High',        
        
        'dropped out of HS at tenth grade',
        'he dropped out of high school two years ago',
        'she dropped out of high school when she was in 11th grade',
        'he dropped out of school in his senior year and is presently working',
        'he dropped out of school in 11th grade',
        'she has dropped out of high school',
        'left high school and is studying to get a GED',        
        'fob is still attending high school',
        'he never finished high school',        
        'She states pt lives at home, he dropped out of high school 2 years ago and is unemployed',
        'High school graduate, some college',
        'He did complete some college',
        'Completed some college',
        'Finished high school and took some college courses',
        'he has some college courses',
        'Completed some college level education',        

        # neg
        'There is also evidence of signal dropout on the gradient echo images',
        'Faint area of susceptibility dropout on the GRE images is again noted',
        'Pt is an elementary school principal and lives with his youngest son',
        'found by police after breaking and entering into elementary school',
        'she has two elementary shool age children',
        'and then dropped out of treatment',        
        
    ]

    for sentence in SENTENCES_1:
        print('\n' + sentence)
        results = run(sentence)

    SENTENCES_2  = [
        # graduated from a school        
        'pt graduated high school',
        'he received a HS diploma',        
        'Pt. is a recent high school graduate',
        'pt does construction work and has a high school education',
        'mo completed high school and had planned to attend college when ',
        "Pt recently graduated from high school and is working at Stop'n'Shop",
        

        # has a specific degree
        'she has a Ph.D in chemistry from MIT',
        "later went to grad school for Master's in French Lit.",        
        'Pt has a GED, has worked multiple small jobs through out his life',
        'She has a tenth grade education with a GED.',
        'The patient has a 10th grade education and then obtained his GED.',
        'With his parents support, he quit HS and pursued a GED because of the ' \
        'academic stress he experienced in school',
        'He later obtained his GED',        
        'obtained a GED and attended some college',
        'Reportedly earned GED.',
        'He received his GED while in prison',
        'Pt. did not complete H. S., but did get his GED, and then entered NAVY',
        'is being told, even with a GED, that \"she is over\n   qualified.\"',
        'Dropped out of [**Location (un) **] HS and got his GED.',
        'He recieved his GED and was in the National Guard for 24 years',
        'He has a GED level of education',
        'dropped out of high school, got his GED',
        'reports getting a GED',
        'Education- GED;',
        'Education: GED',
        'She attended high school through the 11th grade, obtained a GED and attended some college',        

        # no match
        'would eventually like to get his GED',
        'Going to get his GED and eventually hopes to work for the EPA',
        'With the microcatheter in this position a series of GED MRI-compatible '\
        'coils were placed to treat the aneurysm',
        'prior to this illness had been attending night school to get her GED',
        'pt electively intubated for GED procedure',
        'Underwent GED, dubhoff tube placed',

        'one of her goals remains to finish high school',
        'exploring option of returning to school and taking some college courses',
        
    ]

    for sentence in SENTENCES_2:
        print('\n' + sentence)
        results = run(sentence)
        
