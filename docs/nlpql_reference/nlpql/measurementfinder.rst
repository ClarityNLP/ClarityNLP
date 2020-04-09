.. _measurementfinder:

Clarity.MeasurementFinder
=========================

Description
-----------

Task for extracting size measurements from text, based on the given `termset`.
Read more about MeasurementFinder :ref:`here<measurementfinderalgo>`.

Example
-------
::

    define ProstateVolumeMeasurement:
        Clarity.MeasurementFinder({
            documentset: [RadiologyReports],
            termset: [ProstateTerms]
        });


Extends
-------
:ref:`base_task`


Arguments
---------

=====================  ===================  ========= ======================================
         Name                 Type          Required                  Notes
=====================  ===================  ========= ======================================
termset                :ref:`termset`       Yes
documentset            :ref:`documentset`   No
cohort                 :ref:`cohort`        No
sections               List[str]            No        Limit terms to specific sections
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
meas_object            List[str]         the object being measured; if ClarityNLP cannot decide, a list of possible objects
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
