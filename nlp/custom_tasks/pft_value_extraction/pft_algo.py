import re
import json
import sys
from algorithms import value_extractor as ve
from claritynlp_logging import log, ERROR, DEBUG


fev_matcher = re.compile(r"\bfev\b", re.IGNORECASE)
fvc_matcher = re.compile(r"\bfvc\b", re.IGNORECASE)

def get_fev1fvc(sentence):
    fev1fvc_list = []
    # Running a loop on the range in which fev1/fvc value could be found.
    # Includes ratios both exprecessed as percent and decimal, > 100% is for predicted values
    for x,y in [(0,2),(10,180)]:
        fev1_fvc = ve.run("fev1/fvc", sentence, x, y)
        fev1_fvc_json = json.loads(fev1_fvc)
        if fev1_fvc_json['querySuccess']:
            for i in range(fev1_fvc_json['measurementCount']):
                fev1fvc_dict = dict()
                fev1fvc_dict['type'] = "fev1_fvc_ratio"
                fev1fvc_dict['text'] = fev1_fvc_json['measurementList'][i]['text']
                fev1fvc_dict['condition'] = fev1_fvc_json['measurementList'][i]['condition']
                fev1fvc_dict['start'] = fev1_fvc_json['measurementList'][i]['start']
                fev1fvc_dict['end'] = fev1_fvc_json['measurementList'][i]['end']
                fev1fvc_dict['x'] = fev1_fvc_json['measurementList'][i]['x']
                fev1fvc_dict['y'] = fev1_fvc_json['measurementList'][i]['y']

                clean_text = fev1_fvc_json['measurementList'][i]['text'].replace(')','').replace('(','')
                sentence = sentence.replace(')','').replace('(','')

                fev1_fvc_units = re.findall(clean_text+r'\s?(%)?',sentence)[0]
                if fev1_fvc_units == '%':
                    fev1_fvc_units = re.findall(clean_text+r'\s?(% ?pred|% ?of ?pred| ?%)',sentence)[0]
                if fev1_fvc_units == '':
                    fev1_fvc_units = ve.EMPTY_FIELD
                fev1fvc_dict['units'] = fev1_fvc_units
                fev1fvc_list.append(fev1fvc_dict)
        else:
            pass
    return fev1fvc_list


def get_fvc(sentence):
    fvc_list = []
    # Includes values in ml,l and % predicted
    for x,y in [(300,6000),(15,170),(0.3,6)]:
        fvc = ve.run("fvc", sentence, x, y)
        fvc_json = json.loads(fvc)
        if fvc_json['querySuccess']:
            for i in range(fvc_json['measurementCount']):
                fvc_dict = dict()
                fvc_dict['type'] = "fvc"
                fvc_dict['text'] = fvc_json['measurementList'][i]['text']
                fvc_dict['condition'] = fvc_json['measurementList'][i]['condition']
                fvc_dict['x'] = fvc_json['measurementList'][i]['x']
                fvc_dict['y'] = fvc_json['measurementList'][i]['y']
                fvc_dict['start'] = fvc_json['measurementList'][i]['start']
                fvc_dict['end'] = fvc_json['measurementList'][i]['end']

                clean_text = fvc_json['measurementList'][i]['text'].replace(')','').replace('(','')
                sentence = sentence.replace(')','').replace('(','')

                fvc_units = re.findall( clean_text +r'\s?(ml|cc|l|L|ML|CC|%)?',sentence)[0]
                if fvc_units == '%':
                    fvc_units = re.findall( clean_text +r'\s?(% ?predicted|% ?of ?predicted|% ?pred|% ?of ?pred| ?%)',sentence)[0]
                if fvc_units == '':
                    fvc_units = ve.EMPTY_FIELD
                fvc_dict['units'] = fvc_units
                fvc_list.append(fvc_dict)
    return fvc_list


