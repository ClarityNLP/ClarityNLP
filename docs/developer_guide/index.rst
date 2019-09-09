Developer Guide
===============

For Algorithm Developers
------------------------

Technical Overview
^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   technical_background/technologies
   technical_background/solr
   technical_background/pipelines

   
Utility Algorithms
^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   algorithms/section_tagger
   algorithms/context
   algorithms/lexical_variants
   algorithms/sentence_tokenization
   algorithms/matrix_preprocessor

.. _task_algorithms_index:

Task Algorithms
^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   algorithms/term-finder
   algorithms/date_finder
   algorithms/time_finder
   algorithms/size_measurement_finder
   algorithms/tnm_stage_finder
   algorithms/value_extraction
   algorithms/measurement_subject_resolution

   
NLPQL Expression Evaluation Algorithms
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   algorithms/nlpql_expr_eval


Building Custom Task Algorithms
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   custom/custom

   
Testing
^^^^^^^

.. toctree::
   :maxdepth: 1
              
   testing
   
              
For App Developers
--------------------------

ClarityNLP Architecture
^^^^^^^^^^^^^^^^^^^^^^^

This library uses Python 3.6+.
The source code is hosted `here <https://github.com/ClarityNLP/ClarityNLP>`_.


Here's an overview of ClarityNLP's architecture.

.. Image:: clarity_simple.png
   :scale: 75 %
   :alt: ClarityNLP Simplified Architecture
   :align: center

           
Third-Party App Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   third_party_app_integration

FHIR Integration
^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   fhir
