from claritynlp_logging import log, ERROR, DEBUG

try:
    from .base_model import BaseModel
except Exception as e:
    log(e)
    from base_model import BaseModel


class Measurement(BaseModel):

    def __init__(self, subject='', X='', Y='', Z='', units='', text='', start='', end='', location='', temporality='',
                 sentence='', condition='', value1='', value2='', x_view='', y_view='', z_view='', matching_terms='', min_value='', max_value=''):
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
        self.condition = condition
        self.value1 = value1
        self.value2 = value2
        self.x_view = x_view
        self.y_view = y_view
        self.z_view = z_view
        self.matching_terms = matching_terms
        self.min_value = min_value
        self.max_value = max_value


class MeasurementResults(BaseModel):

    def __init__(self, measurements):
        self.measurements = measurements
