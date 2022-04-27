from algorithms.value_extraction_wrappers.tnm_wrapper import run_tnm_stager_full

SENTENCES = [
    "pT3pN1M1 colon cancer with resection for cure of "
    "both the primary tumor and a liver metastasis; R0 (colon); R0 (liver)."
    " The tumor is classified as pT4bpN1bM0 (stage IIIC)."
]

EXPECTED =  [
    [
        {
            'text':'pT3pN1M1 c',
            'start':0,
            'end':10,
            't_prefix':'p',
            't_code':'3',
            't_certainty':None,
            't_suffixes':None,
            't_mult':None,
            'n_prefix':'p',
            'n_code':'1',
            'n_certainty':None,
            'n_suffixes':None,
            'n_regional_nodes_examined':None,
            'n_regional_nodes_involved':None,
            'm_prefix':None,
            'm_code':'1',
            'm_certainty':None,
            'm_suffixes':['c'],
            'l_code':None,
            'g_code':None,
            'v_code':None,
            'pn_code':None,
            'serum_code':None,
            'r_codes':None,
            'r_suffixes':None,
            'r_locations':None,
            'stage_prefix':None,
            'stage_number':None,
            'stage_letter':None,
            'sentence':'pT3pN1M1 colon cancer with resection for cure of both the primary tumor and a liver metastasis; R0 (colon); R0 (liver).',
        },
        {
            'text':'pT4bpN1bM0 (stage IIIC)',
            'start':27,
            'end':50,
            't_prefix':'p',
            't_code':'4',
            't_certainty':None,
            't_suffixes':['b'],
            't_mult':None,
            'n_prefix':'p',
            'n_code':'1',
            'n_certainty':None,
            'n_suffixes':['b'],
            'n_regional_nodes_examined':None,
            'n_regional_nodes_involved':None,
            'm_prefix':None,
            'm_code':'0',
            'm_certainty':None,
            'm_suffixes':None,
            'l_code':None,
            'g_code':None,
            'v_code':None,
            'pn_code':None,
            'serum_code':None,
            'r_codes':None,
            'r_suffixes':None,
            'r_locations':None,
            'stage_prefix':None,
            'stage_number':'3',
            'stage_letter':'c',
            'sentence':'The tumor is classified as pT4bpN1bM0 (stage IIIC).',
        }
    ]
]

'''
with open('tmp.txt', 'w') as file:
    result = [run_tnm_stager_full(x) for x in SENTENCES]
    for res in result:
        for r in res:
            file.write('{\n')
            for k, v in r.items():
                if isinstance(v, str):
                    file.write(f'\t\'{k}\':\'{v}\',\n')
                else:
                    file.write(f'\t\'{k}\':{str(v)},\n')
            file.write('},\n')
'''

def test_tnm():
    assert EXPECTED == [run_tnm_stager_full(x) for x in SENTENCES]