.. _nlpqlref:

NLPQL Reference
===============

NLPQL Helpers
-------------

.. toctree::
   :maxdepth: 1

   nlpql/documentset
   nlpql/cohort
   nlpql/termset
   nlpql/context
   nlpql/macros

NLPQL Tasks
-----------
All tasks (or data entities) are prefixed in NLPQL as `define`, with the optional `final` flag. The `final` flag writes each result as part of the finalized result set in MongoDB.


Core Tasks
~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   nlpql/measurementfinder
   nlpql/ner
   nlpql/ngram
   nlpql/pos
   nlpql/provider_assert
   nlpql/proximity
   nlpql/term_finder
   nlpql/valueextractor


Custom Tasks
~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   nlpql/cqlexecution
   nlpql/ecog
   nlpql/gleason
   nlpql/o2sat
   nlpql/pftfinder
   nlpql/pregnancy
   nlpql/race
   nlpql/textstats
   nlpql/tnm
   nlpql/transfusion


Base Classes
~~~~~~~~~~~~

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