def get_fev1(sentence):
    fev1_list = []
    # Includes values in ml, l and % predicted
    for x,y in [(0,6),(20,190),(300,6000)]:
        fev1 = ve.run("fev1", sentence, x, y)
        fev1_json = json.loads(fev1)
        if fev1_json['querySuccess']:
            for i in range(fev1_json['measurementCount']):
                fev1_dict = dict()
                fev1_dict['type'] = "fev1"
                fev1_dict['text'] = fev1_json['measurementList'][i]['text']
                fev1_dict['condition'] = fev1_json['measurementList'][i]['condition']
                fev1_dict['x'] = fev1_json['measurementList'][i]['x']
                fev1_dict['y'] = fev1_json['measurementList'][i]['y']
                fev1_dict['start'] = fev1_json['measurementList'][i]['start']
                fev1_dict['end'] = fev1_json['measurementList'][i]['end']

                clean_text = fev1_json['measurementList'][i]['text'].replace(')','').replace('(','')
                sentence = sentence.replace(')','').replace('(','')

                fev1_units = re.findall( clean_text +r'\s?(ml|cc|l|L|ML|CC|%)?',sentence)[0]
                if fev1_units == '%':
                    fev1_units = re.findall( clean_text +r'\s?(% ?predicted|% ?of ?predicted|% ?pred|% ?of ?pred| ?%)',sentence)[0]
                if fev1_units == '':
                    fev1_units = ve.EMPTY_FIELD
                fev1_dict['units'] = fev1_units
                fev1_list.append(fev1_dict)
    return fev1_list


def pft_extractor(x):
    pft_dict = dict()
    pft_dict['results'] = list()
    pft_dict['start'] = 0
    pft_dict['end'] = 0
    pft_dict['sentence'] = x
    pft_dict['fev1_condition'] = ''
    pft_dict['fev1_units'] = ''
    pft_dict['fev1_value'] = 0.0
    pft_dict['fev1_text'] = ''
    pft_dict['fev1_count'] = 0
    pft_dict['fev1_fvc_ratio_count'] = 0
    pft_dict['fev1_fvc_condition'] = ''
    pft_dict['fev1_fvc_units'] = ''
    pft_dict['fev1_fvc_value'] = 0.0
    pft_dict['fev1_fvc_text'] = ''
    pft_dict['fvc_count'] = 0
    pft_dict['fvc_condition'] = ''
    pft_dict['fvc_units'] = ''
    pft_dict['fvc_value'] = 0.0
    pft_dict['fvc_text'] = ''


    starts = list()
    ends = list()

    fev_match = fev_matcher.search(x)
    fvc_match = fvc_matcher.search(x)

    if fev_match or fvc_match:
        fev1fvc = get_fev1fvc(x)
        if fev1fvc:
            len_fev1_fvc = len(fev1fvc)
            if len_fev1_fvc > 0:
                pft_dict['results'].append(fev1fvc)
                pft_dict['fev1_fvc_ratio_count'] = len_fev1_fvc
                for f in fev1fvc:
                    starts.append(f['start'])
                    ends.append(f['end'])
                    pft_dict['fev1_fvc_condition'] = f['condition']
                    pft_dict['fev1_fvc_units'] = f['units']
                    pft_dict['fev1_fvc_value'] = f['x']
                    pft_dict['fev1_fvc_text'] = f['text']

    x = x.lower()
    x = x.replace('fev1/fvc', '$')

    if fvc_match:
        fvc = get_fvc(x)
        if fvc:
            len_fvc = len(fvc)
            if len_fvc > 0:
                pft_dict['results'].append(fvc)
                pft_dict['fvc_count'] = len_fvc
                for f in fvc:
                    starts.append(f['start'])
                    ends.append(f['end'])
                    pft_dict['fvc_condition'] = f['condition']
                    pft_dict['fvc_units'] = f['units']
                    pft_dict['fvc_value'] = f['x']
                    pft_dict['fvc_text'] = f['text']

    if fev_match:
        fev1 = get_fev1(x)
        if fev1:
            len_fev1 = len(fev1)
            if len_fev1 > 0:
                pft_dict['results'].append(fev1)
                pft_dict['fev1_count'] = len_fev1
                for f in fev1:
                    starts.append(f['start'])
                    ends.append(f['end'])
                    pft_dict['fev1_condition'] = f['condition']
                    pft_dict['fev1_units'] = f['units']
                    pft_dict['fev1_value'] = f['x']
                    pft_dict['fev1_text'] = f['x']

    if len(starts) > 0 and len(ends) > 0:
        pft_dict['start'] = min(starts)
        pft_dict['end'] = max(ends)


    return json.dumps(pft_dict)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        log(pft_extractor(sys.argv[1]))

    else:
        raise SystemExit("No pft values could be found in <name>")
