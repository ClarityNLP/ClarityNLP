import en_core_web_sm as english_model
from data_access import BaseModel
import time
from algorithms.segmentation import Segmentation
from claritynlp_logging import log, ERROR, DEBUG


segmentation = Segmentation()

data = {}
loading_status = 'none'
tags = {
    "CC": "Coordinating conjunction",
    "CD": "Cardinal number",
    "DT": "Determiner",
    "EX": "Existential there",
    "FW": "Foreign word",
    "IN": "Preposition or subordinating conjunction",
    "JJ": "Adjective",
    "JJR": "Adjective, comparative",
    "JJS": "Adjective, superlative",
    "LS": "List item marker",
    "MD": "Modal",
    "NN": "Noun, singular or mass",
    "NNS": "Noun, plural",
    "NNP": "Proper noun, singular",
    "NNPS": "Proper noun, plural",
    "PDT": "Predeterminer",
    "POS": "Possessive ending",
    "PRP": "Personal pronoun",
    "PRP$": "Possessive pronoun",
    "RB": "Adverb",
    "RBR": "Adverb, comparative",
    "RBS": "Adverb, superlative",
    "RP": "Particle",
    "SYM": "Symbol",
    "TO": "to",
    "UH": "Interjection",
    "VB": "Verb, base form",
    "VBD": "Verb, past tense",
    "VBG": "Verb, gerund or present participle",
    "VBN": "Verb, past participle",
    "VBP": "Verb, non-3rd person singular present",
    "VBZ": "Verb, 3rd person singular present",
    "WDT": "Wh-determiner",
    "WP": "Wh-pronoun",
    "WP$": "Possessive wh-pronoun",
    "WRB": "Wh-adverb"
}


def nlp_init(tries=0):
    if tries > 0:
        log('Retrying, try%d' % tries)

    global loading_status
    if loading_status == 'none' and 'nlp' not in data:
        try:
            log('POSTagger init...')
            loading_status = 'loading'
            data['nlp'] = english_model.load()
            loading_status = 'done'
        except Exception as exc:
            log(exc)
            loading_status = 'none'
    elif loading_status == 'loading' and tries < 30:
        time.sleep(10)
        if loading_status == 'loading':
            new_tries = tries + 1
            return nlp_init(tries=new_tries)

    return data['nlp']


class Tag(BaseModel):

    def __init__(self, sentence, text, lemma, pos, tag, dep, shape, is_alpha, is_stop):
        self.sentence = sentence
        self.text = text
        self.lemma = lemma
        self.pos = pos
        self.tag = tag
        self.dep = dep
        self.shape = shape
        self.is_alpha = is_alpha
        self.is_stop = is_stop
        if tag in tags:
            self.description = tags[tag]
        else:
            self.description = tag


def get_tags(text):
    spacy = nlp_init()
    sentences = segmentation.parse_sentences(text)
    results = []
    for s in sentences:
        s = s.strip()
        if len(s) > 0:
            doc = spacy(s)
            results.extend([Tag(s, token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                                token.shape_, token.is_alpha, token.is_stop) for token in doc])
    return results


if __name__ == "__main__":
    res = get_tags("George Burdell sold my homework in Florida for $1")
    for r in res:
        log(r.to_json())
    exit(0)
