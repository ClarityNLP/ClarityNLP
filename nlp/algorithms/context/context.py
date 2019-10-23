import re
import os
import traceback
from enum import Enum
from claritynlp_logging import log, ERROR, DEBUG

SCRIPT_DIR = os.path.dirname(__file__)

over_several_period_rule = re.compile(r"(within the last|in the last|for the past|for the last|over the past|over the last|for)(\s+\d*(\.\d*)*|\s+(\w+)(\s+\w*)?(\s+\w*)?(\s+\w*)?(\s+\w*)?(\s+\w*)?)?(\s+days|\s+day)", re.IGNORECASE|re.MULTILINE)
for_the_past_period_rule = re.compile(r"(for the past|for the last|over the past|over the last|for)(\s+\d*(\.\d*)*|\s+(\w+)(\s+\w*)?(\s+\w*)?(\s+\w*)?(\s+\w*)?(\s+\w*)?)?(\s+weeks|\s+week|\s+months|\s+month|\s+years|\s+year)", re.IGNORECASE|re.MULTILINE)
space_rule = r"[\s+]"
negative_window = 4
all_terms = dict()
inited = False


def load_terms(key):
    try:
        path = os.path.join(SCRIPT_DIR, "data/%s_triggers.txt" % key)
        # log(path)
        with open(path) as f:
            triggers = f.read().splitlines()
            return triggers
    except Exception as e:
        log(e, ERROR)
        log("cannot open %s_triggers.txt" % key, ERROR)


    return []


def context_init():
    log("Context init...")
    global inited
    global all_terms
    if not inited:
        all_terms["negated"] = load_terms("negex")
        all_terms["experiencier"] = load_terms("experiencer")
        all_terms["historical"] = load_terms("history")
        all_terms["hypothetical"] = load_terms("hypothetical")

        inited = True
    return all_terms


class ContextFeature(object):

    def __init__(self, target_phrase, matched_phrase, sentence, eval_sentence, context_type):
        self.target_phrase = target_phrase
        self.matched_phrase = matched_phrase
        self.sentence = sentence
        self.eval_sentence = eval_sentence
        self.context_type = context_type


class ContextResult(object):

    def __init__(self, phrase, sentence, temporality, experiencier, negex):
        self.phrase = phrase
        self.sentence = sentence
        self.temporality = temporality
        self.experiencier = experiencier
        self.negex = negex

    def __repr__(self):
        return '%s(%s, %s, %s, %s, %s)' % (self.__class__.__name__, self.phrase, self.sentence, str(self.temporality),
                                           str(self.experiencier), str(self.negex))


class Temporality(Enum):
    Recent = "Recent"
    Historical = "Historical"
    Hypothetical = "Hypothetical"


class Experiencer(Enum):
    Patient = "Patient"
    Other = "Other"


class Negation(Enum):
    Affirmed = "Affirmed"
    Negated = "Negated"
    Possible = "Possible"


feature_map = {
    "negated": Negation.Negated,
    "possible": Negation.Possible,
    "experiencier": Experiencer.Other,
    "historical": Temporality.Historical,
    "hypothetical": Temporality.Hypothetical
}

windows = {
    "negated": 5,
    "experiencier": 8,
    "historical": 8,
    "hypothetical": 5
}


def stop_trigger(ipt: str):
    return ipt.startswith("[CONJ]") or ipt.startswith("[PSEU]") or ipt.startswith("[POST]")  or ipt.startswith("[PREN]")  or ipt.startswith("[PREP]") or ipt.startswith("[POSP]") or ipt.startswith("[FSTT]") or ipt.startswith("[ONEW]")
  

