#!/usr/bin/env python3
"""

Module for finding a patient's primary language.

"""

import os
import re
import sys
from collections import namedtuple

if __name__ == '__main__':
    # interactive testing
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


LANGUAGE_TUPLE_FIELDS = [
    'sentence',
    'languages', # list of primary languages
]

LanguageTuple = namedtuple('LanguageTuple', LANGUAGE_TUPLE_FIELDS)

# set default value of all fields to None
LanguageTuple.__new__.__defaults__ = (None,) * len(LanguageTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 2

# set to True to enable debug output
_TRACE = False

# some world languages and other forms that have been seen in clinical notes
_LANGUAGES = [
    'afrikaans',
    'albanian',
    'amharic',
    'arabic',
    'armenian',
    'assamese',
    'azerbaijani',
    'bavarian',
    'belarusian',
    'bengali','bangla',
    'bojpuri',
    'bosnian',
    'bulgarian',
    'burmese',
    'cambodian',
    'cantonese','cantanese',
    'cebuano',
    'chhattisgarhi',
    'chittagonian',
    'chinese','mandarin',
    'creole',
    'croatian',
    'czech','czechoslovokian','bohemian',
    'danish',
    'dari',
    'deccan','deccani','dakni','dakhni','dakkhani','dakkani',
    'dutch','flemish',
    'english',
    'estonian',
    'farsi','persian',
    'finnish','suomi',
    'french',
    'fula','fulani','fulah',
    'gaelic','irish',
    'georgian',
    'german',
    'greek',
    'gujarati',
    'hausa',
    'hebrew',
    'hindi','hindustani','indian',
    'hmong',
    'hungarian',
    'icelandic',
    'igbo',
    'indonesian',
    'italian',
    'japanese',
    'javanese',
    'kannada',
    'kazakh',
    'khmer',
    'kinyarwanda',
    'korean',
    'kurdish',
    'ladino',
    'lao','laotian',
    'latvian',
    'lithuanian',
    'macedonian',
    'magahi',
    'maithili',
    'malayalam',
    'malaysian','malay',
    'maltese',
    'marathi',
    'mongolian',
    'montenegrin','montonegrin',
    'nepali',
    'norwegian','norsk',
    'odia',
    'pashto',
    'polish',
    'portuguese','portugese',
    'punjabi',
    'romanian','rumanian','roumanian','moldovan',
    'rundi','kirundi',
    'russian',
    'saraiki',
    'serbian',
    'serbocroatian', # single-word only
    'signlanguage',  # single-word only
    'sinhalese',
    'sindhi',
    'slovak',
    'slovene','slovenian',
    'somali',
    'spanish',
    'swedish','svenska',
    'sunda',
    'swahili','kiswahili','shikomor','comorian',
    'sylheti',
    'tagalog','filipino',
    'tajik','tajiki','tadzhiki',
    'tamil',
    'telugu',
    'thai',
    'tibetan',
    'turkish',
    'turkmen',
    'tunisian','tounsi',
    'ukranian',
    'urdu',
    'urhobo',
    'uyghur','uighur',
    'uzbek',
    'vietnamese',
    'welsh',
    'yiddish',
    'yoruba',
    'zulu',
]

# replace multi-word languages with single words
_REPLACEMENTS = {
    'sign language' : 'signlanguage',
    'serbo croatian' : 'serbocroatian',
}

_INV_REPLACEMENTS = {v:k for k,v in _REPLACEMENTS.items()}

# build regex string for recognizing languages
_languages = sorted(_LANGUAGES, key=lambda x: len(x), reverse=True)
_languages = [re.escape(s) for s in _languages]
_str_language = r'\b(' + r'|'.join(_languages) + r')\b'

# match a single language
_regex_language = re.compile(_str_language, re.IGNORECASE)


# recognize multiple languages separated by 'and', 'or', 'nor', or space
_str_languages = r'(?P<languages>((' + _str_language + r'(and|n?or| ))+)?' +\
    r'(and|n?or| )?[ ]?' + _str_language + r')'

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\b\s?(' + _str_word + r'){0,5}?'
_str_one_or_more_words = r'(' + _str_word + r'){1,5}?'

# words used to state that somebody does NOT speak a language
# (apostrophes are removed in _cleanup)
_str_neg_words = r'\b(without|other than|lacks|understands neither|unable to|cannot|cant|not|non?)\b'
_str_neg_language = _str_neg_words + _str_words + _str_languages
_regex_neg_language = re.compile(_str_neg_language, re.IGNORECASE)

# ... English as the primary language
_str_primary1 = _str_languages + _str_words + r'\bprimary languages?\b'
_regex_primary1 = re.compile(_str_primary1, re.IGNORECASE)

# ...primary language is English...
_str_primary2 = r'\bprimary languages?\b' + _str_words + _str_languages
_regex_primary2 = re.compile(_str_primary2, re.IGNORECASE)

# ....needs a Spanish interpreter...
_str_interp = r'(?P<languages>' + _str_language + r')' + _str_words +\
    r'\b(interpret(e|o)r|translat(e|o)r)\b'
_regex_interp = re.compile(_str_interp, re.IGNORECASE)

# ....Mandarin speaking woman...
_str_l_speaking = _str_languages + r'\s?' + r'\bspeaking\b'
_regex_l_speaking = re.compile(_str_l_speaking, re.IGNORECASE)

# ...patient only speaks French...
_str_speak = r'\b(speak(ing|s)?|spoken?|talk(ing|ed|s)?|shout(ing|ed|s)|yell(ing|ed|s))\b' + _str_words + _str_languages
_regex_speak = re.compile(_str_speak, re.IGNORECASE)

# ...patient communicates with sign language...
_str_comm = r'\b(communicat(ive|ion|ing|es?)|understand(ing|s)?|interact(ing|ion|s)?)\b' +\
    _str_words + _str_languages
_regex_comm = re.compile(_str_comm, re.IGNORECASE)


_REGEXES = [
    _regex_primary1,
    _regex_primary2,
    _regex_interp,
    _regex_l_speaking,
    _regex_speak,
    _regex_comm,
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

    # replace multi-word languages with single words
    for old, new in _REPLACEMENTS.items():
        sentence = re.sub(old, new, sentence)

    return sentence
    

###############################################################################
def _regex_match(sentence, regex_list):
    """
    """

    sentence_save = sentence
    
    # erase any negated languages from the sentence, then attempt regexes
    neg_match = _regex_neg_language.search(sentence)
    if neg_match:
        if _TRACE:
            print('NEG LANGUAGE MATCH: "{0}"'.format(neg_match.group()))
        sentence = sentence[:neg_match.start()] + sentence[neg_match.end():]
    
    candidates = []
    for i, regex in enumerate(regex_list):
        iterator = regex.finditer(sentence)
        for match in iterator:
            # strip any trailing whitespace (invalidates match.end())
            match_text = match.group().rstrip()
            start = match.start()
            end = start + len(match_text)

            # isolate the matching language(s)
            language_text = match.group('languages').strip()
            
            candidates.append(overlap.Candidate(
                start, end, match_text, regex, other=language_text
            ))

    # sort the candidates in DECREASING order of length
    candidates = sorted(candidates, key=lambda x: x.end-x.start)

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
    
    candidates = _regex_match(cleaned_sentence, _REGEXES)

    for c in candidates:
        # extract each language from matching string of languages, stored in c.other
        language_list = []
        it2 = _regex_language.finditer(c.other)
        for match2 in it2:
            language_text = match2.group().rstrip()
            # restore space in 'signlanguage' and others
            if language_text in _INV_REPLACEMENTS:
                language_text = _INV_REPLACEMENTS[language_text]
            language_list.append(language_text)

        num_languages = len(language_list)
        assert num_languages > 0

        obj = LanguageTuple(
            sentence = cleaned_sentence,
            languages = language_list
        )

        results.append(obj)

    return results


###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':


    SENTENCES = [
        'english as her primary language',
        'portuguese primary language',
        'yet primary language is portugese',
        'english or spanish as primary language',
        "mom's primary language is portugese",
        'patients primary language is farsi and does not comprehend much english',
        'primary language spanish',
        'primary language creole',
        'primary language french, swahili, some broken english',
        'primary language of the caregiver other than english',
        'she understands neither english nor spanish',
        'english or spanish as primary language',
        'primary languages are serbo-croatian, sign language, and swahili',
        'american sign language is her primary language',

        'spanish translator',
        'seen with farsi interpreter',
        'farsi translator in to evaluate pt',
        'sign language translator at bedside',
        'russian translator @ bedside',
        'communicates via sign language interpreter',
        'with aid of japanese interpreter',
        'met with family and mandarin interpreter',
        'met parents with mandarin interpreter',
        'farsi interpreter present',
        'patient was deaf, and an american sign language interpreter was utilized',
        'american sign language interpreter present',
        'per sign language interpreter',
        'sign-language interpreter',
        'sign language interpreter was called and translated',
        'needs a russian sign language interpreter',

        'are chinese speaking and will require an interpreter',
        '52 yr old mandarin speaking woman',
        'mandarin speaking only',
        'neuro-mandarin speaking only',
        'pt is farsi speaking only',
        'spanish speaking primarily',
        'pt is russian speaking primarily, understands some english',
        'farsi speaking with little english understanding',
        'persian (farsi) speaking only',
        '52 yo woman chinese speaking',
        'patient is chinese-speaking',
        'patient is hindi speaking',
        'pt creole speaking',
        'primarily spanish speaking',
        'primarily chinese speaking but speaks english',
        'who is primarily cambodian speaking',
        'pt is primaily french/swahili speaking',
        'family is mainly chinese speaking',
        'portugese-creole speaking female',
        'russian speaking only-limited understanding of english',
        'russian speaking only->limited understanding of english',
        'non english speaking',
        'non-english speaking individuals',

        'pt only speaks farsi, understands little/no english',
        'she speaks only farsi',
        'pt spoke spanish and it was translated by translator',
        'speaks farsi only',
        'begins to speak danish',
        'speaks a dilalect of mandarin called fuzhou',
        'co-worker who speaks fluent creole, was able to interpret',

        'more communicative using american sign language',
        'able to communicate with basic sign language',
        'communication to family and staff by sign language',
        'attempting to communicate with sign language',
        'able to communicate through simple phrases and sign language',
        'speaks through sign language',
        'interacting w/ sign language w/ daughter',
        'able to understand family members with sign language',
        'parents speak sign language only',
        'pt communicates with sign language',
        'communicating c sign language',
        'pt is deaf, understands sign language, and is able to read lips',
        'pt does not speak sign language',

        'frequently shouting in Russian interpreter provided',
        'yelling in what seemed to be japanese',
    ]

    for sentence in SENTENCES:
        print(sentence)
        results = run(sentence)
        for r in results:
            if len(r.languages) > 0:
                for l in r.languages:
                    print('\t{0}'.format(l))

                    
"""

pt is deaf and can read lips
   however able to read lips

language barrier, farsi
'deaf sign language',


danish only at breakfast
"""
