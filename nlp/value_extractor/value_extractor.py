from subprocess import Popen, PIPE, STDOUT
import os
import json
from data_access import BaseModel


SCRIPT_DIR = os.path.dirname(__file__)
JAR = "jars/QueryValueExtractor.jar"
MODEL_DIR = "jars/models"


MODEL_FULL_DIR = os.path.join(SCRIPT_DIR, MODEL_DIR)
FULL_JAR = os.path.join(SCRIPT_DIR, JAR)


class Measurement(BaseModel):

    def __init__(self, subject='', X='', Y='', Z='', units='', text='', start='', end='', location='', temporality='', sentence=''):
        self.subject = subject
        self.X = X
        self.Y = Y
        self.Z = Z
        self.units = units
        self.text = text
        self.start = start
        self.end = end
        self.location = location
        self.temporality = temporality
        self.sentence = sentence


class MeasurementResults(BaseModel):

    def __init__(self, measurements):
        self.measurements = measurements


def run_value_extractor(sentence, query):

    measurements = list()
    try:
        p = Popen(['java', '-jar', FULL_JAR, '-s', sentence, '-q', query, '-m', MODEL_FULL_DIR], stdout=PIPE, stderr=STDOUT)
        json_str = ''
        for line in p.stdout:
            json_str += (str(line, 'utf-8') + '\n')

        json_obj = json.loads(json_str)
        meas_list = json_obj['measurements']
        for meas in meas_list:
            meas_obj = Measurement.from_dict(meas)
            meas_obj.__setattr__('sentence', sentence)
            measurements.append(meas_obj)
    except Exception as e:
        print(e)

    return measurements


def run_value_extractor_on_sentences(sentences, query):
    measurements = list()

    for sentence in sentences:
        this_measurements = run_value_extractor(sentence, query)
        measurements.extend(this_measurements)

    return measurements


if __name__ == '__main__':
    res = run_value_extractor('the tumor measures 5 cm x 1 cm', "tumor")
    json_string = json.dumps([r.__dict__ for r in res], indent=4)
    print(json_string)