def run_individual_context(sentence: str, target_phrase: str, key: str, rules, phrase_regex):
    found = []
    custom_window = windows[key]

    try:
        target_replace = repr(target_phrase).replace(" ", "_")
        eval_sentence = sentence.replace(target_phrase, target_replace)
        eval_sentence = ".%s." % eval_sentence

        if key == "historical":
            over_several_period_match = re.findall(over_several_period_rule, eval_sentence)
            if any(True for _ in over_several_period_match):
                rules.append("%s\t\t[CONJ]" % over_several_period_match[0][0].strip())

            for_the_past_period_match = re.findall(for_the_past_period_rule, eval_sentence)
            if any(True for _ in for_the_past_period_match):
                rules.append("%s\t\t[CONJ]" % for_the_past_period_match[0][0].strip())

        rules.sort(key=len, reverse=True)

        rule_match = 0
        for rule in rules:
            rule_tokens = rule.strip().split('\t\t')
            rule_text = rule_tokens[0]

            rule_builder_regex = re.compile(r"\b(%s)\b" % rule_text, re.IGNORECASE | re.MULTILINE)
            all_matched = re.finditer(rule_builder_regex, eval_sentence)
            if all_matched:
                prev_end = 0
                new_eval_sentence = ''
                for matched in all_matched:
                    start = matched.start()
                    end   = matched.end()
                    tokens = rule_tokens[1].strip().split("[")
                    match_text = str(matched.group(0)).strip().replace(" ", "_")
                    repl = "[%s%s[/%s" % (tokens[1], match_text, tokens[1])
                    rule_match += 1
                    new_eval_sentence += eval_sentence[prev_end:start]
                    new_eval_sentence += repl
                    prev_end = end
                new_eval_sentence += eval_sentence[prev_end:]
                eval_sentence = new_eval_sentence

            if rule_match > 0:
                eval_sentence = eval_sentence.replace("_", " ")
                eval_sentence = eval_sentence[1:eval_sentence.strip().rfind('.')]

                sentence_tokens = eval_sentence.strip().split(' ')
                matched_phrase = ''
                sentence_tokens_length = len(sentence_tokens)
                i = -1

                for sentence_token in sentence_tokens:
                    i += 0
                    stripped = sentence_token.strip()
                    if stripped.startswith("[PREN]") or stripped.startswith("[FSTT]") or stripped.startswith("[ONEW]"):
                        j = i + 1
                        break_trigger = False
                        while j < sentence_tokens_length:
                            matched_phrase += (sentence_tokens[j] + " ")
                            if j >= (sentence_tokens_length - 1) or j > custom_window or stop_trigger(sentence_tokens[j].strip()):
                                break_trigger = True

                            if break_trigger:
                                phrase_regex_matches = re.finditer(phrase_regex, matched_phrase)
                                if any(True for _ in phrase_regex_matches):
                                    found.append(ContextFeature(target_phrase, matched_phrase, sentence, eval_sentence,
                                                                key))
                                    break_trigger = False
                                    matched_phrase = ''
                            j += 1

                    if stripped.startswith("[POST]") or stripped.startswith("[FSTT]"):
                        j = i - 1
                        break_trigger = False
                        while j >= 0:
                            matched_phrase = " " + sentence_tokens[j]
                            if j == 0 or j < (i - negative_window) or stop_trigger(sentence_tokens[j].strip()):
                                break_trigger = True

                            if break_trigger:
                                phrase_regex_matches = re.finditer(phrase_regex, matched_phrase)
                                if any(True for _ in phrase_regex_matches):
                                    found.append(ContextFeature(target_phrase, matched_phrase, sentence, eval_sentence,
                                                                key))
                                    break_trigger = False
                                    matched_phrase = ''
                            j -= 1

    except Exception as e:
        log(e, ERROR)

    return found


def replace_all_matches(regex, expected_term, sentence):
    prev_end = 0
    new_sentence = ''
    iterator = regex.finditer(sentence)
    for match in iterator:
        start = match.start()
        end   = match.end()
        new_text  = ' no ' + expected_term
        new_sentence += sentence[prev_end:start]
        new_sentence += new_text
        prev_end = end

    if 0 == prev_end:
        return sentence
    else:
        new_sentence += sentence[prev_end:]
        return new_sentence

def replace_dash_as_negation(expected_term, sentence):

    # match a dash that precedes a word only if whitespace precedes the dash
    str_negated_term = r'\s-\s*' + expected_term + r'\b'
    regex_negated_term = re.compile(str_negated_term, re.IGNORECASE)
    return replace_all_matches(regex_negated_term, expected_term, sentence)

def replace_future_occurrence_as_current_negation(expected_term, sentence):

    word = r'\b[a-z]+\b\s*'
    words = r'(' + word + r')+?'        # nongreedy
    words_0_to_n = r'(' + word + r')*?' # nongreedy

    str_instructions = r'\b(give|take|prescribe|rx)\s+' + words +\
                       r'\b(for|in\s+case\s+of|if|when)\s+'     +\
                       expected_term + r'\b'
    regex_instructions = re.compile(str_instructions, re.IGNORECASE)
    sentence = replace_all_matches(regex_instructions, expected_term, sentence)

    # no trailing r'\b' to handle plural forms of final word
    str_if_1 = r'\b(if|should)\s+' + words_0_to_n + expected_term              +\
               r'\s+(should\s+)?'                                              +\
               r'\b(appear|arise|begin|crop\s+up|commence|come\s+to\s+light|'  +\
               r'come\s+into\s+being|develop|emanate|emerge|ensue|exhibit|'    +\
               r'happen|occur|originate|result|set\s+in|start|take\s+place)'
    regex_if_1 = re.compile(str_if_1, re.IGNORECASE)
    sentence = replace_all_matches(regex_if_1, expected_term, sentence)

    str_if_2 = r'\b(if|should)\s+' + words_0_to_n                        +\
               r'\b(commences?|develops?|exhibits?|happens?|presents?|'  +\
               r'results?(\s+in)?|sets?\s+in|starts?|takes?\s+place)\s+' +\
               words_0_to_n + expected_term + r'\b'
    regex_if_2 = re.compile(str_if_2, re.IGNORECASE)
    sentence = replace_all_matches(regex_if_2, expected_term, sentence)

    str_in_case_of = r'\b(in\s+case\s+of|should\s+there\s+be|should|' +\
                     r'(look|watch)\s+(out\s+)?for)\s+'               +\
                     words_0_to_n + expected_term + r'\b'
    regex_in_case_of = re.compile(str_in_case_of, re.IGNORECASE)
    sentence = replace_all_matches(regex_in_case_of, expected_term, sentence)

    return sentence

