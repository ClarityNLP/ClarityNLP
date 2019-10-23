try:
    from .pft_algo import pft_extractor as pftex
except Exception as e:
    from pft_algo import pft_extractor as pftex

from collections import namedtuple
import json
from algorithms import value_extraction as ve
from claritynlp_logging import log, ERROR, DEBUG



test_sentences = [
"fev1 is 95% for the patient, FEv1/fvc is 50% of pred, fev1/fvc is 110%, fvc is 1.2 liters, fvc is 110% of predicted, fvc is 600ml and fvc is 700"
,'tests, spirometry) revealed FVC actual 1.36, predicted 2.99, percent predicted 45; FEV1 actual 0.85, predicted 2.26, percent predicted 38; MMF actual 0.37, predicted 2.73, percent predicted 14; FEV1/FVC actual 62, predicted 76, percent predicted 83.'
,'improved to 7.32, 72, 77.  PFTs from [**3420-10-16**]:  FEV1/FVC ratio 19% of predicted.  Sodium 137, potassium 5.4, chloride 96, bicarbonate 34 approximately at baseline, BUN 33,'
,'respiratory weakness with resultant restrictive lung disease who is transferred from OSH for respiratory failure. The pt has been followed by Dr. [**First Name8 (NamePattern2) **] [**Last Name (NamePattern1) **] of the Pulmonary division at [**Hospital1 18**] for the past year. PFTs taken on [**2602-10-8**], demonstrated an FEV1/FVC of 89 (114%), FEV1 of 1.19L(48%) and FVC of 1.34L'
,'TLC 2.42 (53%), DLCo 74%. [**3282-6-1**]: FVC 0.83(22%), FEV1 0.66(22%), FEV1/FVC (78), TLC'
,'s/p [**Month/Year (2) **] in [**2529-1-4**] for high grade heart block and bradycardia, generator change [**2536-10-3**] Asthma, PFTs [**5-/2522**] showed FVC 1.75 (69% pred), FEV1 0.93 (52%'
,'PFTs [**3100-4-23**]: FVC 40%, FEV1 152%, MMF 79%, FEV1/FVC 121% (FVC'
,'on weight loss but remainder of w/u done).  In pulmonary rehab here, and at home is on 2L O2 continuous with 4L O2 for exertion.  Most recent PFTs [**2-11**]: FEV1 1.58 (51%), FVC 1.84 (44%), FEV1/FVC 86%, TLC 2.61 (43% in [**12-11**]), DLCO 8.6 (32% in'
]

for sentence in test_sentences:
    json_data = json.loads(pftex(sentence))
    VALUE_RESULT_FIELDS = ['sentence', 'fev1_count', 'fev1_fvc_ratio_count', 'fvc_count', 'results']
    ValueResult = namedtuple('ValueResult', VALUE_RESULT_FIELDS)
    result = ValueResult(**json_data)


    log('sentence: {0}'.format(result.sentence))
    log()
    log('fev1_count: {0}'.format(result.fev1_count))
    log('fev1_fvc_ratio_count: {0}'.format(result.fev1_fvc_ratio_count))
    log('fvc_count: {0}'.format(result.fvc_count))

    pft_object = 1
    for x in result.results:
        index = 1
        if x != []:
            for v in x:

                log('         type[{0}.{1}]: {2}'.format(pft_object, index, v['type']))
                log('         text[{0}.{1}]: {2}'.format(pft_object,index , v['text']))
                log('    condition[{0}.{1}]: {2}'.format(pft_object,index , v['condition']))
                log('            x[{0}.{1}]: {2}'.format(pft_object,index , v['x']))
                if ve.EMPTY_FIELD != v['y']:
                    log('            y[{0}.{1}]: {2}'.format(pft_object,index , v['y']))
                if ve.EMPTY_FIELD != v['units']:
                    log('        units[{0}.{1}]: {2}'.format(pft_object,index , v['units']))
                else:
                    log('        units[{0}.{1}]: ABSENT'.format(pft_object,index))
                index = index + 1
                log()
        pft_object +=1
        log()
