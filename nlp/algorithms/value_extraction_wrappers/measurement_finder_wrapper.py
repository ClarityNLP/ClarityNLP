from algorithms.segmentation import *
from data_access import Measurement
from algorithms import run_subject_finder, subject_finder_init
import json

print('Initializing models for measurement finder...')
segmentor = Segmentation()
subject_finder_init()
print('Done initializing models for measurement finder..')


def run_measurement_finder_full(text, term_list, is_case_sensitive_text=False):
    if not is_case_sensitive_text:
        term_list = [term.lower() for term in term_list]
        text = text.lower()

    terms = ",".join(term_list)
    results = []

    sentence_list = segmentor.parse_sentences(text)
    for s in sentence_list:
        json_str = run_subject_finder(terms, s)
        json_obj = json.loads(json_str)
        if json_obj and 'measurementList' in json_obj:
            for x in json_obj['measurementList']:
                try:
                    results.append(Measurement(sentence=s, text=x['text'], location=x['location'],
                                               x_view=x['x_view'], start=x['start'], temporality=x['temporality'],
                                               y_view=x['y_view'], Z=x['z'], subject=', '.join(x['subject']),
                                               X=x['x'], end=x['end'], condition=x['condition'],
                                               matching_terms=', '.join(x['matchingTerm']),
                                               value1=x['values'], z_view=x['z_view'], units=x['units'], Y=x['y']
                                               ))
                except Exception as ex:
                    print(ex)

    return results


if __name__ == '__main__':
    res = run_measurement_finder_full(
        'A necrotic periportal lymph node  measures 2.0 cm compared to 1.7 cm previously.',
        ["node"])

    [print(str(t.to_json())) for t in res]
