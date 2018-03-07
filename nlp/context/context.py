import re
import os
import traceback
from enum import Enum

SCRIPT_DIR = os.path.dirname(__file__)

over_several_period_rule = re.compile(r"(within the last|in the last|for the past|for the last|over the past|over the last|for)(\s+\d*(\.\d*)*|\s+(\w+)(\s+\w*)?(\s+\w*)?(\s+\w*)?(\s+\w*)?(\s+\w*)?)?(\s+days|\s+day)", re.IGNORECASE|re.MULTILINE)
for_the_past_period_rule = re.compile(r"(for the past|for the last|over the past|over the last|for)(\s+\d*(\.\d*)*|\s+(\w+)(\s+\w*)?(\s+\w*)?(\s+\w*)?(\s+\w*)?(\s+\w*)?)?(\s+weeks|\s+week|\s+months|\s+month|\s+years|\s+year)", re.IGNORECASE|re.MULTILINE)
space_rule = r"[\s+]"
negative_window = 4


def load_terms(key):
    try:
        path = os.path.join(SCRIPT_DIR, "data/%s_triggers.txt" % key)
        print(path)
        with open(path) as f:
            triggers = f.read().splitlines()
            return triggers
    except Exception as e:
        print("cannot open %s_triggers.txt" % key)
        print(e)

    return []


print("Context init...")
all_terms = {
    "negated": load_terms("negex"),
    "experiencier": load_terms("experiencer"),
    "historical": load_terms("history"),
    "hypothetical": load_terms("hypothetical")
}


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


def load_terms(key):
    try:
        path = os.path.join(SCRIPT_DIR, "data/%s_triggers.txt" % key)
        print(path)
        with open(path) as f:
            triggers = f.read().splitlines()
            return triggers
    except Exception as e:
        print("cannot open %s_triggers.txt" % key)
        print(e)

    return []


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
                for matched in all_matched:
                    tokens = rule_tokens[1].strip().split("[")
                    match_text = str(matched.group(0)).strip().replace(" ", "_")
                    repl = "[%s%s[/%s" % (tokens[1], match_text, tokens[1])
                    repl_sent = "%s%s%s" % (eval_sentence[0:matched.start()], repl, eval_sentence[matched.end():len(
                        eval_sentence)])
                    eval_sentence = repl_sent
                    rule_match += 1

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
        print(e)
        traceback.print_exc()

    return found


class Context(object):

    def __init__(self):
        print("Context init...")
        self.terms = all_terms

    def run_context(self, expected_term, sentence):
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

        return ContextResult(expected_term, sentence, temporality, experiencer, negation)


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

    print(m1)
    print(m2)
    print(m3)
    print(m4)
    print(m5)
    print(m6)
    print(m7)
    print(m8)
    print(m9)
    print(m10)
    print(m11)
