Measurement-Subject Resolution
******************************

Overview
========

Measurement-subject resolution is the process of associating size measurements
in a sentence with the object(s) possessing those measurements. For instance,
in the sentence

    ``The spleen measures 7.5 cm.``

the measurement ``7.5 cm`` is associated with ``spleen``. The term
``spleen`` is said to be the *subject* of the measurement ``7.5 cm``. In this
example the subject of the measurement also happens to be the subject of the
sentence. This is not always the case, as the next sentence illustrates:

    ``The liver is normal in architecture and echogenicity, and is``
    ``seen to contain numerous small cysts ranging in size from a few``
    ``millimeters to approximately 1.2 cm in diameter.``

Here the subject of the sentence is ``liver``, but the subject of the
``1.2 cm`` measurement is ``cysts``.

In this document we describe how Clarity analyzes sentences and attempts to
resolve subjects and measurements.

Source Code
===========

The source code for the measurement subject finder is located in
``nlp/finder/subject_finder.py``.

Inputs
------

The entry point to the subject finder is the ``run`` function:

.. code-block:: python
    :linenos:

    def run(term_string,        # string, comma-separated list of query terms
            sentence,           # string, the sentence to be processed
            nosub=False,        # set to True to disable ngram substitutions
            use_displacy=False) # set to True to display a dependency parse

The ``term_string`` argument is a comma-separated list of query terms. The
``nosub`` argument can be used to disable ngram substitution, described below.
The ``use_displacy`` argument generates an html page displaying a dependency
parse of the sentence. This visualization capability should only be used for
debugging and development.

Outputs
-------

A JSON array containing these fields for each size measurement found:

================  ==============================================================
Field Name        Explanation
================  ==============================================================
sentence          the sentence from which size measurements  were extracted
terms             comma-separated list of query terms
querySuccess      "true" if at least one query term matched a measurement subject
measurementCount  the number of size measurements found
measurements      array of individual size measurements
================  ==============================================================

Each result in the measurements array contains these fields:

================  ==============================================================
Field Name        Explanation
================  ==============================================================
text              text of the complete size measurement
start             offset of the first character in the matching text
end               offset of the final character in the matching text plus 1
temporality       indicartion of when measurement occurred
                  values are 'CURRENT' and 'PREVIOUS'
units             units of the x, y, and z fields
                  values are 'MILLIMETERS', 'SQUARE_MILLIMETERS', and
                  'CUBIC_MILLIMETERS'
condition         numeric ranges will have this field set to 'RANGE'
                  all other measurements will set this field to 'EQUAL'
matchingTerm      an array of all matching query terms for this measurement
subject           an array of strings, the possible measurement subjects
location          a string representing the anatomic location of the object
x                 numeric value of first measurement dimension
y                 numeric value of second measurement dimension
z                 numeric value of third measurement dimension
values            JSON array of all numeric values in a size list
xView             view specification for x value
yView             view specification for y value
zView             view specification for z value
minValue          minimum value of x, y, and z
maxValue          maximum value of x, y, and z
================  ==============================================================

All JSON results will have an identical number of fields. Any fields that are
not valid for a given measurement will have a value of EMPTY_FIELD and should be
ignored.

Dependencies
------------

The measurement subject finder has a dependency on Clarity's size measurement
finder module, documentation for which can be found here:
:ref:`size-measurement-finder`.

.. _spaCy: https://spacy.io/
     
There is also a dependency on `spaCy`_, a python library for natural language
processing. The Clarity subject finder module uses spaCy to generate a
*dependency parse* of each sentence that it processes. A dependency parse
provides part-of-speech information for each word in a sentence, as well as
relationship information encoded in tree form. To illustrate, here is a diagram
of a dependency parse of the sentence...



