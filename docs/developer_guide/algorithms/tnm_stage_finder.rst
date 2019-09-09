.. _tnmalgo:

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
document describes the TNM system and the information that ClarityNLP provides
for each TNM code that it recognizes.

Information on the TNM system was taken from the reference document [1]_ and
the explanatory supplement [2]_. Information on serum marker values was
taken from the Wikipedia article on the TNM staging system [3]_.


Source Code
===========

The source code for the TNM stage module is located in
``nlp/algorithms/value_extraction/tnm_stage_extractor.py``.

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

ClarityNLP uses a set of regular expressions to recognize TNM codes as a whole
and to decode the individual subgroups. A TNM code consists of mandatory
T, N, and M groups, as well as optional G, L, R, Pn, S, and V groups.
A staging designation may also be present.

Prefixes
--------

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

Certainty Factor
----------------

The T, N, and M groups can have an optional certainty factor,
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

T Group
-------

The T group describes the extent of the primary tumor:

==============  =====================================================
T Code          Meaning
==============  =====================================================
TX              primary tumor cannot be assessed
T0              no evidence of primary tumor
Tis             carcinoma *in situ*
T1, T2, T3, T4  increasing size and/or local extent of primary tumor
==============  =====================================================

For multiple tumors, the multiplicity appears in parentheses after
the T group code, e.g. ``T1(m)`` or ``T1(3)``. Anatomical subsites
are denoted with suffixes ``a``, ``b``, ``c``, or ``d``, e.g. ``T2a``.
Recurrence in the area of a primary tumor is denoted with the ``+``
suffix.

N Group
-------

The N group describes the extent of regional lymph node involvement:

==============  =====================================================
N Code          Meaning
==============  =====================================================
NX              reginal lymph node involvement cannot be assessed
N0              no regional lymph node metastasis
N1, N2, N3      increasing involvement of regional lymph nodes
==============  =====================================================

Anatomical subsites are denoted with suffixes ``a``, ``b``, ``c``, or
``d``, e.g. ``N1b``. With only micrometastasis (smaller than 0.2 cm),
the suffix ``(mi)`` should be used, e.g. ``pN1(mi)``.

Suffix ``(sn)`` indicates sentinal lymph node involvement.

Examination for isolated tumor cells (ITC) is indicated with the suffixes
in parentheses (e.g. ``pN0(i-)``):

==============  =====================================================
ITC Suffix      Meaning
==============  =====================================================
(i-)            no histologic regional node matastasis,
                negative morphological findings for ITC
(i+)            no histologic regional node metastasis,
                positive morphological findings for ITC
(mol-)          no histologic regional node metastasis,
                negative non-morphological findings for ITC
(mol+)          no histologic regional node metastasis,
                positive non-morphological findings for ITC
==============  =====================================================

Examination for ITC in sentinel lymph nodes uses these suffixes:

==============  =====================================================
ITC(sn) Suffix  Meaning
==============  =====================================================
(i-)(sn)        no histologic sentinel node matastasis,
                negative morphological findings for ITC
(i+)(sn)        no histologic sentinel node metastasis,
                positive morphological findings for ITC
(mol-)(sn)      no histologic sentinel node metastasis,
                negative non-morphological findings for ITC
(mol+)(sn)      no histologic sentinel node metastasis,
                positive non-morphological findings for ITC
==============  =====================================================

The TNM supplement [2]_ chapter 1, p. 8 recommends adding the number
of involved and examined regional lymph nodes to the ``pN``
classification (pathological classification), e.g. ``pN1b(2/11)``.
This example says that 11 regional lymph nodes were examined and
two were found to be involved.

M Group
-------

The M group describes the extent of distant metastasis:

==============  ==========================================================
M Code          Meaning
==============  ==========================================================
MX              metastasis cannot be assessed; considered inappropriate if
                metastasis can be evaluated based on physical exam alone;
                see [1]_ p. 24, [2]_ pp. 10-11.
