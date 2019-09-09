.. _measurementfinderalgo:

Finding Size Measurements
*************************

Overview
=========

Size measurements are common in electronic health records, especially in
radiology and other diagnostic reports.  By 'size measurement' we mean a 1D, 2D,
or 3D expression involving lengths, such as:

=====================================  =======================
Example                                Meaning
=====================================  =======================
3mm		                               1D measurement
1.2 cm x 3.6 cm                        2D measurement
3 by 4 by 5 cm                         3D measurement
1.5 cm2                                area measurement
4.3 mm3                                volume measurement
2.3 - 4.5 cm                           range of lengths
1.1, 2.3, 8.5, and 12.6 cm             list of lengths
1.5cm craniocaudal x 2.2cm transverse  measurement with views
=====================================  =======================

ClarityNLP scans sentences for size measurements, extracts the numeric values
for each dimension, normalizes each to a common set of units (performing unit
conversions if necessary), and provides output in JSON format to other pipeline
components.

Source Code
============

The source code for the size measurement finder module is located in
``nlp/algorithms/finder/size_measurement_finder.py``.


Inputs
------

A single string, the sentence to be scanned for size measurements.

Outputs
-------

A JSON array containing these fields for each size measurement found:

===========  ==============================================================
Field Name   Explanation
===========  ==============================================================
text         text of the complete measurement
start        offset of the first character in the matching text
end          offset of the final character in the matching text plus 1
temporality  CURRENT or PREVIOUS, indicating when the measurement occurred
units        either mm, mm2, or mm3
condition    either 'RANGE' for numeric ranges, or 'EQUAL' for all others
x            numeric value of first number
y            numeric value of second number
z            numeric value of third number
values       for lists, a JSON array of all values in the list
xView        view specification for the first axis
yView        view specification for the second axis
zView        view specification for the third axis
minValue     either ``min([x, y, z])`` or ``min(values)``
maxValue     either ``max([x, y, z])`` or ``max(values)``
===========  ==============================================================

All JSON measurement results contain an identical number of fields. Any fields
that are not valid for a given measurement will have a value of EMPTY_FIELD and
should be ignored.

All string operations of the size measurement finder are case-insensitive.


Algorithm
=========

ClarityNLP uses a set of regular expressions to recognize size measurements. It
scans a sentence with each regex, keeps track of any matches, and finds the
longest match among the matching set. The longest matching text string is then
tokenized, values are extracted, units are converted, and a python namedtuple
representing the measurement is generated. This process is repeated until no
more measurements are found, at which point the array of measurement
namedtuples is converted to JSON and returned to the caller.

Measurement Formats
-------------------

ClarityNLP is able to recognize size measurements in a number of different formats.
Using notation similar to that of [1]_, we define the following quantities:

=========  ===============================================================================
Shorthand  Meaning
=========  ===============================================================================
x y z      Any numeric value, either floating point or integer
cm         Units for the preceding numeric value
by         Either the word 'by' or the symbol 'x'
to         Either the word 'to' or the symbol '-'
vol        Dimensional modifier, either 'square', 'cubic', 'sq', 'sq.', 'cu', 'cu.', 'cc'
view       View specification, any word will match
=========  ===============================================================================

With these definitions, the measurement formats that ClarityNLP recognizes are:

===================================  ======================================================
Regex Form                           Examples
===================================  ======================================================
x cm                                 3 mm, 5cm, 10.2 inches
x vol cm                             5 square mm, 3.2cm2
x to y cm                            3-5 cm, 3 to 5cm
x cm to y cm                         3 cm to 5 cm, 3cm - 5 cm
x by y cm                            3 x 5 inches, 3x5 cm
x cm by y cm                         3 mm by 5 mm
x cm view by y cm view               3 cm craniocaudal x 5 cm transverse
x by y by z cm                       3 x 5 x 7 mm
x by y cm by z cm                    3 x 5mm x 7 mm
x cm by y cm by z cm                 3 mm x 5 mm x 7 mm
x cm view by y cm view by z cm view  3 cm craniocaudal by 5cm transverse by 7 cm anterior
===================================  ======================================================

ClarityNLP can also find size measurements with nonuniform spacing between the
various components, as several of the examples above demonstrate. Newlines can
also be present within a measurement. Inconsistent spacing such as this
appears frequently in electronic health records.

Details
-------

These medically-relevant measurement units are supported:

============= =============================
Units         Textual Forms
============= =============================
millimeters    mm, millimeter, millimeters
centimeters    cm, centimeter, centimeters
inches         in, inch, inches
============= =============================

ClarityNLP tries to distinguish uses of the word 'in' as a preposition vs.
its use as a unit of length. **It cannot correctly identify all such instances.**
Hence the word 'in' preceded by a numeric value may sometimes generate false
positive results.

Numeric values can be integers (sequence of digits) or floating point values.
The digit before the decimal point is optional. Some examples:

* 3, 42
* 12.4887
* .314, 0.314



References
==========

.. [1] | M. Sevenster, J. Buurman, P. Liu, J.F. Peters, P.J. Chang
       | **Natural Language Processing Techniques for Extracting and Categorizing**
       | **Finding Measurements in Narrative Radiology Reports**
       | *Appl. Clin. Inform.*, 6(3) 600-610, 2015.
