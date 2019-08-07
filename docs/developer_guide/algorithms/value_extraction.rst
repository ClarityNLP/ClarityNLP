.. _general-value-extraction:

General Value Extraction
************************

Overview
========

*Value extraction* is the process of scanning text for query terms and finding
numeric values associated with those terms. For example, consider the
sentence:
::
   The patient's heart rate was 60 beats per minute.

It is clear that the value 60 is associated with ``heart rate``. A value
extractor using this sentence as input should therefore return 60 as the
result for the query ``heart rate``.

Values can occur either before or after the query terms, since both
variants are acceptable forms of English expression:
::
   A 98.6F temperature was measured during the exam.    (before)
   A temperature of 98.6F was measured during the exam. (after)

The *value-follows-query* form is dominant in the text of medical records.
To constrain the scope of the problem and to reduce the chances of error:

    **ClarityNLP assumes that the value FOLLOWS the query terms.**

This assumption does **not** imply anything about the distance between the
query and the value. Sometimes the value immediately follows the term, as
in terse lists of vital signs:
::
   Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA

Other times, in narrative text, one or more words fill the space between
query term and value:
::
   The temperature recorded for the patient at the exam was 98.6F.

ClarityNLP tries to understand these situations and correctly associate the
value 98.6 with "temperature".

Value Types
-----------

ClarityNLP's value extractor can recognize several different value types:

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

ClarityNLP can associate queries and values expressed in many different formats:

=================================  ==========================================================
Format                             Example
=================================  ==========================================================
No space                           ``T98.6``
Whitespace                         ``T 98.6``, ``T    98.6``
Dash                               ``T-98.6``, ``T- 98.6``
Colon                              ``T:98.6``, ``T  :98.6``
Equality                           ``T=98.6``, ``T = 98.6``, ``T  =98.6``, ``T is 98.6``
Approximations                     ``T ~ 98.6``, ``T approx. 98.6``, ``T is ~98.6``
Greater Than or Less Than          ``T > 98.6``, ``T<=98.6``, ``T .lt. 98.6``, ``T gt 98.6``
Narrative                          ``T was greater than 98.6``
=================================  ==========================================================

In general, the amount of whitespace between query and value is arbitrary.

Result Filters
--------------

ClarityNLP filters numerical results by user-specified min and max values.
Any results that fall outside of the interval ``[min, max]`` are discarded.
Any numeric value is accepted if these limits are omitted.

For fractions, the value extractor returns the numerator value by default.
The denominator can be returned instead by use of the ``is_denom_only``
argument (see below).

Hypotheticals
-------------

The value extractor attempts to identify hypothetical phrases and to ignore any
values found therein. It uses a simplified version of the *ConText* algorithm
of [1]_ to recognize hypothetical phrases. The "trigger" terms that denote
the start of a hypothetical phrase are: ``in case``, ``call for``, ``should``,
``will consider``, and ``if`` when not preceded by ``know`` and not followed
by ``negative``.


Source Code
===========

The source code for the value extractor module is located in
``nlp/algorithms/value_extraction/value_extractor.py``.

Inputs
------

The entry point to the value extractor is the ``run`` function:

.. code-block:: python
   :linenos:

   def run(term_string,              # string, comma-separated list of query terms
           sentence,                 # string, the sentence to be processed
           str_minval=None,          # minimum numeric value
           str_maxval=None,          # maximum numeric value
           is_case_sensitive=False,  # set to True to preserve case
           is_denom_only=False)      # set to True to return denoms

If the ``str_minval`` and ``str_maxval`` arguments are omitted, ClarityNLP accepts
any numeric value that it finds for a given query. The other arguments should be
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
text              matching text containing query and value
start             offset of the first character in the matching text
end               offset of the final character in the matching text plus 1
condition         a string expressing the relation between query and value:
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

The value extractor does its work in four stages. The first stage consists of
preprocessing operations; the second stage consists of extracting candidate
values; the third stage consists of overlap resolution to choose a winner
from among the candidates; and the fourth stage consists of the removal of
hypotheticals. All results that remain are converted to JSON format and
returned to the caller.

Preprocessing
-------------

In the preprocessing stage, a few nonessential characters (such as parentheses
and brackets) are removed from the sentence. Removal of these characters helps
to simplify the regular expressions at the core of the value extractor.
Conversion to lowercase follows for the default case-insensitive mode of
operation. Identical preprocessing operations are applied to the list of
query terms.

