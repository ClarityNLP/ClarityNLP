.. _transfusion:

Clarity.TransfusionNursingNotesParser
=====================================

Description
-----------

Task that parses Nursing notes (specifically formatted for Columbia University
Medical Center) for transfusion information.

Example
-------

::

    phenotype "TNN" version "2";

    include ClarityCore version "1.0" called Clarity;

    documentset TransfusionNotes:
        Clarity.createDocumentSet({
            "report_types":["Transfusion Flowsheet"]});

    define TransfusionOutput:
        Clarity.TransfusionNursingNotesParser({
            documentset: [TransfusionNotes]
            });


Extends
-------
:ref:`base_task`


Arguments
---------

=====================  ===================  ========= ======================================
         Name                 Type          Required                  Notes
=====================  ===================  ========= ======================================
termset                :ref:`termset`       No
documentset            :ref:`documentset`   No
cohort                 :ref:`cohort`        No
=====================  ===================  ========= ======================================



Results
-------


=====================  ================  ==========================================
         Name                 Type                             Notes
=====================  ================  ==========================================
reaction               str               yes or no
elapsedMinutes         int
transfusionStart       str               YYYY-MM-DD HH:MM:SS (ISO format)
transfusionEnd         str               YYYY-MM-DD HH:MM:SS (ISO format)
bloodProductOrdered    str
dateTime               str               YYYY-MM-DD HH:MM:SS (ISO format) at which these measurements were taken
timeDeltaMinutes       int               elapsed time in minutes since transfusionStart
dryWeightKg            float
heightCm               int
tempF                  float
tempC                  float
heartRate              int               units of beats/min
respRateMachine        int               units of breaths/min
respRatePatient        int               units of breaths/min
nibpSystolic           int
nibpDiastolic          int
nibpMean               int
arterialSystolic       int
arterialDiastolic      int
arterialMean           int
bloodGlucose           int               units of mg/dl
cvp                    int               units mmHg
spO2                   int               percentage
oxygenFlow             int               units of Lpm
endTidalCO2            int               units of mm Hg
fiO2                   int               percentage
=====================  ================  ==========================================


Collector
---------
No
