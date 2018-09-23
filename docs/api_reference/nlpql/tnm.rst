.. _tnm:

Clarity.TNMStager
=================

Description
-----------
Extract tumor stages from text. Read more `here <https://clarity-nlp.readthedocs.io/en/latest/developer_guide/algorithms/tnm_stage_finder.html>`_.

Example
-------
::

    define final TNMStage:
        Clarity.TNMStager ({
            cohort:PSAPatients,
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

See result outputs table `here <https://clarity-nlp.readthedocs.io/en/latest/developer_guide/algorithms/tnm_stage_finder.html>`_.

Collector
---------
No