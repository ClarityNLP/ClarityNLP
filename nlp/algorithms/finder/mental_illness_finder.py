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
_str_header = r'\b[a-z]+:'
_str_header_mi =  _str_header + _str_words + _str_mi
_regex_header_mi = re.compile(_str_header_mi, re.IGNORECASE)

# is mentally ill
_str_is_mi = r'\bis\b' + _str_words + r'(?P<mi>mentally ill)'
_regex_is_mi = re.compile(_str_is_mi, re.IGNORECASE)

# anxiety disorder
_str_anxiety_disorder = r'\b(?P<anxiety>((social )?anxiety|panic) disorder)\b'
_regex_anxiety_disorder = re.compile(_str_anxiety_disorder, re.IGNORECASE)

# phobia
_str_phobia = r'\b(?P<anxiety>(needle|multiple|many|several )?phobias?)'
_regex_phobia = re.compile(_str_phobia, re.IGNORECASE)

# ADHD
_str_adhd = r'\b(?P<adhd>(adhd|attention defecit hyperactivity disorder))'
_regex_adhd = re.compile(_str_adhd, re.IGNORECASE)

_str_header_adhd = _str_header + _str_words + _str_adhd
_regex_header_adhd = re.compile(_str_header_adhd, re.IGNORECASE)

# bipolar disorder
_str_bipolar = r'\b(?P<bipolar>bipolar( disorder)?)\b'
_regex_bipolar = re.compile(_str_bipolar, re.IGNORECASE)

_str_header_bipolar = _str_header + _str_words + _str_bipolar
_regex_header_bipolar = re.compile(_str_header_bipolar, re.IGNORECASE)

# borderline personality disorder
_str_bpd = r'\b(?P<bpd>borderline personality disorder)\b'
_regex_bpd = re.compile(_str_bpd, re.IGNORECASE)

_str_header_bpd = _str_header + _str_words + _str_bpd
_regex_header_bpd = re.compile(_str_header_bpd, re.IGNORECASE)

# depression
_str_depression = r'\b(?P<depression>(depression|depressive disorder))\b'
_regex_depression = re.compile(_str_depression, re.IGNORECASE)

_str_header_depression = _str_header + _str_words + _str_depression
_regex_header_depression = re.compile(_str_header_depression, re.IGNORECASE)

# dissociative disorder
_str_dissociative = r'\b(?P<dissociative>(dissociative|multiple personality) disorder)\b'
_regex_dissociative = re.compile(_str_dissociative, re.IGNORECASE)

_str_header_dissociative = _str_header + _str_words + _str_dissociative
_regex_header_dissociative = re.compile(_str_header_dissociative, re.IGNORECASE)

# eating disorder
_str_eating = r'\b(?P<eating>(eating disorder|anorexi[ac]( nervosa)?|bul[ei]mi[ac]|binge eat(ing|er)))'
_regex_eating = re.compile(_str_eating, re.IGNORECASE)

_str_header_eating = _str_header + _str_words + _str_eating
_regex_header_eating = re.compile(_str_header_eating, re.IGNORECASE)

# OCD
_str_ocd = r'\b(?P<ocd>((?<!dome )ocd(?! (lesion|left|right))|obsessive compulsive disorder))'
_regex_ocd = re.compile(_str_ocd, re.IGNORECASE)

_str_header_ocd = _str_header + _str_words + _str_ocd
_regex_header_ocd = re.compile(_str_header_ocd, re.IGNORECASE)

_str_ocd_ignore = r'\b(talon|joint|elbow|ankle|ligament|bone|cartilage|fracture|tissue|swelling|evidence|spur)s?'
_regex_ocd_ignore = re.compile(_str_ocd_ignore, re.IGNORECASE)

# PTSD
_str_ptsd = r'\b(?P<ptsd>(ptsd|post traumatic stress disorder))'
_regex_ptsd = re.compile(_str_ptsd, re.IGNORECASE)

_str_header_ptsd = _str_header + _str_words + _str_ptsd
_regex_header_ptsd = re.compile(_str_header_ptsd, re.IGNORECASE)

_REGEXES = [
    _regex_history,
    _regex_diagnosis,
    _regex_her_mi,
    _regex_is_mi,
    _regex_header_mi,
    _regex_anxiety_disorder,
    _regex_phobia,
    _regex_adhd,
    _regex_header_adhd,
    _regex_bipolar,
    _regex_header_bipolar,
    _regex_bpd,
    _regex_header_bpd,
    _regex_depression,
    _regex_header_depression,
    _regex_dissociative,
    _regex_header_dissociative,
    _regex_eating,
    _regex_header_eating,
    _regex_ocd,
    _regex_header_ocd,
    _regex_ptsd,
    _regex_header_ptsd,
]


