Developer Guide
===============
This library uses Python 3.4+.

Repository
----------
`GitHub
<https://github.com/ClarityNLP/ClarityNLP>`_



Technical Background
--------------------
.. toctree::
   :maxdepth: 1

   technical_background/technologies
   technical_background/solr
   technical_background/pipelines
   testing


Custom Local Setup
------------------
Use this setup only when you are not using Docker, and just wish to run the main NLP Flask API standalone. You might do this if you already have a Solr, Postgres and MongoDB hosted elsewhere, or you don't want to host them locally.

.. toctree::
   :maxdepth: 1

   local-nlp-setup



Algorithms
----------

.. toctree::
   :maxdepth: 1

   algorithms/term-finder
   algorithms/size_measurement_finder
   algorithms/tnm_stage_finder
   algorithms/value_extraction
   algorithms/measurement_subject_resolution
   algorithms/section_tagger
   algorithms/context


Building Custom Algorithms
--------------------------

.. toctree::
   :maxdepth: 1

   custom/custom


