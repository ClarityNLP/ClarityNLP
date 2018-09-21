.. _ngram:


Clarity.ngram
=============

Description
-----------

Task that aggregates n-grams across the selected document set. Uses `textacy <https://github.com/chartbeat-labs/textacy>`_. There's no need to specify `final` on this task. Any n-gram that occurs at at least the minimum frequency will show up in the final result.

Example
-------
::

  define demographicsNgram:
    Clarity.ngram({
      termset:[DemographicTerms],
      "n": "3",
      "filter_nums": false,
      "filter_stops": false,
      "filter_punct": true,
      "min_freq": 2,
      "lemmas": true,
      "limit_to_termset": true
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
n                      int                  No        Default = 2
filter_nums            bool                 No        Default = false; Exclude numbers from n-grams
filter_stops           bool                 No        Default = true; Exclude stop words
filter_punct           bool                 No        Default = true; Exclude punctuation
lemmas                 bool                 No        Default = true; Converts work tokens to lemmas
limit_to_termset       bool                 No        Default = false; Only include n-grams that contain at least one term from `termset`
min_freq               bool                 No        Default = 1; Minimum frequency for n-gram to return in final result
=====================  ===================  ========= ======================================



Results
-------


=====================  ================  ==========================================
         Name                 Type                             Notes
=====================  ================  ==========================================
text                   str               The n-gram detected
count                  int               The number of occurrences of the n-gram
=====================  ================  ==========================================


Collector
---------
:ref:`base_collector`
