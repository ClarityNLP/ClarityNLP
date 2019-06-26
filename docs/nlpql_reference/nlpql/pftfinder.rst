.. _pftfinder:

Clarity.PFTFinder
=================

Description
-----------

Custom module for extracting pulmonary function test (PFT) values.

Examples
--------
::

    termset Terms:
      ["FEV1", "FEV", "PFT", "pulmonary function test"];

    define final PFTTestPatients:
      Clarity.PFTFinder({
        termset:[Terms]
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
=====================  ===================  ========= ======================================



Results
-------


=====================  ================  ==========================================
         Name                 Type                             Notes
=====================  ================  ==========================================
sentence               str               Sentence where measurement is found
start                  int               offset of the first character in the matching text
end                    int               offset of the final character in the matching text plus 1
fev1_condition         str
fev1_units             str
fev1_value             floats
fev1_text              str
fev1_count             int
fev1_fvc_ratio_count   int
fev1_fvc_condition     str
fev1_fvc_units         str
fev1_fvc_value         float
fev1_fvc_text          str
fvc_count              int
fvc_condition          str
fvc_units              str
fvc_value              float
fvc_text               str
=====================  ================  ==========================================


Collector
---------
No
