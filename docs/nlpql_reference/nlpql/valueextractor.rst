.. _valueextractor:

Clarity.ValueExtraction
=======================

Description
-----------

Extract values from text, related to terms.
Read more :ref:`here<general-value-extraction>`.

Examples
--------
::

    define NYHAClass:
      Clarity.ValueExtraction({
        termset: [NYHATerms],
        enum_list: ["ii","iii","iv"];
        });

::


    define Temperature:
      Clarity.ValueExtraction({
        cohort:PlateletTransfusionPatients,
        termset: [TempTerms],
        minimum_value: "96",
        maximum_value: "106"
        });


Extends
-------
:ref:`base_task`


Arguments
---------

=====================  ===================  ========= ======================================
         Name                 Type          Required                  Notes
=====================  ===================  ========= ======================================
termset                :ref:`termset`       Yes       List of possible terms to find, e.g. 'NYHA'
documentset            :ref:`documentset`   No
cohort                 :ref:`cohort`        No
enum_list              List[str]            No        List of possible strings associated with the query terms
minimum_value          int                  No        Minimum allowable value; any extracted values less than this are ignored
maximum_value          int                  No        Maximum allowable value; any extracted values greater than this are ignored
case_sensitive         bool                 No        Default = false; whether to do a case-sensitive term match
=====================  ===================  ========= ======================================

Custom String Arguments
-----------------------

For these arguments, surround the string on each side of the ':' character with quotes.

For example:
::
   define systolic_blood_pressure:
       Clarity.ValueExtraction({
           termset: [blood_pressure_terms],
           documentset: [my_docs]
       });

   define diastolic_blood_pressure:
       Clarity.ValueExtraction({
           termset: [blood_pressure_terms],
           documentset: [my_docs],
           "denom_only":"True"
    });

=====================  ===================  ========= ======================================
         Name                 Type          Required                  Notes
=====================  ===================  ========= ======================================
denom_only             str                  No        Default = "False"; if "True", return denominators of fractions instead of
                                                      numerators
values_before_terms    str                  No        (for enumlist only) Default = "False"; if "True", look for `enum_list` strings
                                                      preceding the query terms. Otherwise look for enumlist strings following the
                                                      query terms.
=====================  ===================  ========= ======================================



Results
-------


=====================  ================  ==========================================
         Name                 Type                             Notes
=====================  ================  ==========================================
sentence               str               sentence where term and value are found
text                   str               substring of sentence containing term and value
start                  int               offset of the first character in the matching text
end                    int               offset of the final character in the matching text plus 1
term                   str               term from `termset` that was found to have an associated value
condition              str               relation of query term to value:
                                         'APPROX', 'LESS_THAN', 'LESS_THAN_OR_EQUAL',
                                         'GREATER_THAN', 'GREATER_THAN_OR_EQUAL',
                                         'EQUAL', 'RANGE', FRACTION_RANGE'
value                  str               the numeric value that was extracted
value1                 str               either identical to `value` or the first number of a range
value2                 str               either the empty string or the second number of a range
min_value              int               either identical to `value` or `min(value1, value2)` if both exist
max_value              int               either identical to `value` or `max(value1, value2)` if both exist
=====================  ================  ==========================================


Collector
---------
No
