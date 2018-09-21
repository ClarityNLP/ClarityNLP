API Reference
=============


NLPQL Helpers
-------------

.. toctree::
   :maxdepth: 1

   nlpql/documentset
   nlpql/cohort
   nlpql/termset
   nlpql/context

NLPQL Tasks
-----------
All tasks (or data entities) are prefixed in NLPQL as `define`, with the optional `final` flag. The `final` flag writes each result as part of the finalized result set in MongoDB.


.. toctree::
   :maxdepth: 1

   nlpql/measurementfinder
   nlpql/ner
   nlpql/ngram
   nlpql/pos
   nlpql/provider_assert
   nlpql/term_finder
   nlpql/tnm
   nlpql/valueextractor
   nlpql/transfusion



Also see the following classes, which are the base classes for the NLPQL tasks:

.. toctree::
   :maxdepth: 1

   nlpql/base_task
   nlpql/base_collector



NLPQL Operations
----------------
All operations are prefixed in NLPQL as `define`, with the optional `final` flag. The `final` flag writes each result as part of the finalized result set in MongoDB.

.. toctree::
   :maxdepth: 1

   nlpql/operations


NLP Web APIs
------------
NLP endpoints provided by ClarityNLP.

.. toctree::
   :maxdepth: 2

   webapis/api_main_list
   webapis/vocabulary
   webapis/ngram_cohort
   webapis/ohdsi
