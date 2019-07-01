Setup
=====
The following guides will get you started with ClarityNLP.

Single-User Setup with Docker
-----------------------------

.. toctree::
   :maxdepth: 2

   local-docker

Single-User Setup without Docker (Bare Bones)
---------------------------------------------

.. toctree::
   :maxdepth: 3

   bare-bones-setup

   
Multi-User (Production) Setup
-----------------------------

.. toctree::
   :maxdepth: 2

   production-docker
      
   
Accessing ClarityNLP Securely
-----------------------------
The following section is useful if you need to interact directly with the ClarityNLP API via a HTTP client or a third-party app.

.. toctree::
   :maxdepth: 2

   retrieve-access-token
   add-third-party-app
   

Data Ingestion
--------------

To begin interacting with ClarityNLP, make sure you have ingested documents into Solr.

.. toctree::
   :maxdepth: 1

   ingest/generic_ingestion
   ingest/file_ingestion
