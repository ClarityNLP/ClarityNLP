General Value Extraction
************************

Overview
========

Value extraction is the process of scanning text for query terms and finding
numeric values associated with those terms. For example, consider the
sentence:

    ``The patient's heart rate was 60 beats per minute.``

It is clear that the value 60 is associated with "heart rate". A value
extractor using this sentence as input should therefore return 60 as the
result for the query "heart rate".

Values can occur either before or after the query terms, since both
variants are acceptable forms of English expression:

 |   ``A 98.6F temperature was measured during the exam.    (before)``
 |   ``A temperature of 98.6F was measured during the exam. (after)``

The value-follows-query form is dominant in the text of medical records.
To constrain the scope of the problem and to reduce the chances of error:

    **Clarity assumes that the value FOLLOWS the query terms.**

This assumption does **not** imply anything about the distance between the
query and the value. Sometimes the value immediately follows the query, as
in terse lists of vital signs:

    ``Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA``

Other times, in narrative text, one or more words fill the space between
query and value:

    ``The temperature measured for the patient at the exam was 98.6F.``

Clarity is able to understand these situations and correctly associate the
value 98.6 with "temperature".

Value Types
-----------

Clarity's value extractor can recognize several different value types:

=================================  ===========================
Value Type                         Example
=================================  ===========================
Nonnegative Integer                0, 3, 42
Nonnegative Floating Point         3.1415, .27, 0.27
Numeric Range                      2-5, 2.3 - 4.6, 2.3 to 4.6
Numeric Range with Matching Units  15 ml to 20 ml
Fraction                           120/80, 120 / 80, 120 /80
Fraction Range                     110/70 - 120/80
=================================  ===========================

Fractions can have arbitrary whitespace on either side of the forward
slash, as some of these examples illustrate. For floating point numbers,
the digit before the decimal point is optional.

Value Relationships
-------------------

Clarity can associate queries and values expressed in many different formats:

=================================  ============================================
Format                             Example
=================================  ============================================
No space                           T98.6
Whitespace                         T 98.6, T   98.6
Dash                               T-98.6, T -98.6
Equality                           T=98.6, T = 98.6, T= 98.6, T is 98.6
Approximations                     T ~ 98.6, T approx. 98.6, T is ~98.6
Greater Than or Less Than          T > 98.6, T <= 98.6, T .lt. 98.6, T gt 98.6
Narrative                          T was greater than 98.6
=================================  ============================================

In general, the amount of whitespace between query and value is arbitrary.

Result Filters
--------------

Clarity filters numerical results by user-specified min and max values.
Any results that fall outside of the interval ``[min, max]`` are discarded.
Any numeric value is accepted if these limits are not specified.

For fractions, the value extractor returns the numerator value by default.
The denominator can be returned instead by use of a runtime argumen.


Source Code
===========

The source code for the value extractor module is located in
``nlp/value_extraction/value_extractor.py``.

Inputs
------

The entry point to the value extractor is the ``run`` function:

.. code-block:: python
   :linenos:

   def run(term_string,              # comma-separated list of query terms
           sentence,                 # string, the sentence to be processed
           str_minval=None,          # minimum numeric value
           str_maxval=None,          # maximum numeric value
           is_case_sensitive=False,  # set to True to preserve case
           is_denom_only=False)      # set to True to return denoms

If the str_minval and str_maxval arguments are omitted, Clarity accepts any
numeric value that it finds for a given query. The other arguments are
self-explanatory.

Outputs
-------

A JSON array containing these fields for each value found:

================  ==============================================================
Field Name        Explanation
================  ==============================================================
sentence          the sentence from which values were extracted
terms             comma-separated list of query terms
querySuccess      "true" if a value was found, "false" if not
measurementCount  the number of values found
measurements      array of results
================  ==============================================================

Each result in the measurements array contains these fields:

================  ==============================================================
Field Name        Explanation
================  ==============================================================
text              matching text for this value
start             offset of the first character in the matching text
end               offset of the final character in the matching text plus 1
condition         a string containing the relation between query and value:
                  APPROX, LESS_THAN, LESS_THAN_OR_EQUAL, GREATER_THAN,
                  GREATER_THAN_OR_EQUAL, EQUAL, RANGE, FRACTION_RANGE
matchingTerm      the query term associated with this value
x                 matching value
y                 matching value (only for ranges)
minValue          minimum value of x and y
maxValue          maximum value of x and y
================  ==============================================================

All JSON results will have an identical number of fields. Any fields that are
not valid for a given result will have a value of EMPTY_FIELD and should be
ignored.



Algorithm
=========


