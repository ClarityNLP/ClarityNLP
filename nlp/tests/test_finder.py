from algorithms.finder import test_finder as tf
from algorithms.finder import test_lab_value_matcher

def test_time_finder():
    assert tf.test_time_finder()

def test_date_finder():
    assert tf.test_date_finder()

def test_size_measurement_finder():
    assert tf.test_size_measurement_finder()

def test_o2sat_finder():
    assert tf.test_o2sat_finder()

def test_lvm():
    assert test_lab_value_matcher.run()



