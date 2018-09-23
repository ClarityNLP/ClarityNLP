.. pos:

Clarity.POSTagger
=================

Description
-----------

Simple task that runs `spaCy <https://spacy.io/api/annotation#section-pos-tagging>`_'s Part of Speech Tagger. Should not be ran on large data sets, as will result in a lot of data generation.

Example
-------
::

    Clarity.POSTagger({
      documentset: [FDANotes]
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
term                   str               Token being evaluated
text                   str               Same as `term`
lemma                  str               Lemma of term
pos                    str               POS tag. See list `here <http://universaldependencies.org/u/pos/>`_.
tag                    str               extended part-of-speech tag
dep                    str               dependency label
shape                  str               Token shape
is_alpha               bool              Is token all alphabetic
is_stop                bool              Is token a stop word
description            str               Tag description
=====================  ================  ==========================================


Collector
---------
No