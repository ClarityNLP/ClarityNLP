.. _ecog_custom:

Clarity.EcogCriteriaTask
========================

Description
-----------

This is a custom task for finding Eastern Cooperative Oncology Group (ECOG)
performance status scores in clinical trial inclusion and exclusion criteria.

An ECOG score provides a measure of the health and physical capabilities of a
patient. The scores range from 0 to 5, with higher scores indicating greater
degrees of physical disability. A score of 0 means perfect health and a score
of 5 means death.

These scores are typically used in oncology to assess a patient's suitability
for various treatments.

Example
-------
::
   
   define final EcogCriteriaFunction:
       Clarity.EcogCriteriaTask({
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
criteria_type          str               Either 'Inclusion' or 'Exclusion'
score_0                int               1 if ECOG score 0 was found, 0 if not
score_1                int               1 if ECOG score 1 was found, 0 if not
score_2                int               1 if ECOG score 2 was found, 0 if not
score_3                int               1 if ECOG score 3 was found, 0 if not
score_4                int               1 if ECOG score 4 was found, 0 if not
score_5                int               1 if ECOG score 5 was found, 0 if not
score_lo               int               value of the minimum ECOG score
score_hi               int               value of the maximum ECOG score
=====================  ================  ==========================================


Collector
---------
No
