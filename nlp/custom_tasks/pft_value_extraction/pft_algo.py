import re
import json
import sys
from algorithms import value_extractor as ve


def get_fev1fvc(sentence):
    fev1fvc_list = []
    # Running a loop on the range in which fev1/fvc value could be found.
    # Includes ratios both exprecessed as percent and decimal, > 100% is for predicted values
    for x,y in [(0,2),(10,180)]:
        fev1_fvc = ve.run("fev1/fvc", sentence, x, y)

        if json.loads(fev1_fvc)['querySuccess']:
            for i in range(json.loads(fev1_fvc)['measurementCount']):
                fev1fvc_dict = {}
                fev1fvc_dict['type'] = "fev1_fvc_ratio"
                fev1fvc_dict['text'] = json.loads(fev1_fvc)['measurementList'][i]['text']
                fev1fvc_dict['condition'] = json.loads(fev1_fvc)['measurementList'][i]['condition']
                fev1fvc_dict['x'] = json.loads(fev1_fvc)['measurementList'][i]['x']
                fev1fvc_dict['y'] = json.loads(fev1_fvc)['measurementList'][i]['y']

                clean_text = json.loads(fev1_fvc)['measurementList'][i]['text'].replace(')','').replace('(','')
                sentence = sentence.replace(')','').replace('(','')

                fev1_fvc_units = re.findall(clean_text+r'\s?(%)?',sentence)[0]
                if fev1_fvc_units == '%':
                    fev1_fvc_units = re.findall(clean_text+r'\s?(% ?pred|% ?of ?pred| ?%)',sentence)[0]
                if fev1_fvc_units == '':
                    fev1_fvc_units = ve.EMPTY_FIELD
                fev1fvc_dict['units'] = fev1_fvc_units
                fev1fvc_list.append(fev1fvc_dict)
        else:
            None
    return fev1fvc_list


def get_fvc(sentence):
    fvc_list = []
    # Includes values in ml,l and % predicted
    for x,y in [(300,6000),(15,170),(0.3,6)]:
        fvc = ve.run("fvc", sentence, x, y)

        if json.loads(fvc)['querySuccess']:
            for i in range(json.loads(fvc)['measurementCount']):
                fvc_dict = {}
                fvc_dict['type'] = "fvc"
                fvc_dict['text'] = json.loads(fvc)['measurementList'][i]['text']
                fvc_dict['condition'] = json.loads(fvc)['measurementList'][i]['condition']
                fvc_dict['x'] = json.loads(fvc)['measurementList'][i]['x']
                fvc_dict['y'] = json.loads(fvc)['measurementList'][i]['y']

                clean_text = json.loads(fvc)['measurementList'][i]['text'].replace(')','').replace('(','')
                sentence = sentence.replace(')','').replace('(','')

                fvc_units = re.findall( clean_text +r'\s?(ml|cc|l|L|ML|CC|%)?',sentence)[0]
                if fvc_units == '%':
                    fvc_units = re.findall( clean_text +r'\s?(% ?predicted|% ?of ?predicted|% ?pred|% ?of ?pred| ?%)',sentence)[0]
                if fvc_units == '':
                    fvc_units = ve.EMPTY_FIELD
                fvc_dict['units'] = fvc_units
                fvc_list.append(fvc_dict)
        else:
            None
    return fvc_list

def get_fev1(sentence):
    fev1_list = []
    # Includes values in ml, l and % predicted
    for x,y in [(0,6),(20,190),(300,6000)]:
        fev1 = ve.run("fev1", sentence, x, y)

        if json.loads(fev1)['querySuccess']:
            for i in range(json.loads(fev1)['measurementCount']):
                fev1_dict = {}
                fev1_dict['type'] = "fev1"
                fev1_dict['text'] = json.loads(fev1)['measurementList'][i]['text']
                fev1_dict['condition'] = json.loads(fev1)['measurementList'][i]['condition']
                fev1_dict['x'] = json.loads(fev1)['measurementList'][i]['x']
                fev1_dict['y'] = json.loads(fev1)['measurementList'][i]['y']

                clean_text = json.loads(fev1)['measurementList'][i]['text'].replace(')','').replace('(','')
                sentence = sentence.replace(')','').replace('(','')

                fev1_units = re.findall( clean_text +r'\s?(ml|cc|l|L|ML|CC|%)?',sentence)[0]
                if fev1_units == '%':
                    fev1_units = re.findall( clean_text +r'\s?(% ?predicted|% ?of ?predicted|% ?pred|% ?of ?pred| ?%)',sentence)[0]
                if fev1_units == '':
                    fev1_units = ve.EMPTY_FIELD
                fev1_dict['units'] = fev1_units
                fev1_list.append(fev1_dict)
        else:
            None
    return fev1_list

def pft_extractor(x):

    pft_dict = {}
    pft_dict['sentence'] = x
    pft_dict['results'] = []
    pft_dict['fev1_fvc_ratio_count'] = len(get_fev1fvc(x))
    pft_dict['results'].append(get_fev1fvc(x))

    x = x.lower()
    x = x.replace('fev1/fvc', '$')

    pft_dict['fvc_count'] = len(get_fvc(x))
    pft_dict['fev1_count'] = len(get_fev1(x))

    pft_dict['results'].append(get_fvc(x))
    pft_dict['results'].append(get_fev1(x))
    return json.dumps(pft_dict)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(pft_extractor(sys.argv[1]))

    else:
        raise SystemExit("No pft values could be found in <name>")