M0              no distant metastasis
M1              distant metastasis
pMX             invalid category ([2]_, p. 10)
pM0             only to be used after autopsy ([2]_, p. 10)
pM1             distant metastasis microscopically confirmed
==============  ==========================================================

The ``M1`` and ``pM1`` subcategories may be extended by these optional
suffixes, indicating the location of the distant metastasis:

===============  ============
Location Suffix  Meaning
===============  ============
PUL              pulmonary
OSS              osseous
HEP              hepatic
BRA              brain
LYM              lymph nodes
MAR              bone marrow
PLE              pleura
PER              peritoneum
ADR              adrenals
SKI              skin
OTH              other
===============  ============

Anatomical subsites are denoted with suffixes ``a``, ``b``, ``c``, and ``d``.
The suffix ``(cy+)`` is valid for ``M1`` codes under certain conditions
(see [2]_ p. 11).

For isolated tumor cells (ITC) found in bone marrow ([2]_ p. 11), these
suffixes can be used:

======  ============================================
Suffix  Meaning
======  ============================================
(i+)    positive morphological findings for ITC
(mol+)  positive non-morphological findings for ITC
======  ============================================

R Group
-------

The R group describes the extent of residual metastases:

============= ===========================================================
R Code        Meaning
============= ===========================================================
RX            presence of residual tumor cannot be assessed
R0 (location) residual tumor cannot be detected by any diagnostic means
R1 (location) microscopic residual tumor at indicated location
R2 (location) macroscopic residual tumor at indicated location
============= ===========================================================

The TNM supplement ([2]_, p. 14) recommends annotating R with the location in
parentheses, e.g. ``R1 (liver)``. There can also be multiple R designations
if residual tumors exist in more than one location.

The presence of noninvasive carcinoma at the resection margin should be
indicated by the suffix ``(is)`` (see [2]_, p. 15).

The suffix ``(cy+)`` for R1 is valid under certain conditions ([2]_, p. 16).

G Group
-------

The G group discribes the histopathological grading score and has these
values:

====== =============================================
G Code Meaning
====== =============================================
GX     grade of differentiation cannot be assessed
G1     well differentiated
G2     moderately differentiated
G3     poorly differentiated
G4     undifferentiated
====== =============================================

| ``G1`` and ``G2`` may be grouped together as ``G1-2`` ([2]_, p. 23).
| ``G3`` and ``G4`` may be grouped together as ``G3-4`` ([2]_, p. 23).

L Group
-------

The L group indicates whether lymphatic invasion has occurred:


====== ======================================
L Code Meaning
====== ======================================
LX     lymphatic invasion cannot be assessed
L0     no lymphatic invasion
L1     lymphatic invasion
====== ======================================

V Group
-------

The V group indicates whether venous invasion has occurred:

====== ======================================
V Code Meaning
====== ======================================
VX     venous invasion cannot be assessed
V0     no venous invasion
V1     microscopic venous invasion
V2     macroscopic venous invasion
====== ======================================

Pn Group
--------

The Pn group indicates whether perineural invasion has occurred:

======= ======================================
Pn Code Meaning
======= ======================================
PnX     perineural invasion cannot be assessed
Pn0     no perinerual invasion
Pn1     perineural invasion
======= ======================================

Serum Group
-----------

The S group indicates the status of serum tumor markers:

====== ======================================
S Code Meaning
====== ======================================
SX     marker studies not available or not performed
S0     marker study levels within normal limits
S1     markers are slightly raised
S2     markers are moderately raised
S3     markers are very high
====== ======================================

Staging
-------

The staging value indicates the severity of the tumor. A staging assignment
depends on the tumor type and is indicated either with digits or roman
numerals, and optionally with subscript ``a``, ``b``, ``c``, or ``d``.
The stage designation can also have a ``y`` or ``yp`` prefix as well
([2]_, p. 18).

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

