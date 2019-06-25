.. _ner:

Clarity.NamedEntityRecognition
==============================

Description
-----------

Simple task that runs `spaCy <https://spacy.io/usage/linguistic-features#section-named-entities>`_'s NER model.

Example
-------
::

    Clarity.NamedEntityRecognition({
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
sections               List[str]            No        Limit terms to specific sections
=====================  ===================  ========= ======================================



Results
-------


=====================  ================  ==========================================
         Name                 Type                             Notes
=====================  ================  ==========================================
term                   str               The original entity text.
text                   str               Same as `term`
start                  int               Index of start of entity
end                    int               Index of end of entity
label                  str               Label of the entity, e.g. PERSON, MONEY, DATE. See `here for more <https://spacy.io/api/annotation#named-entities>`_
description            str               Description of the entity
=====================  ================  ==========================================


Collector
---------
No