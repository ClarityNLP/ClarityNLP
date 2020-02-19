import en_core_web_sm as english_model
from data_access import BaseModel
import time
from algorithms.segmentation import Segmentation
from claritynlp_logging import log, ERROR, DEBUG


segmentation = Segmentation()

data = {}
loading_status = 'none'
descriptions = {
    "PERSON": "People",
    "NORP": "Nationalities or religious or political groups",
    "FACILITY": "Buildings, airports, highways, bridges, etc.",
    "ORG": "Companies, agencies, institutions, etc.",
    "GPE": "Countries, cities, states.",
    "LOC": "Non-GPE locations, mountain ranges, bodies of water.",
    "PRODUCT": "Objects, vehicles, foods, etc.x",
    "EVENT" : "Named hurricanes, battles, wars, sports events, etc.",
    "WORK_OF_ART": "Titles of books, songs, etc.",
    "LAW": "Named documents made into laws.",
    "LANGUAGE": "Any named language.",
    "DATE": "Absolute or relative dates or periods.",
    "TIME": "Times smaller than a day.",
    "PERCENT": "Percentage.",
    "MONEY": "Monetary values.",
    "QUANTITY": "Measurements, as of weight or distance.",
    "ORDINAL": "Ordinal numbers",
    "CARDINAL": "Numerals that do not fall under another type."
}


def nlp_init(tries=0):
    if tries > 0:
        log('Retrying, try%d' % tries)

    global loading_status
    if loading_status == 'none' and 'nlp' not in data:
        try:
            log('NER init...')
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


class NamedEntity(BaseModel):

    def __init__(self, sentence, text, start, end, label):
        self.sentence = sentence
        self.text = text
        self.start = start
        self.end = end
        self.label = label
        if label in descriptions:
            self.description = descriptions[label]
        else:
            self.description = label


def get_standard_entities(text):
    spacy = nlp_init()
    sentences = segmentation.parse_sentences(text)
    results = []
    for s in sentences:
        s = s.strip()
        if len(s) > 0:
            doc = spacy(s)
            results.extend([NamedEntity(s, ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents])
    return results


if __name__ == "__main__":
    res = get_standard_entities("George Burdell sold my homework in Florida for $1")
    for r in res:
        log(r.to_json())
    exit(0)
