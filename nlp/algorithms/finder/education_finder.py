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


# from Wikipedia, List of doctoral degrees in the US
_DEGREE_MAP = {
    'doctor of arts' : 'da',
    'doctor of business administration' : 'dba',
    'doctor of canon law' : 'jcd',
    'doctor of design' : 'ddes',
    
}

    
# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\b\s?(' + _str_word + r'){0,5}?'
_str_one_or_more_words = r'(' + _str_word + r'){1,5}?'


# words used to state that somebody does NOT have a degree
# (apostrophes are removed in _cleanup)
_str_neg_words = r'\b(without|other than|lacks|understands neither|unable to|cannot|cant|not|non?)\b'
_str_neg_degree = _str_neg_words + _str_words + _str_degree
_regex_neg_degree = re.compile(_str_neg_degree, re.IGNORECASE)

    
###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 2

# set to True to enable debug output
_TRACE = False


###############################################################################
def _cleanup(sentence):
    """
    Apply some cleanup operations to the sentence and return the
    cleaned sentence.
    """

    # convert to lowercase
    sentence = sentence.lower()

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
def run(sentence):

    results = []
    cleaned_sentence = _cleanup(sentence)

    if _TRACE:
        print(cleaned_sentence)


###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':


    SENTENCES = [
        'she has a Ph.D in chemistry from MIT',
        'pt does construction work and has a high school education',
        'mo completed high school and had planned to attend college when ' \
        'she became pregnant',        
        'she graduated high school',
        'lives at home and attends [**Location (un) 1375**] High School',
        'Pt is a senior at [**Location (un) **] High School',
        'in high school and lives in [**Location 3356**] with his brother',
        'allow pt. to attend his High School graduation tomorrow',
        "I'm only in High School",
        'Pt. is a recent high school graduate',
        'Mother also attends high school in [**Name (NI) 21**] and is in the 11th grade',
        "Pt recently graduated from high school and is working at Stop'n'Shop",
        'Mom is [**Initials (NamePattern4) **] [**Last Name (NamePattern4) 1486**] ' \
        'in high school and plans to get a home tutor',
        'Employment status: Employed. Pt is high school student',
        'Pt was identified by his high school ID',
        'Pt lives with her dtr, [**Name (NI) 500**], who is [**Initials (NamePattern4) **] ' \
        '[**Last Name (NamePattern4) 3066**] in high school (attending night school)',
        'Pt also has a son who recently began college',
        'HIGH SCHOOL BIOLOGY TEACHER AWAITS TRANSFER',
        'senior in high school at [**Location (un) 4358**] High',
        'This is an 18yr old high school senior admitted to 11R',
        'He is second to the youngest and due to graduate High School this Weekend',
        'he received a HS diploma',
        'dropped out of HS at tenth grade',
        'he dropped out of high school two years ago',
        'she dropped out of high school when she was in 11th grade',
        'he dropped out of school in his senior year and is presently working',
        'he dropped out of school in 11th grade',
        'she has dropped out of high school',

        "later went to grad school for Master's in French Lit.",

        'Pt is an 18 year old college student',
        'He played football and baseball in high school and then played football ' \
        'in his first (and only) semester of college',
        
        'one of her goals remains to finish high school',
        'patient has been very unhappy in her degree program',
        'will not likely see their son go through his senior year in HS',
        'Pt is [**Initials (NamePattern4) **] [**Last Name (NamePattern4) 3066**] ' \
        'but have been high school sweethearts for past x 14 yrs.',
        'Pt has had issues with etoh and drugs since his sophomore year in high school',        
        
        'fob is still attending high school',
        'he never finished high school',
        'will finish the school year with a tutor',
        'She states pt lives at home, he dropped out of high school 2 years ago and is unemployed',

        'There is also evidence of signal dropout on the gradient echo images'
        'Faint area of susceptibility dropout on the\n GRE images is again noted',
        'Pt is an elementary school principal and lives with his youngest son',
        'found by police after breaking and entering into elementary school',
        'she has two elementary shool age children',

        'pt electively intubated for GED procedure',
        'Underwent GED, dubhoff tube placed',
        'he could not pass a GED exam',
        'is being told, even with a GED, that \"she is over\n   qualified.\"',
        'Occupation: studying for GED',
        'Pt has a GED, has worked multiple small jobs through out his life',
        'With his parent\ns support, he quit HS and pursued a GED because of the ' \
        'academic stress he experienced in school',
        'With the microcatheter in this position a series of GED MRI-compatible '\
        'coils were placed to treat the aneurysm',
        'She has a tenth grade education with a GED.',
        'The patient has a 10th grade education and then obtained his GED.',
        'Reportedly earned GED.',
        'He later obtained his GED',
        'obtained a GED and attended some college',
        'He received his GED while in prison',
        'Dropped out of [**Location (un) **] HS and got his GED.',
        'Pt. did not complete H. S., but did get his GED, and then entered NAVY',
        'studying for final step of GED',
        'Going to school for his GED',
        'He recieved his GED and was in the National Guard for 24 years',
        'She has a GED',
        'He has a GED level of education',
        'dropped out of high school, got his GED',
        'reports getting a GED',
        'left high school and is studying to get a GED',
        'Education- GED;',
        'Education: GED',
        'prior to this illness had been attending night school to get her GED',
        'would eventually like to get his GED',
        'Going to get his GED and eventually hopes to work for the EPA',

        'High school graduate, some college',
        'He did complete some college',
        'Completed some college',
        'Finished high school and took some college courses',
        'She attended high school through the 11th grade, obtained a GED and attended some college',
        'exploring option of returning to school and taking some college courses',
        'he has some college courses',
        'Completed some college level education',

        'and then dropped out of treatment',
        
    ]
