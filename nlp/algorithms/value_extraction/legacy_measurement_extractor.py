import json
import os
import random
import string
from itertools import product
from subprocess import Popen, PIPE, STDOUT
from data_access import Measurement
from algorithms.segmentation import *
from claritynlp_logging import log, ERROR, DEBUG

log('Initializing models for measurement finder...')
segmentor = Segmentation()
log('Done initializing models for measurement finder...')

SCRIPT_DIR = os.path.dirname(__file__)
JAR = "jars/QueryValueExtractor.jar"
MODEL_DIR = "jars/models"


MODEL_FULL_DIR = os.path.join(SCRIPT_DIR, MODEL_DIR)
FULL_JAR = os.path.join(SCRIPT_DIR, JAR)


def run_measurement_finder(filename):

    measurements = list()
    try:
        p = Popen(['java', '-jar', FULL_JAR, '-f', filename, '-m', MODEL_FULL_DIR], stdout=PIPE, stderr=STDOUT)
        json_str = ''
        for line in p.stdout:
            json_str += str(line, 'utf-8')

        json_obj = json.loads(json_str)
        results = json_obj['results']
        for res in results:
            meas_count = int(res["measurementCount"])
            if meas_count > 0:
                # print("found %d measurements" % meas_count)
                meas_results = res['measurements']
                for meas in meas_results:
                    meas_obj = Measurement.from_dict(meas)
                    meas_obj.__setattr__('sentence', res['sentence'])
                    measurements.append(meas_obj)
    except Exception as e:
        log(e, ERROR)

    return measurements


def run_legacy_measurement_finder_full(text, query: list()):
    sentences = segmentor.parse_sentences(text)
    rand_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(1, 10)))
    filename = "/tmp/%s.txt" % rand_name
    matchers = [re.compile(r"\b%s\b" % t, re.IGNORECASE) for t in query]
    vals = product(sentences, matchers)
    with open(filename, "w") as fileout:
        for v in vals:
            sentence = v[0]
            matcher = v[1]
            match = matcher.search(sentence)
            if match:
                term = match.group(0)
                # print("Value Extraction QUERY: %s\n %s" % (term, sentence.replace('\n', ' ')))
                fileout.write("QUERY: %s\n" % term)
                fileout.write(sentence.replace('\n', ' '))
                fileout.write("\n\n")

    measurements = run_measurement_finder(filename)
    os.remove(filename)

    return measurements


if __name__ == '__main__':
    res = run_legacy_measurement_finder_full("COMPLETE GU U.S. (BLADDER & RENAL) \n Reason: r/o stones, tumor hydro, need PVR prostate size\n\n UNDERLYING MEDICAL CONDITION:\n  hx TURP and bladder ca\n REASON FOR THIS EXAMINATION:\n  r/o stones, tumor hydro, need PVR prostate size\n  FINAL REPORT\n COMPLETE GU ULTRASOUND\n\n INDICATION:  History of bladder cancer and TURB.  Rule out stones, tumor\n burden, need PVR and prostate size.\n\n COMPLETE GU ULTRASOUND:  Comparison is made to prior CT examination date.  The right kidney measures 12.3 cm.  The left kidney measures 9.9 cm.\n There is no hydronephrosis or stones.  Multiple cysts are seen bilaterally.\n These appear simple.  The largest cyst is seen in the lower pole of the left\n kidney and measures 3.0 x 1.8 x 2.4 cm.  The bladder is partially filled.  The\n prostate gland measures 3.8 x 2.9 x 3.0 cm resulting in a volume of 17 cc and\n a predicted PSA of 2.1.  Upon voiding, there was no post-void residual.\n\n IMPRESSION:  Multiple bilateral renal cysts.  Otherwise, normal examination.", ['tumor', 'cyst'])
    json_string = json.dumps([r.__dict__ for r in res], indent=4)
    log(json_string)
