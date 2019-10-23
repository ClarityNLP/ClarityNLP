from algorithms.segmentation import *
from data_access import Measurement
from algorithms import run_subject_finder, subject_finder_init
import json
from claritynlp_logging import log, ERROR, DEBUG

log('Initializing models for measurement finder...')
segmentor = Segmentation()
subject_finder_init()
log('Done initializing models for measurement finder..')


def run_measurement_finder_full(text, term_list, is_case_sensitive_text=False):
    if not is_case_sensitive_text:
        term_list = [term.lower() for term in term_list]
        text = text.lower()

    term_count = len(term_list)
    terms = ",".join(term_list)
    results = []

    sentence_list = segmentor.parse_sentences(text)
    for s in sentence_list:
        json_str = run_subject_finder(terms, s)
        json_obj = json.loads(json_str)
        if 0 == json_obj['measurementCount']:
            continue
        if term_count > 0 and not json_obj['querySuccess']:
            # ignore if query term(s) not found
            continue
        if json_obj and 'measurementList' in json_obj:
            for x in json_obj['measurementList']:
                try:
                    m = Measurement(sentence=s,
                                    text=x['text'],
                                    start=x['start'],
                                    end=x['end'],
                                    temporality=x['temporality'],
                                    units=x['units'],
                                    condition=x['condition'],
                                    matching_terms=', '.join(x['matchingTerm']),
                                    subject=', '.join(x['subject']),
                                    location=x['location'],
                                    X=x['x'],
                                    Y=x['y'],
                                    Z=x['z'],
                                    x_view=x['xView'],
                                    y_view=x['yView'],
                                    z_view=x['zView'],
                                    value1=x['values'],
                                    min_value = x['minValue'],
                                    max_value = x['maxValue']
                    )
                    results.append(m)
                    
                except Exception as ex:
                    log('measurement_finder_wrapper exception: {0}'.format(ex), ERROR)
                    log(ERROR, ex)

    return results


if __name__ == '__main__':
    res = run_measurement_finder_full(
        'A necrotic periportal lymph node  measures 2.0 cm compared to 1.7 cm previously.',
        ["node"])

    [log(str(t.to_json())) for t in res]
