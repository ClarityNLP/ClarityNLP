.. _gleason:

Clarity.GleasonScoreTask
========================

Description
-----------

This is a custom task for extracting a patients Gleason score, which is relevant to prostate cancer diagnosis and staging.

Example
-------

::

    define final GleasonFinderFunction:
        Clarity.GleasonScoreTask({
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
value                  int               Gleason score
value_first            int               First number in Gleason score
value_second           int               Second number in Gleason score
=====================  ================  ==========================================


Collector
---------
No