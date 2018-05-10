.. Clarity Health NLP documentation master file, created by
   sphinx-quickstart on Wed May  9 18:27:16 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Clarity Health NLP
==================

This is the home for clinical NLP phenotyping, algorithms, and related APIs with Clarity.

.. image:: https://travis-ci.org/ClarityNLP/health-nlp.svg?branch=master
    :target: https://travis-ci.org/ClarityNLP/health-nlp

Repository
----------
`GitHub
<https://github.com/ClarityNLP/health-nlp>`_

Setup
-----
This library uses Python 3.4+.

.. toctree::
   :maxdepth: 2

   setup
   technologies


Document Ingestion
------------------

To begin interacting with Clarity, make sure you have ingested documents into Solr.

.. toctree::
   :maxdepth: 2

   ingest/aact
   ingest/file_ingestion



APIs
----

.. toctree::
   :maxdepth: 2

   apis/apis
   apis/ohdsi
   apis/ngram
   apis/vocabulary


Phenotypes
----------

.. toctree::
   :maxdepth: 2

   intro_to_phenotypes
   pipelines
   nlpql

Algorithms
----------

.. toctree::
   :maxdepth: 2

   algorithms/size_measurement_finder
   algorithms/tnm_stage_finder
   algorithms/value_extraction
   algorithms/measurement_subject_resolution
   algorithms/section_tagger

Everything else...
------------------

.. toctree::
   :maxdepth: 2

   testing
   team
   partners
   projects

Sample files
------------
See `samples
<https://github.com/ClarityNLP/health-nlp/tree/master/samples/>`_.

License
-------
This project is licensed under Mozilla Public License 2.0.


Search
------

* :ref:`search`
