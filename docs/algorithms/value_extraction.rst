General Value Extraction
************************

Overview
========

Value extraction is the process of scanning text for query terms and finding
numeric values associated with those terms. For example, consider this
sentence:

    ``The patient's heart rate was 60 beats per minute.``

The value extraction process applied to this sentence would return the
value "60" for the query "heart rate".

In general, the value can occur either before or after the query.
Using "temperature" as the query term, the next two sentences illustrate
the value of 98.6 occurring in each position:

 |   ``A 98.6F temperature was measured during the exam.    (before)``
 |   ``A temperature of 98.6F was measured during the exam. (after)``

Clarity's value extractor makes the following assumption about the relative
positioning of the query terms and the value:

    **Clarity assumes that the value FOLLOWS the query terms.**

Assuming that the value follows the query terms does **not** imply anything about
the distance between the query and the value. Sometimes the value immediately
follows the query, as in terse lists of vital signs:

    ``Vitals: Temp 100.2 HR 72 BP 184/56 RR 16 sats 96% on RA``

Other times, in narrative text, one or more words can fill the space between
query and value:

    ``The temperature measured for the patient at the exam was 98.6F.``

Clarity is able to handle both of these situations and correctly associate the
value 98.6 with "temperature".

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

Fractions can have arbitrary whitespace to either side of the forward
slash, as some of these examples illustrate.

Value Relationships
-------------------