###############################################################################
def _prune_errors(matchobj_list, sentence):

    pruned = []
    for obj in matchobj_list:
        matchobj = obj['matchobj']
        assert 1 == len(matchobj.groupdict())
        skip = False
        for k,v in matchobj.groupdict().items():
            if 'ocd' == k:
                # search sentence for words related to Osteochondritis Dissecans
                match = _regex_ocd_ignore.search(sentence)
                if match:
                    # skip this one
                    skip = True
                    break
                
        if not skip:
            pruned.append(obj)

    return pruned


###############################################################################
def run(sentence):

    results = []
    cleaned_sentence = SDOH.cleanup(sentence)

    if _TRACE:
        DISPLAY(cleaned_sentence)

    matchobj_list = SDOH.regex_match(cleaned_sentence, _REGEXES)
    matchobj_list = _prune_errors(matchobj_list, cleaned_sentence)

    if _TRACE:
        for obj in matchobj_list:
            matchobj = obj['matchobj']
            for k,v in matchobj.groupdict().items():
                DISPLAY('\t{0}: {1}'.format(k.upper(), v))
        

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

        # ADHD
        '27 year old male with a history of substance abuse, bipolar, ADHD, anxiety/depression',
        'Pt is 25yo male with PMH of ADHD',
        'PMHx: schizoaffective, bipolar, MR, ADHD',

        # bipolar disorder
        '52 year old man with bipolar disorder admitted for sycopal episode',
        "55 year old woman with CHF, bipolar disorder, poor ABG's post op.",
        'UNDERLYING MEDICAL CONDITION:  59 year old man with hx bipolar disorder',

        # borderline personality disorder
        'UNDERLYING MEDICAL CONDITION: 32 year old woman with borderline personality disorder, swallowed batteries',
        '26F with history of depression, borderline personality disorder, PTSD',
        'Systolic CHF (EF 45-50%), Bipolar and Borderline Personality Disorder admitted ',

        # depression
        '27 uo M with PMH: polysubstance abuse, depressive disorder and GERD',

        # dissociative disorder
        'PMH: AF, cataracts, high cholesterol, dissociative disorder, HTN',
        'ast Medical History: Suicide attepts over 20 psych admissions Depression ' \
        'Axiety Iron deficiency anemia Cervical dysplasia Anorexia Dissociative disorder ' \
        'Etoh abuse Borderline Personality Disorder ADHD',
        '1 hour after Hd started, pt started to have hallucinations, delerium and multiple personality disorder',
        'PAST MEDICAL HISTORY:  PTSD secondary to abuse as a child. Multiple personality disorder.',

        # eating disorder
        'Reason: eating disorder protocol',
        'FINAL REPORT INDICATION: 25-year-old woman with hypokalemia, anorexia',
        '18 yo F anorexic appearing in the ED with lightheadedness and generalized weakness',
        'Eating disorder (including Anorexia Nervosa, Bulemia)',
        '18 year old woman with pmh significant for anorexia',
        'Email consult was received for h/o eating disorder',
        'She received Ensure tid as part of her eating disorder protocol, along with electrolyte repletion.',
        'Hx: appy, hx of migraines, anorexia, bulimia, ovarian cyst surgery',

        # OCD
        'Pt is a 52F with OCD (stable recently, but h/o OD, anorexia and alcohol use in past',
        'Her husband states that her OCD is stable currently',
        'PMH: OSA, ADD,OCD,COPD, DM',
        'Past medical history: Depression Anxiety Obsessive compulsive disorder with hoarding tendencies',
        'Obsessive-compulsive disorder, depression and increasing memory deficit.',
        'patient is a 27-year-old man with history of obsessive-compulsive disorder and depression',
        
        # OCD negative
        'Reason: assess OCD lesion left talus',
        'No talar dome OCD is identified',
        'consistent with an OCD fracture', 

        # PTSD
        'She has a long psychiatric history including borderline personality disorder and ' \
        'post traumatic stress disorder',
        '41-year old male with a history of depression, post traumatic stress disorder, and suicidal ideation',
        'History remarkable for post-traumatic stress disorder',
        '30 year old woman with h/o MDD, anxiety, PTSD, h/o ingestion of razors, pens, and knives',
        
        # schizoafective disorder
        'PMHx: schizoaffective, bipolar, MR, ADHD',
        
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
