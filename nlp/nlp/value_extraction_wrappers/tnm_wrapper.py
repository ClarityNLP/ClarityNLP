from nlp.segmentation import *

import json
from nlp.value_extraction.tnm_stage_extractor import run as run_tnm_stager

segmentor = Segmentation()


def run_tnm_stager_full(text):
    res = []
    sentences = segmentor.parse_sentences(text)
    for s in sentences:
        json_string = run_tnm_stager(s)
        json_data = json.loads(json_string)
        for j in json_data:
            j['sentence'] = s
            res.append(j)
    return res
