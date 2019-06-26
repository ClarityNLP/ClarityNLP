.. _tnm:

Clarity.TNMStager
=================

Description
-----------
Extract tumor stages from text. Read more :ref:`here<tnmalgo>`.

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

See the 'Outputs' table :ref:`here<tnmalgo>`.

Collector
---------
No
