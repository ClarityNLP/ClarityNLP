from nlp.segmentation import *

import json
try:
    from .tnm_stager import run as run_tnm_stager, TNM_FIELDS, TnmCode, EMPTY_FIELD as EMPTY_TNM_FIELD
except Exception as ex:
    print(ex)
    from tnm_stager import run as run_tnm_stager, TNM_FIELDS, TnmCode, EMPTY_FIELD as EMPTY_TNM_FIELD

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
