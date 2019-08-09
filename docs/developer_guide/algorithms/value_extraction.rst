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

We should emphasize that this is a **generic** value extractor. Our design goal
is to achieve good performance across a wide variety of value extraction
problems. It has **not** been specialized for any particular type of problem,
such as for extracting temperatures or blood pressures. It instead uses
an empirically-determined set of rules and regular expressions to find
values (either numeric or textual - see below) that are likely to be associated
with the query terms. These regexes and rules are under continual refinement
and testing as the development of ClarityNLP continues.

You can get a clearer picture of what the value extractor does and the
results that it finds by examining our comprehensive suite of
`value extractor tests <https://github.com/ClarityNLP/ClarityNLP/blob/develop/nlp/algorithms/value_extraction/test_value_extractor.py>`_.


Value Types
-----------

The value extractor can recognize several different value types:

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

The value extractor can associate queries and values expressed in many different
formats:

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

These are just a few of the many different variants that the value extractor supports.
In general, the amount of whitespace between query and value is arbitrary.

Result Filters
--------------

Numerical results can be filtered by user-specified min and max values.
Any results that fall outside of the interval ``[min, max]`` are discarded.
Any numeric value is accepted if these limits are omitted in the NLPQL
statement.

For fractions, the value extractor returns the numerator value by default.
The denominator can be returned instead by using the ``is_denom_only``
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
           str_enumlist=None,        # comma-separated string of terms (see below)
           is_case_sensitive=False,  # set to True to preserve case
           is_denom_only=False)      # set to True to return denoms

If the ``str_minval`` and ``str_maxval`` arguments are omitted, ClarityNLP accepts
any numeric value that it finds for a given query. The ``str_enumlist`` argument
will be explained below. The other arguments should be self-explanatory.

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

Text Mode and the Enumeration List
----------------------------------

The value extractor supports a mode of operation ("text mode") in which it
extracts text strings instead of numeric values. Text mode can be enabled by
supplying a comma-separated string of terms to the
:ref:`enum_list <valueextractor>` parameter in your NLPQL statement. The
enumlist acts like a term filter for the results. Only those terms
appearing in the enumlist are returned in the ``value`` field of the JSON
result.

To illustrate how text mode works, suppose you have the task of searching
medical records for the presence of hepatitis B or C infections. You want
to use ClarityNLP to scan the data and report any lab results that mention
HBV or HCV. The presence or absence of HBV or HCV is typically reported as
either "positive" or "negative", or sometimes as just "+" or "-".

You would start by constructing an enumlist with the terms and
symbols that you want, such as ``"positive, negative, +, -"``. This string
would be supplied as the value for the NLPQL enum_list.  Your
:ref:`termset <termset>` would include the strings ``"HBV"`` and ``"HCV"``.

Next suppose that, during a run, ClarityNLP were to encounter the sentence
``She was HCV negative, HBV +, IgM Titer-1:80, IgG positive``. The value
extractor would process this sentence, noticing the presence of the enumlist,
and therefore put itself into text mode. When processing completes the value
extractor would return two results. The first JSON result would have these
values for the matching "term" and "value" fields (other fields omitted):
::
   {
       "term":"HCV",
       "value":"negative"
   }

The second JSON result would have these values:
::
   {
       "term":"HBV",
       "value":"+"
   }

In this manner the value extractor supports the extraction of textual
"values" in addition to numeric values.

Algorithm
=========

The value extractor does its work in four stages. The first stage consists of
preprocessing operations; the second stage extracts candidate
values; the third stage performs overlap resolution to choose a winner
from among the candidates; and the fourth stage removes hypotheticals. All
results that remain are converted to JSON format and returned to the caller.

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

   Time *durations* such as ``2 hrs`` are identified and erased.

To illustrate the erasure process, consider this somewhat contrived example:
::
   Her BP at 3:27 on3/27 from her12 cm. x9cm x6  cm. heart was110/70.

Here we see a sentence containing the time expression ``3:27``, a date
expression ``3/27``, and a size measurement ``12 cm. x9cm x6  cm.``. The
sentence exhibits **irregular spacing**, as is often the case with clinical
text.

Suppose that the query term is ``BP``, meaning "blood pressure".  When the
value extractor processes this sentence, it converts the sentence to
lowercase, then scans for dates, measurements, and times. The date and time
expressions satisfy the criteria for erasure specified above. The resulting
sentence after preprocessing is:
::
   her bp at      on     from her                    heart was110/70.

This is the text that the value extractor uses for subsequent stages. Observe
that the erasure process preserves character offsets.

Candidate Selection
-------------------

After preprocessing, the value extractor constructs a regular expression for
a query involving each search term. **Simple term matching is not sufficient**.
To understand why, consider a temperature query involving the term ``t``.
Term matching would result in a match for every letter t in the text.

The query regex enforces the constraint that the search term can only be found
at a word boundary and not as a substring of another word. The query regex
accomodates variable amounts of whitespace, separators, and fill words.

The query regex is incorporated into a list of additional regular expressions.
These regexes each scan the sentence and attempt to recognize various contexts
from which to extract values. These contexts are, with examples:

1. A range involving two fractions connected by "between/and" or "from/to":
::
   BP varied from 110/70 to 120/80.

2. A range involving two fractions:
::
   BP range: 105/75 - 120/70

