.. _race:

Clarity.RaceFinderTask
======================

Description
-----------

This is a custom task for extracting a patient's race (i.e. asian, african american, caucasian, etc.).

Example
-------

::

    define RaceFinderFunction:
        Clarity.RaceFinderTask({
            documentset: [DischargeSummaries]
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
sentence               str
start                  int
end                    int
value                  str               Race mentioned in note
value_normalized       str               Normalized value, e.g. caucasian -> white
=====================  ================  ==========================================


Collector
---------
No