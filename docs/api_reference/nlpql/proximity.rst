.. _proximity:

Clarity.TermProximityTask
=========================

Description
-----------

This is a custom task for performing a term proximity search. It takes two lists of search terms and a maximum word distance. If terms from lists 1 and 2 both appear in the sentence and are within the specified distance, the search succeeds and both terms appear in the results. A boolean parameter can also be provided that either enforces or ignores the order of the terms.

Example
-------

::

    define final TermProximityFunction:
        Clarity.TermProximityTask({
            documentset: [Docs],
            "termset1": [ProstateTerms],
            "termset2": "cancer, Gleason, Gleason's, Gleasons",
            "word_distance": 5,
            "any_order": "False"
        });


Extends
-------
:ref:`base_task`


Arguments
---------

=====================  =====================  ========= ======================================
         Name                 Type            Required                  Notes
=====================  =====================  ========= ======================================
documentset            :ref:`documentset`     No
cohort                 :ref:`cohort`          No
termset1               :ref:`termset` or str  Yes       :ref:`termset` or comma-separated list of terms to search for
termset2               :ref:`termset` or str  Yes       :ref:`termset` or comma-separated list of terms to search for
word_distance          int                    Yes       max distance between search terms
any_order              bool                   No        Default = false; Should terms in set1 come before terms in set1?
=====================  =====================  ========= ======================================



Results
-------


=====================  ================  ==========================================
         Name                 Type                             Notes
=====================  ================  ==========================================
sentence               str
start                  int               Start of entire matched phrase
end                    int               End of entire matched phrase
value                  str               Comma separated list of matched terms
word1                  str               First term matched
word2                  str               Second term matched
start1                 int               Start of first term
start2                 int               End of second term
end1                   int               Start of first term
end2                   int               End of second term
=====================  ================  ==========================================


Collector
---------
No
