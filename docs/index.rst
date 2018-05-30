.. ClarityNLP NLP documentation master file, created by
   sphinx-quickstart on Fri May 25 10:57:24 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ClarityNLP
==========

This is the home for clinical NLP phenotyping, algorithms, and related APIs with ClarityNLP.


Repository
----------
`GitHub
<https://github.com/ClarityNLP/ClarityNLP>`_

Setup
-----
This library uses Python 3.4+.

.. toctree::
   :maxdepth: 1

   local-docker
   local-nlp-setup
   production-docker
   technologies
   solr



Document Ingestion
------------------

To begin interacting with ClarityNLP, make sure you have ingested documents into Solr.

.. toctree::
   :maxdepth: 1

   ingest/generic_ingestion
   ingest/aact
   ingest/file_ingestion



APIs
----

.. toctree::
   :maxdepth: 1

   apis/apis
   apis/ohdsi
   apis/ngram
   apis/vocabulary


Phenotypes
----------

.. toctree::
   :maxdepth: 1

   nlpql
   pipelines
   phenotypes


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

Everything else...
------------------

.. toctree::
   :maxdepth: 1

   testing
   team
   partners
   projects

Sample files
------------
See `samples
<https://github.com/ClarityNLP/ClarityNLP/tree/master/nlp/samples/>`_.

License
-------
This project is licensed under Mozilla Public License 2.0.


Search
------

* :ref:`search`

