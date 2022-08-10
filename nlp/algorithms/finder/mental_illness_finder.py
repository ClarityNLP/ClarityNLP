#!/usr/bin/evn python3
"""
Module for finding mentions of mental illness.

Conditions recognized (https://www.nami.org/About-Mental-Illness/Mental-Health-Conditions):

    anxiety disorder
        generalized anxiety disorder
        social anxiety disorder
        panic disorder
        phobias (acrophobia, agoraphobia, ...)
    attention defecit hyperactivity disorder (ADHD)
        inattention
        hyperactivity
        impulsivity
    bioplar disorder
    borderline personality disorder
        difficulty regulating emotion
        self-harm
        impulsive behaviors
        intense depression, irritability, or anxiety
    depression
    dissociative disorder
        memory loss of specific times, people, or events
        out-of-body experiences
        sense of detachment
        lack of a sense of self-identity
        dissociative amnesia
        depersonalization disorder
        dissociative identity disorder, multiple personality disorder
    eating disorders
        anorexia, bulimia, binge eating
    obsessive-compulsive disorder (OCD)
    post-traumatic stress disorder (PTSD)
        flaashbacks, nightmares, insomnia, outbursts of anger, hypervigilance
    psychosis
    schizoaffective disorder
        hallucinations
        delusions
        disorganized thoughts
        depression
        manic behavior
    schizophrenia

    statements of general mental illness

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
    import sdoh_common as SDOH    
    import finder_overlap as overlap
    DISPLAY = print
except:
    # ClarityNLP path
    from claritynlp_logging import log, ERROR, DEBUG
    DISPLAY = log
    from algorithms.finder import sdoh_common as SDOH    
    from algorithms.finder import finder_overlap as overlap
    
MENTAL_ILLNESS_FIELDS = [
    'sentence',
    'mental_illness'
]

MentalIllnessTuple = namedtuple('MentalIllnessTuple', MENTAL_ILLNESS_FIELDS)
MentalIllnessTuple.__new__.__defaults__ = (None,) * len(MentalIllnessTuple._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

# set to True to enable debug output
_TRACE = True

# a word, possibly hyphenated or abbreviated
_str_word = r'[-a-z]+\.?\s?'

# nongreedy word captures
_str_words = r'\s?(' + _str_word + r'){0,5}?'

_str_mi = r'\b(?P<mi>mental illness( diagnosis)?)'

# history of mental illness
_str_hist = r'\b((history|setting) of|struggl(ing|e[sd]?) with)'
_str_history =  _str_hist + _str_words + _str_mi
_regex_history = re.compile(_str_history, re.IGNORECASE)

_str_diagnosis = r'\b(diagnos(is|ed)|chronic|known|have|has)' + _str_words + _str_mi
_regex_diagnosis = re.compile(_str_diagnosis, re.IGNORECASE)

# her mental illness
_str_her_mi = r'\b(patients|their|his|her)\b' + _str_words + _str_mi
_regex_her_mi = re.compile(_str_her_mi, re.IGNORECASE)

# Past Medical History: "Mental Illness"
_str_pmhx = r'\b(Past Medical History|pmhx):' + _str_words + _str_mi
_regex_pmhx = re.compile(_str_pmhx, re.IGNORECASE)

# is mentally ill
_str_is_mi = r'\bis\b' + _str_words + r'(?P<mi>mentally ill)'
_regex_is_mi = re.compile(_str_is_mi, re.IGNORECASE)

# anxiety disorder
_str_anxiety_disorder = r'\b(?P<anxiety>((social )?anxiety|panic) disorder)\b'
_regex_anxiety_disorder = re.compile(_str_anxiety_disorder, re.IGNORECASE)

# phobia
_str_phobia = r'\b(?P<anxiety>(needle|multiple|many|several )?phobias?)'
_regex_phobia = re.compile(_str_phobia, re.IGNORECASE)

_REGEXES = [
    _regex_history,
    _regex_diagnosis,
    _regex_her_mi,
    _regex_is_mi,
    _regex_pmhx,
    _regex_anxiety_disorder,
    _regex_phobia,
]


###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = SDOH.cleanup(sentence)

    if _TRACE:
        DISPLAY(cleaned_sentence)

    matchobj_list = SDOH.regex_match(cleaned_sentence, _REGEXES)

    if _TRACE:
        for obj in matchobj_list:
            matchobj = obj['matchobj']
            for k,v in matchobj.groupdict().items():
                DISPLAY('\t{0}: {1}'.format(k.upper(), v))#obj['match_text']))
        

    # for c in candidates:
    #     immigration_status = c.other

    #     obj = ImmigrationTuple(
    #         sentence = cleaned_sentence,
    #         immigration_status = immigration_status
    #     )

    #     results.append(obj)

    # return json.dumps([r._asdict() for r in results], indent=4)


###############################################################################
def get_version():
    path, module_name = os.path.split(__file__)
    return '{0} {1}.{2}'.format(module_name, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':
    
    SENTENCES = [
        'significant history of chronic pain and mental illness',
        'she has had a history of mental illness that went away at the onset of menopause',
        'struggling with mental illness',
        'Mother fearful that pt may not be taken seriously secondary to her mental illness dx',
        'Family recounts that pt has history of mental illness with one significant suicide attempt.',
        "Confused, poorly tracks thoughts, ?pt's baseline given hx of mental illness.",
        'She believes that pt lives on the street and has a history of mental illness ' \
        'although she is not sure of the specifics',
        "They located a suicide note that pt left and are appropriately tearful when " \
        "talking about pt's struggle with mental illness.",
        'Pt is nervous and has a history of mental illness',
        'likely complicated by his mental illness',
        'Pt with a lengthy history of alcohol abuse in the setting of mental illness.',
        'history of increasing agitation in setting of known mental illness',
        'history of chronic pain and mental illness',
        "Concerned re: severity of patient's mental illness/inability to receive meds",
        'he has poor insight into his own mental illness',
        'Pt w/ hx of mental illness and ETOH abuse', 
        'Pt has history of mental illness, ? diagnosis',
        '[**Name (NI) 5892**] is known to have a mental illness and he does not take his medication',
        'He is divorced, his ex wife also has mental illness',
        'chronic mental illness, limited social supports',
        'PMHx:   \"mental illness\" - on disability',
        'PAST MEDICAL HISTORY: -\"mental illness\"',
        'because of her history of malignancy and significant mental illness',
        'has major mental illness which is currently untreated',
        'the patient is severely mentally ill',

        # anxiety disorder
        'Significant medical Hx of depression and anxiety disorder requiring multiple hospitalizations',
        '22 y old male with 2yr history of schizophrenia and anxiety disorder with multiple psychiatric admissions',
        'depressive/anxiety disorder',
        'Pt is nervous and has a slight anxiety disorder , taking xanax prn',
        'She reports an anxiety disorder for which she has sought tx and has been able to manage symptoms',
        'Pregnancy was complicated by anxiety disorder, treated with Lexapro',
        'PT. HAS ANXIETY DISORDER',
        'Pt receives psychiatric care for panic and anxiety disorder',
        'Pt has anxiety disorder and she gets very agitated at times',
        'She has a severe case of social anxiety disorder that can be debilitating',
        'Pt other pmh significant for psoriasis, depression, panic disorder, alcohol abuse',
        'Pt also has multiple phobias and gets very agitated w/ small spaces, restraints, touching etc',
        'The family relates she has long history of phobias and does not like to be touched by or close to people',
        'She has anxiety disorder, various phobias, and mental illness',
        

        # # possible mental illness
        # 'There is also possibly a component of mental illness',
        # 'Pt states that there is a family hx of mental illness',
        # 'Social History: ? mental illness',
        
        # # somebody else
        # 'biggest concern was contacting his brother who is currently in CA and has ' \
        # 'recently been dx with some form of mental illness',
        # 'Daughter expresses concern that pts son, who has mental illness, may become agitated ',
        # 'DAUGHTER W/HX MENTAL ILLNESS PER HER HUSBAND',
        # 'for people with mental illness',
        # 'he patient was born and raised in [**Location (un) 86**] to parents who both had mental illness',
        # "son has hx of untreated mental illness, and cannot adequately provide for pt's needs",

        # negated
        'He was evaluated by psychiatry who did not feel that he had a mental illness',
        'and has not been found to have sx. major depression or other mental illness',
        'Yet there is no mention in Ms. [**Known patient lastname 9259**]s chart about any mental illness',
        'she has not been found to have a major mental illness incl. major depression, bipolar disorder or psychosis',
        'Patient denies family medical history of mental illness',
        'A psychiatric evaluation was performed, there was no evidence of mental illness ' \
        'other than severe alcohol dependence',
        'The patient denies any significant social stressors and she did not have any features ' \
        'of generalized anxiety disorder or other specific phobias',

        
        '"Pt is 25yo male with PMH of ADHD\n   Trauma, s/p sword injury to R hand, nerve and tendon repair of 2,3,4^th\n   fingers, amp of 5^th finger\n   Assessment:\n   Pt received from OR (11hr case), R hand in pillow splint,  ulnar artery\n   repair.\n   Action:\n   Ulnar artery pulse on 4^th finger Dopplerable q1h, adequate CSM to R\n   fingers, hand elevated on pillow,Hep drip\n   Ancef q8h\n   Response:\n   Pulse Dopplerable with good quality, fingers w/good CSM\n   Plan:\n   Continue current plan of care, PTT q6h,assess for infection\n   Anxiety\n   Assessment:\n   Pt w/baseline anxiety disorder,ADHD, on prescription meds, self-\n   medicates w/ETOH,marijuana, family members\n prescription meds,\n   extremely anxious on admit\n   Action:\n   Valium 5mg ivp, 5mg PO. Dilaudid IV prn, PCA initiated,Lexapro daily\n   dose given. Father at bedside for several hours with good effect\n   Much reassurance and encouragement given\n   Response:\n   Pt sleeping in naps, calmer overnight\n   Plan:\n   Valium prn, emotional support\n   Acute Pain\n   Assessment:\n   Pain r/t amp of finger, nerve surgery\n   Action:\n   PCA initiated,   pt using appropriately\n   Response:\n   Pt still c/o pain [**10-2**], states pain med works for a short time- pt\n   sleeping in naps\n   Plan:\n   Continue PCA, prn Valium\n   Assessment:\n   Action:\n   Response:\n   Plan:\n",',

    ]
    
    
    
    for sentence in SENTENCES:
        DISPLAY('\n' + sentence)
        run(sentence)
