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
sentence               str               Sentence where measurement is found
text                   str               text of the complete measurement
start                  int               offset of the first character in the matching text
end                    int               offset of the final character in the matching text plus 1
value                  str               numeric value of first number (same as `dimension_X`)
term                   str               term from `termset` that matched a measurement
dimension_X            int               numeric value of first number
dimension_Y            int               numeric value of second number
dimension_Z            int               numeric value of third number
units                  str               either mm, mm2, or mm3
location               List[str]         location of measurement, if detected
condition              str               either ‘RANGE’ for numeric ranges, or ‘EQUAL’ for all others
temporality            str               CURRENT or PREVIOUS, indicating when the measurement occurred
min_value              int               either `min([x, y, z])` or `min(values)`
max_value              int               either `max([x, y, z])` or `max(values)`
=====================  ================  ==========================================


Collector
---------
No