The sentence is then scanned for
:ref:`date expressions<datefinderalgo>`,
:ref:`size measurements<measurementfinderalgo>`, and
:ref:`time expressions<timefinderalgo>`. The value extractor erases any
that it finds, subject to these restrictions:

1. Date expressions are not erased if they consist entirely of simple digits.
   For instance, the date finder will identify the string "1995" as the year
   1995, but "1995" could potentially be a volume measurement or another
   value in a different context.

2. All size measurements are erased unless the units are cubic centimeters
   or inches. Measurements in inches are kept since "in" as an abbreviation
   for "inches" can be easily confused with "in" as a preposition. ClarityNLP
   makes an attempt at disambiguation, but at present it does not have a
   technique that works reliably in all instances. Part of speech tagging is
   generally not helpful either. Tagging algorithms trained on formal
   Engish text (such as journalism or Wikipedia articles) exhibit lackluster
   performance on medical text, in our experience.

3. Time measurements require additional processing. Any time measurements
   that consist entirely of integers on both sides of a ``-`` sign are not
   erased, since these are likely to be numeric ranges instead of time
   expressions.
   
   ISO time formats such as ``hh, hhmm, hhmmss`` that are *not* preceded by
   ``at`` or ``@`` are not erased, since these are likely to be values and
   not time expressions.

   Time *durations* such as ``2 hrs`` are identified and removed.

To illustrate the erasure process, consider this somewhat contrived example:
::
   Her BP at 3:27 on 3/27 from her 12 cm. x9cm x6  cm. heart was 110/70.

Here we see a sentence containing the time expression ``3:27``, a date
expression ``3/27``, and a size measurement ``12 cm. x9cm x6  cm.``. The
measurement is irregularly formatted, as is often the case with clinical
text.

Suppose that the query term is ``BP``.  When the value extractor processes
this sentence, it converts the sentence to lowercase, then scans for dates,
measurements, and times. The date and time expressions satisfy the criteria
for erasure specified above. The resulting sentence after preprocessing is:
::
   her bp at      on      from her                     heart was 110/70.

This is the text that the value extractor uses for subsequent stages.   

Candidate Selection
-------------------

After preprocessing, the value extractor constructs a regular expression for
a query involving each search term. Simple term matching **is not adequate**.
To understand why, consider a temperature query involving the term ``t``.
Term matching would result in a match for every letter t in the text.

The query regex enforces the constraint that the search term can only be found
at a word boundary (and not inside other text). The query regex accomodates
variable amounts of whitespace, separators, and fill words.

The query regex is incorporated into a list of additional regular expressions.
These regexes each scan the sentence and attempt to recognize various contexts
from which to extract values. These contexts are:

1. A range involving two fractions connected by between/and or from/to:
  
   ``BP varied from 110/70 to 120/80.``

2. A range involving two fractions:

   ``BP range: 105/75 - 120/70``

3. A fraction:

   ``BP lt. or eq 112/70``

4. A range with explicit unit specifiers:

   ``Platelets between 25k and 38k``

5. A numeric range involving between/and or from/to:

   ``Respiration rate between 22 and 32``

6. A numeric range:

   ``Respiration rate 22-32``

7. A query of the general form <query_term> <operator> <value>:

   ``The patient's pulse was frequently >= 60 bpm.``

8. A query of the general form <query_term> <words> <value>:

   ``Overall LVEF is severely depressed (20%).``

Several of the context regexes will usually match a given query, requiring
a resolution process to select a winner.

Enumerated Values
-----------------

TBD


Overlap Resolution
------------------

TBD


If a match is found, the numeric values are extracted, and filters for min
and max values and hypotheticals applied. If the values survive the filtering
operations, a python namedtuple containing all relevant fields is created.
All such namedtuples are appended to a list during processing. 

When no more regex matches can be found, the list of result namedtuples is
converted to JSON and returned to the caller.

Users can expect the value extractor to return the first valid numeric result
following a query term.

References
==========

.. [1] | H. Harkema, J. Dowling, T. Thornblade, W. Chapman
       | **ConText: an Algorithm for Determining Negation, Experiencer,**
       | **and Temporal Status from Clinical Reports**
       | *J. Biomed. Inform.*, 42(5) 839-851, 2009.