class Context(object):

    def __init__(self):
        log("Context init...")
        self.terms = context_init()

    def run_context(self, expected_term, sentence):

        original_sentence = sentence
        sentence = replace_dash_as_negation(expected_term, sentence)
        sentence = replace_future_occurrence_as_current_negation(expected_term, sentence)

        features = []
        phrase_regex = re.compile(r"(\b|\]\[)%s(\b|\]\[)" % expected_term, re.IGNORECASE)
        for key, terms in self.terms.items():
            found = run_individual_context(sentence, expected_term, key, terms, phrase_regex)
            if found:
                features.extend(found)

        temporality = Temporality.Recent
        experiencer = Experiencer.Patient
        negation = Negation.Affirmed
        for feature in features:
            mapped_feature = feature_map[feature.context_type]
            if mapped_feature:
                if isinstance(mapped_feature, Temporality):
                    temporality = mapped_feature
                elif isinstance(mapped_feature, Negation):
                    negation = mapped_feature
                elif isinstance(mapped_feature, Experiencer):
                    experiencer = mapped_feature

        return ContextResult(expected_term, original_sentence, temporality, experiencer, negation)


if __name__ == '__main__':
    ctxt = Context()
    m1 = ctxt.run_context("pass out",
                 "She had definite   presyncope with lightheadedness and dizziness as if she was going to PASS OUT.")
    m2 = ctxt.run_context("coronary artery disease",
                 "MEDICAL HISTORY:   Atrial fibrillation, hypertension, arthritis, CORONARY ARTERY DISEASE, GERD,   cataracts, and cancer of the left eyelid.")
    m3 = ctxt.run_context("hypertension",
                 "Ms. **NAME[AAA] is a very pleasant **AGE[in 80s]-year-old female with a history of hypertension   who was transferred to **INSTITUTION from an outside hospital because of NECROTIZING   PANCREATITIS.")
    m4 = ctxt.run_context("PANCREATITIS",
                 "Ms. **NAME[AAA] is a very pleasant **AGE[in 80s]-year-old female with a history of hypertension   who was transferred to **INSTITUTION from an outside hospital because of NECROTIZING   PANCREATITIS.")
    m5 = ctxt.run_context("gallops", "Heart - Regular rate and rhythm, no   MURMURS, gallops, or rubs.")
    m6 = ctxt.run_context("edema", "Extremities reveal no peripheral cyanosis or EDEMA")
    m7 = ctxt.run_context("pneumonia", "However, no evidence of pleural effusion or acute pneumonia. ")
    m8 = ctxt.run_context("dementia", "The patient has no evidence of dementia, but has a history of diabetes")
    m9 = ctxt.run_context("nausea", "He has had signs of nausea and vomiting for the past 2 weeks")
    m10 = ctxt.run_context("heart attack", "FAMILY HISTORY: grandmother recently suffered heart attack")
    m11 = ctxt.run_context("heart attack", "Pt with three children and 1 grandaughter, pt voiced concerns over grandaughter and son (pt son 36 y/o had heart attack in FL).")
    m12 = ctxt.run_context("fevers", "Patient condition: -fevers, - chills, - Weight Loss, alert")
    m13 = ctxt.run_context("chills", "Patient condition: -fevers, - chills, - Weight Loss, alert")
    m14 = ctxt.run_context("weight loss", "Patient condition: -fevers, - chills, - Weight Loss, alert")
    m15 = ctxt.run_context("chills", "Instructions to patient: take Tylenol for chills.")
    m16 = ctxt.run_context("fever", "Should fever appear, take Tylenol as indicated.")
    m17 = ctxt.run_context("chills", "Take as prescribed; should there be chills or fever do as instructed.")
    m18 = ctxt.run_context("fever", "Take as prescribed; should there be chills or fever do as instructed.")
    m19 = ctxt.run_context("shortness of breath", "In case of severe shortness of breath do as instructed.")
    m20 = ctxt.run_context("problem", "If a problem arises, follow the instructions.")
    m21 = ctxt.run_context("problems", "In case of problems with the patient's breathing do as instructed.")
    m22 = ctxt.run_context("shortness of breath", "If the patient develops shortness of breath, do as instructed.")

    log(m1)
    log(m2)
    log(m3)
    log(m4)
    log(m5)
    log(m6)
    log(m7)
    log(m8)
    log(m9)
    log(m10)
    log(m11)
    log(m12)
    log(m13)
    log(m14)
    log(m15)
    log(m16)
    log(m17)
    log(m18)
    log(m19)
    log(m20)
    log(m21)
    log(m22)
