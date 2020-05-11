.. _pregnancytask:

Clarity.PregnancyTask
*********************

Description
-----------

This is a custom task for estimating pregnancy-related dates from pregnancy
duration statements in clinical text. For example, the phrase
``30 y/o 24wks pregnant`` in a clinical report dated July 1, 2019 implies that
conception occured 24 weeks prior, on approximately Jan. 14th. For a normal
40 week pregnancy, the estimated delivery date would be 40 - 24 == 16 weeks
into the future, or sometime around Oct. 21. The complete set of
pregnancy-related dates and times is listed below.

The relevant dates can be computed from a wide variety of duration
statements. Some examples:
::
   approx. 28 weeks pregnant
   she is 2.5 months pregnant
   pregnant at 26wks
   approx. 10-12 weeks pregnant
   patient is a 23 year G4P2 @ 27
   patient is a 29 yo G1 @ 5.3wks
   37 year old woman at 29 weeks
   etc.

Example
-------
::
   
   define final PregnancyFunction:
       Clarity.PregnancyTask({
           documentset: [Docs]
       });

Extends
-------
:ref:`base_task`


Arguments
---------

=====================  ===================  ========= ======================================
         Name                 Type          Required                  Notes
=====================  ===================  ========= ======================================
termset                :ref:`termset`       No        Termsets are not used by this task.
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
weeks_pregnant         int or float
weeks_remaining        int or float
trimester              int               1 if <=13 wks; 2 if [14, 26] wks; 3 otherwise
date_conception        str               YYYY-MM-DD format
date_delivery          str               YYYY-MM-DD format
=====================  ================  ==========================================


Collector
---------
No
