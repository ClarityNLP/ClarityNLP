Extracting Tumor Stage Information
**********************************

Overview
========

The Union for International Cancer Control (UICC) has developed a system for
classifying malignant tumors called the TNM staging system. Each tumor is
assigned an alphanumeric code (the TNM code) that describes the extent of
the tumor, lymph node involvement, whether it has metastasized, and several
other descriptive factors. The code also includes staging information.
ClarityNLP can locate these codes in medical reports and decode them. This
document describes the TNM system and the information that Clarity provides
on decode.

Information on the TNM system was taken from the reference document [1]_ and
the explanatory supplement [2]_. Information on serum marker values was
taken from the Wikipedia article on the TNM staging system [3]_.


Source Code
===========

The source code for the TNM stage module is located in
``nlp/value_extraction/tnm_stage_extractor.py``.

Inputs
------

A single string representing the sentence to be searched for TNM codes.

Outputs
-------

A JSON array containing these fields for each code found:

==========================  ===================================================
Field Name                  Explanation
==========================  ===================================================
text                        text of the complete code
start                       offset of first char in the matching text
end                         offset of final char in the matching text + 1

t_prefix                    see prefix code table below
t_code                      extent of primary tumor
t_certainty                 primary tumor certainty factor
t_suffixes                  see T suffix table below
t_multiplicity              tumor multiplicity value

n_prefix                    see prefix code table below
n_code                      regional lymph node involvement
n_certainty                 certainty factor for lymph node involvement
n_suffixes                  see N suffix table below
n_regional_nodes_examined   number of regional lymph nodes examined
n_regional_nodes_involved   number of regional lymph nodes involved

m_prefix                    see prefix code table below
m_code                      distant metastasis
m_certainty                 certainty factor for distant metastasis
m_suffixes                  see M suffix table below

l_code                      lymphatic invasion code
g_code                      histopathological grading code
v_code                      venous invasion code
pn_code                     perineural invasion code
serum_code                  serum tumor marker code

r_codes                     residual metastases code
r_suffixes                  see R suffix table below
r_locations                 string array indicating location(s) of metastases

stage_prefix                see prefix table below
stage_number                integer value of numeric stage
stage_letter                supplementary staging information
==========================  ===================================================

All JSON measurement results contain an indentical number of fields. Any fields
that are not valid for a given measurement will have a value of EMPTY_FIELD and
should be ignored.



Algorithm
=========

Clarity uses a set of regular expressions to recognize TNM codes as a whole
and to decode the individual subgroups. A TNM code consists of mandatory
``T``, ``N``, and ``M`` groups, as well as optional ``G``, ``L``, ``R``,
``PN``, ``S``, and ``V`` groups.

The set of prefixes used for the groups is found in the next table:

==============  ===============================================================
Prefix Letter   Meaning
==============  ===============================================================
c               clinical classification
p               pathological classification
yc              clinical classification performed during multimodal therapy
yp              pathological classification performed during multimodal therapy
r               recurrent tumor
rp              recurrence after a disease-free interval, designated at autopsy
a               classification determined at autopsy
==============  ===============================================================

The ``T``, ``N``, and ``M`` groups can have an optional certainty factor,
which indicates the degree of confidence in the designation.  This certainty
factor was present in the 4th through 7th editions of the TNM guide, but it
has been removed from the 8th edition [1]_.

================  =================================================================
Certainty Factor  Meaning
================  =================================================================
C1                evidence from standard diagnostic means (inspection, palpitation)
C2                evidence from special diagnostic means (CT, MRI, ultrasound)
C3                evidence from surgical exploration, including biopsy and cytology
C4                evidence from definitive surgery and pathological examination
C5                evidence from autopsy
================  =================================================================



References
==========

.. [1] | J. Brierly, M. Gospodarowicz, C. Wittekind, *eds.*
       | **TNM Classification of Malignant Tumors, Eighth Edition**
       | *Union for International Cancer Control (UICC)*
       | Wiley Blackwell, 2017
       | https://www.uicc.org/resources/tnm

.. [2] | C. Wittekind, C. Compton, J. Brierly, L. Sobin, *eds.*
       | **TNM Supplement: A Commentary on Uniform Use**
       | *Union for International Cancer Control (UICC)*
       | Wiley Blackwell, 2012

.. [3] | https://en.wikipedia.org/wiki/TNM_staging_system

