.. _o2sat:

Clarity.O2SaturationTask
========================

Description
-----------

This is a custom task for extracting
`Oxygen <https://www.amazon.com/Oxygen-molecule-Oxford-Landmark-Science/dp/0198784937>`_
saturation information from clinical text. The ``O2SaturationTask`` processes
sentences and looks for information about Oxygen saturation levels and the use
of supplemental Oxygen devices. For instance, the sentence:
::
   Vitals were T 98 BP 163/64 HR 73 O2 95% on 55% venti mask

contains ``O2 95% on 55% venti mask``, meaning that the patient's blood Oxygen
saturation level (probably measured by a
`pulse oximeter <https://en.wikipedia.org/wiki/Pulse_oximetry>`_)
is 95%, while receiving supplemental Oxygen via a
`Venturi mask <https://en.wikipedia.org/wiki/Venturi_mask>`_. The flow rate
through the mask is sufficient to produce a 55% Oxygen concentration in the
air that the patient breathes.

The ``O2SaturationTask`` captures the Oxygen saturation level and other
data relevant to Oxygen delivery, flow rates, partial pressures, etc. If
sufficient clues are provided in the sentence, standard conversions are used
to estimate related quantities not explicitly stated. The complete set of
output fields and estimated quantities is listed in the Results section
below. Estimated values have field names with the suffix ``_est``, to
distinguish them from values extracted directly from the text.

Conversions
-----------

The partial pressure of Oxygen in arterial blood can be estimated from a
pulse oximeter reading. From the supplemental data provided with
reference [1]_:

============= ============
SpO2 (%)      PaO2 (mmHg)
============= ============
      80            44
      81            45
      82            46
      83            47
      84            49
      85            50
      86            52
      87            53
      88            55
      89            57
      90            60
      91            62
      92            65
      93            69
      94            73
      95            79
      96            86
      97            96
      98           112
      99           145
============= ============

The *fraction of inspired Oxygen* ``FiO2`` can be estimated from knowledge of
the Oxygen delivery device and the O2 flow rate. For normal breathing in the
Earth's atmosphere the O2 concentration is
`approximately 21% <https://en.wikipedia.org/wiki/Atmosphere_of_Earth>`_.
Hence the FiO2 for these conditions is 21%, or 0.21.

For a `nasal cannula <https://en.wikipedia.org/wiki/Nasal_cannula>`_, each L/min
of O2 adds approximately 4% to the FiO2 value [1]_. (The data in [1]_ covers the
range of 1-6 L/min, but the 4%/L rule seems to be the standard approximation in
the respiratory therapy literature for moderately higher flow nasal cannulas).

================================ ============
Nasal Cannula Flow Rate (L/min)  FiO2 (%)
================================ ============
             1                       24
             2                       28
             3                       32
             4                       36
             5                       40
             6                       44
             7                       48
             8                       52
             9                       56
             10                      60
================================ ============

For a `nasopharyngeal catheter <https://en.wikipedia.org/wiki/Airway_management>`_ [1]_:

========================================== ============
Nasopharyngeal Catheter Flow Rate (L/min)  FiO2 (%)
========================================== ============
                1                             24
                2                             28
                3                             32
                4                             36
                5                             40
                6                             44
                7                             48
                8                             52
                9                             56
                10                            60
========================================== ============

For a `simple fask mask with no reservoir <https://en.wikipedia.org/wiki/Simple_face_mask>`_:

============================ ============
Face Mask Flow Rate (L/min)  FiO2 (%)
============================ ============
             5                  35
             6                  39
             7                  43
             8                  47
             9                  51
             10                 55
============================ ============

For a `face mask with reservoir (non-rebreather) <https://en.wikipedia.org/wiki/Non-rebreather_mask>`_ [1]_:

=========================================== ============
Face Mask With Reservoir Flow Rate (L/min)  FiO2 (%)
=========================================== ============
                  6                            60
                  7                            70
                  8                            80
                  9                            90
                  10                           95
=========================================== ============

For a `Venturi mask <https://www.youtube.com/watch?v=W2mbRyTt_7k>`_:

=============================== ============
Venturi Mask Flow Rate (L/min)  FiO2 (%)
=============================== ============
             2                     24
             4                     28
             6                     31
             8                     35
             10                    40
             15                    60
=============================== ============

The ``O2SaturationTask`` uses the data in these tables to linearly interpolate
FiO2 values for the stated devices and flow rates.


Example
-------

::

    define final O2Data:
        Clarity.O2SaturationTask({
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
documentset            :ref:`documentset`   No
cohort                 :ref:`cohort`        No
=====================  ===================  ========= ======================================



Results
-------


=====================  ================  ==========================================
         Name                 Type                             Notes
=====================  ================  ==========================================
sentence               str               The input sentence after textual cleanup operations have been performed.
text                   str               That portion of `sentence` containing an O2 saturation statement.
start                  int               Offset into `sentence` of the first character of the O2 saturation statement.
end                    int               One character past the end of the O2 saturation statement.
device                 str               The Oxygen delivery device, if any.
flow_rate              float             Device Oxygen flow rate in liters/min.
condition              str               Relation of the O2 saturation to the stated `value`:
                                         'APPROX', 'LESS_THAN', 'LESS_THAN_OR_EQUAL',
                                         'GREATER_THAN', 'GREATER_THAN_OR_EQUAL',
                                         'EQUAL', 'RANGE'
value                  float             Oxygen saturation percentage
value2                 float             Oxygen saturation percentage, only valid for ranges
pao2                   int               Oxygen partial pressure in mmHg, if any
pao2_est               int               Oxygen partial pressure estimated from clues in sentence
fio2                   int               Fraction of inspired Oxygen, expressed as a percentage
fio2_est               int               Fraction of inspired Oxygen estimated from clues in sentence
p_to_f_ratio           int               PaO2/FiO2 extracted from sentence, if any
p_to_f_ratio_est       int               P/F ratio estimated from clues in sentence, if any
=====================  ================  ==========================================


Collector
---------
No


References
----------

.. [1] | Vlaar A, Toy P, Fung M, et. al.
       | **A Consensus Redefinition of Transfusion-Related Acute Lung Injury**
       | *Transfusion* (59) 2465-2476, 2019.
       | `https://www.ncbi.nlm.nih.gov/pubmed/30993745 <https://www.ncbi.nlm.nih.gov/pubmed/30993745>`_