3. A fraction:
::
   BP lt. or eq 112/70

4. A range with explicit unit specifiers:
::
   Platelets between 25k and 38k

5. A numeric range involving "between/and" or "from/to":
::
   Respiration rate between 22 and 32

6. A numeric range:
::
   Respiration rate 22-32

7. A query of the general form <query_term> <operator> <value>:
::
   The patient's pulse was frequently >= 60 bpm.

8. A query of the general form <query_term> <words> <value>:
::
   Overall LVEF is severely depressed (20%).

Multiple regexes typically match a given query, so an overlap resolution
process is required to select the final result.


Overlap Resolution
------------------

If the value extractor finds more than one candidate for a given query, the
overlap resolution process prunes the candidates and selects a winner. The
rules for pruning candidates have been developed through many rounds of
iterated testing. More rules may be discovered in the future. The situations
requiring pruning and the rules for doing so are as follows:

1. **If two candidate results overlap exactly, return the result with the longest matching term.**

   Example:
       | sentence:``T=98 BP= 122/58  HR= 7 RR= 20  O2 sat= 100% 2L NC``
       | termset:``O2, O2 sat``
   Candiates:
       | ``{"term":"O2",     "value":100, "text":"O2 sat= 100"}``
       | ``{"term":"O2 sat", "value":100, "text":"O2 sat= 100"}``

   In this example, both "O2" and "O2 sat" match the value 100, and both
   matches have identical start/end values. The value extractor returns
   the candidate for "O2 sat" as the winner since it is the longer of the
   two query terms and completely encompasses the other candidate.
   
2. **If two results partially overlap, discard the first match if the extracted value is contained within the search term for the second.**

   Example:
       | sentence:``BP 120/80 HR 60-80s RR  SaO2 96% 6L NC.``
       | termset:``RR, SaO2``
   Candidates:
       | ``{"term":"RR",   "value":2,  "text":"RR  SaO2 96"}``
       | ``{"term":"SaO2", "value":96, "text":"SaO2 96"}``
       
   Note that the search term ``RR`` has no matching value in the sentence,
   so the value extractor keeps scanning and finds the 2 in "SaO2". The 2
   is part of a search term, not an independent value, so that candidate
   result is discarded.

3. (text mode only) **Whenever two results overlap and one result is a terminating substring of the other, discard the candidate with the contained substring.**

   Example:
       | sentence:``no enteric gram negative rods found``
       | termset:``gram negative, negative``
       | enumlist:``rods``
   Candidates:
       | ``{"term":"gram negative", "value":"rods", "text":"gram negative rods"}``
       | ``{"term":"negative",      "value":"rods", "text":"negative rods"}``

    The second candidate is a terminating substring of the first and is
    discarded. Note that this is a different situation from no. 1 above, since
    the matching text for the candidates have different starting offsets.

4. **If two candidates have overlapping matching terms, keep the candidate with the longest matching term.**

    Example:
       | sentence:``BLOOD PT-10.8 PTT-32.6 INR(PT)-1.0``
       | termset:``pt, ptt, inr(pt)``
    Candidates:
       | ``{"term":"pt",     "value":10.8, "text":"PT-10.8"}``
       | ``{"term":"pt",     "value":1.0,  "text":"PT)-1.0"}``
       | ``{"term":"ptt",    "value":32.6, "text":"PTT-32.6"}``
       | ``{"term":INR(PT)", "value":1.0,  "text":"INR(PT)-1.0"}``

    The second and fourth candidates have overlapping matching query terms.
    The longest matching term is ``INR(PT)``, so candidate four is retained and
    candidate two is discarded. This is a different situation from no. 3 above,
    which only applies in text mode.

5. (text mode only) **Keep both candidates if their matching terms are connected by "and" or "or".**

    Example:
        | sentence:``which grew gram positive and negative rods``
        | termset:``gram positive, negative``
        | enumlist:``rods``
    Candidates:
        | ``{"term":"gram positive", "value":"rods", "text":"gram positive and negative rods"}``
        | ``{"term":"negative",      "value":"rods", "text":"negative rods"}``

    The matching texts for each candidate consts of query terms connected by the word "and",
    so both results are kept.

6. **If two candidates have overlapping matching text but nonoverlapping query terms, keep the candidate with query term closest to the value.**

    Example:
        | sentence:``received one bag of platelets dure to platelet count of 71k``
        | termset:``platelets, platelet, platelet count``
    Candidates:
        | ``{"term":"platelets",      "value":71000, "text":"platelets due to platelet count of 71k"}``
        | ``{"term":"platelet count", "value":71000, "text":"platelet count of 71k"}``

    These candidates have overlapping matching texts with nonoverlapping query
    terms. Keep the candidate with query term "platelet count" since it is
    closest to the value of 71000.

After these pruning operations, any remaining candidates that express
hypothetical conditions (see above) are discarded. The survivor(s) are
converted to JSON and returned as the result(s).
    
In general, users can expect the value extractor to return the first valid
numeric result following a query term.

References
==========

.. [1] | H. Harkema, J. Dowling, T. Thornblade, W. Chapman
       | **ConText: an Algorithm for Determining Negation, Experiencer,**
       | **and Temporal Status from Clinical Reports**
       | *J. Biomed. Inform.*, 42(5) 839-851, 2009.
