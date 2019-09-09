.. _providerassertion:

Clarity.ProviderAssertion
=========================

Description
-----------

Simple task for identifying positive terms that are not hypothethical and related to the subject.
Read more :ref:`here<termfinderalgo>`.


Example
-------
::

    Clarity.ProviderAssertion({
      cohort:RBCTransfusionPatients,
      termset: [PRBCTerms],
      documentset: [ProviderNotes]
    });


Extends
-------
:ref:`base_task`


Arguments
---------

=====================  ===================  ========= ======================================
         Name                 Type          Required                  Notes
=====================  ===================  ========= ======================================
termset                :ref:`termset`       Yes
excluded_termset       :ref:`termset`       No        Matches that should be excluded if these terms are found
documentset            :ref:`documentset`   No
cohort                 :ref:`cohort`        No
sections               List[str]            No        Limit terms to specific sections
include_synonyms       bool                 No
include_descendants    bool                 No
include_ancestors      bool                 No
vocabulary             str                  No        Default: 'MIMIC'
=====================  ===================  ========= ======================================



Results
-------


=====================  ================  ==========================================
         Name                 Type                             Notes
=====================  ================  ==========================================
sentence               str               Sentence where the term was found.
section                str               Section where the term was found.
term                   str               Term identified
start                  str               Start position of term in sentence.
end                    str               End position of term in sentence.
negation               str               Negation identified by ConText.
temporality            str               Temporality identified by ConText.
experiencer            str               Experiencer identified by ConText.
=====================  ================  ==========================================


Collector
---------
No
