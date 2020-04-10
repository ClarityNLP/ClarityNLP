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
        termset:[NYHATerms],
        enum_list:   ["ii","iii","iv"];
        });

::


    define Temperature:
      Clarity.ValueExtraction({
        cohort:PlateletTransfusionPatients,
        termset:[TempTerms],
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
enum_list              List[str]            No        List of possible values to find
minimum_value          int                  No        Minimum possible value
maximum_value          int                  No        Maximum possible value
case_sensitive         bool                 No        Default = false; Is value case sensitive
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
condition              str               either ‘RANGE’ for numeric ranges, or ‘EQUAL’ for all others
value                  str               the numeric value that was extracted
value1                 str               either identical to `value` or the first number of a range
value2                 str               either the empty string or the second number of a range
min_value              int               either identical to `value` or `min(value1, value2)` if both exist
max_value              int               either identical to `value` or `max(value1, value2)` if both exist
=====================  ================  ==========================================


Collector
---------
No
