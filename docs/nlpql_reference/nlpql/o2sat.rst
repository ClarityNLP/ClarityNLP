.. _o2sat:

Clarity.O2SaturationTask
========================

Description
-----------

This is a custom task for extracting oxygen saturation information from clinical text.
This task processes each sentence of each input document, looking for information about
oxygen saturation levels in the blood. For instance, the sentence:
::
   Vitals as follows: BP 120/80 HR 60-80's RR SaO2 96% 6L NC

<TBD>


       
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
sentence               str               "Cleaned" version of input sentence
text                   str               That portion of `sentence` containing an O2 saturation statement.
start                  int               Offset into `sentence` of the first character of the O2 saturation statement.
end                    int               One character past the end of the O2 saturation statement.
device                 str               The Oxygen delivery device, if any.
flow_rate              float             Device Oxygen flow rate in liters/min.
condition              str               Relation of the O2 saturation to `value`:
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
