#!/usr/bin/env python3
"""

Module for finding a patient's primary language.

"""

import os
import re
import sys


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = True


# some world languages and other forms that have been seen in clinical notes
_LANGUAGES = [
    'afrikaans',
    'amharic',
    'arabic',
    'armenian',
    'assamese',
    'azerbaijani',
    'bavarian',
    'bengali','bangla',
    'bojpuri',
    'burmese',
    'cambodian',
    'cantonese','cantanese',
    'cebuano',
    'chhattisgarhi',
    'chittagonian',
    'chinese','mandarin',
    'creole',
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
    'magahi',
    'maithili',
    'malayalam',
    'malaysian','malay',
    'marathi',
    'mongolian',
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
    'serbo-croatian','serbo croatian','serbocroatian',
    'sign language',
    'sinhalese',
    'sindhi',
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

# build regex string for recognizing languages
_languages = sorted(_LANGUAGES, key=lambda x: len(x), reverse=True)
_languages = [re.escape(s) for s in _languages]
_str_language = r'(' + r'|'.join(_languages) + r')'

print(_str_language)


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
    sentence = re.sub(r'\->', ' ', sentence)

    # erase commas
    sentence = re.sub(r',', '', sentence)

    # replace other chars with whitespace
    sentence = re.sub(r'[&(){}\[\]:~/;]', ' ', sentence)

    # collapse repeated whitespace
    sentence = re.sub(r'\s+', ' ', sentence)

    if _TRACE:
        print('sentence after cleanup: "{0}"'.format(sentence))

    return sentence
    

###############################################################################
def run(sentence):

    cleaned_sentence = _cleanup(sentence)

    result = cleaned_sentence
    return result
    

###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':


    SENTENCES = [
        'interacting w/ sign language w/ daughter',
        'pt is deaf, understands sign language, and is able to read lips',
        'russian translator @ bedside',
        'russian speaking only->limited understanding of english',
    ]

    for sentence in SENTENCES:
        result = run(sentence)

"""

handle these also: sign language, indian, creole, armenian, cambodian
                   portugese and portuguese
                   cantanese and cantonese

             more communicative using american sign language
                able to communicate with basic sign language
          communication to family and staff by sign language
                attempting to communicate with sign language
able to communicate through simple phrases and sign language
                                speaks through sign language
                                interacting w/ sign language w/ daughter
        able to understand family members with sign language
                                 parents speak sign language only
                          pt communicates with sign language
                               communicating c sign language
                                          deaf sign language
                       pt is deaf, understands sign language, and is able to read lips
                             pt does not speak sign language

pt is deaf and can read lips
   however able to read lips

          she is deaf and her primary language is Persian
american sign language is her primary language
                             maternal language canadian french


garbled speech per russian speaking nurse
                   russian speaking male
                frequently shouting in Russian interpreter provided
                            yelling in what seemed to be japanese


                      pt only speaks farsi, understands little/no english
                          she speaks only farsi
                           pt spoke spanish and it was translated by translator
                              speaks farsi only
                    begins to speak danish
                              speaks a dilalect of mandarin called fuzhou
                co-worker who speaks fluent creole, was able to interpret
                  are chinese speaking and will require an interpreter
           52 yr old mandarin speaking woman
                     mandarin speaking only
               neuro-mandarin speaking only
                  pt is farsi speaking only
                      spanish speaking primarily
                pt is russian speaking primarily, understands some english
                        farsi speaking with little english understanding
              persian (farsi) speaking only
          52 yo woman chinese speaking
           patient is chinese-speaking
             patient is hindi speaking
                    pt creole speaking
            primarily spanish speaking
            primarily chinese speaking but speaks english
   who is primarily cambodian speaking
pt is primaily french/swahili speaking
     family is mainly chinese speaking
             portugese-creole speaking female
                      russian speaking only-limited understanding of english
                      russian speaking only->limited understanding of english
                  non english speaking
                  non-english speaking individuals
                     does not speak english

language barrier, farsi

                                             spanish translator
                                     seen with farsi interpreter
                                               farsi translator in to evaluate pt
                                       sign language translator at bedside
                                             russian translator @ bedside
                      communicates via sign language interpreter
                                with aid of japanese interpreter
                        met with family and mandarin interpreter
                           met parents with mandarin interpreter
                                               farsi interpreter present
     patient was deaf, and an american sign language interpreter was utilized
                              american sign language interpreter present
                                   per sign language interpreter
                                       sign-language interpreter
                                       sign language interpreter was called and translated
                       needs a russian sign language interpreter


               english as her primary language
                   portuguese primary language
                          yet primary language is portugese
        english or spanish as primary language
                        mom's primary language is portugese
                     patients primary language is farsi and does not comprehend much english
                              primary language spanish
                              primary language creole
                              primary language french, swahili, some broken english

                              primary language of the caregiver other than english

danish only at breakfast
"""
