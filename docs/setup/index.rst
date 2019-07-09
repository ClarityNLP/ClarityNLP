.. _setupindex:

.. |br| raw:: html

   <br />

   
Setup
=====

The instructions below will guide you through the ClarityNLP setup and
installation process. There are several installation options for you to choose
from:

1. **Local Machine Setup with Docker**

   Choose this option if you will be the only user of ClarityNLP, you want to
   install ClarityNLP on your laptop or desktop, and you want everything to be
   configured for you.

   |br|
   
2. **Local Machine Setup without Docker**

   Choose this option if you will be the only user of ClarityNLP, you want to
   install ClarityNLP on your laptop or desktop, and you want to configure
   everything yourself.

   |br|
   
3. **Server Setup**

   Choose this option if you anticipate supporting multiple users. This is a
   Docker-based installation with OAuth2 security.


Local Machine Setup
-------------------

.. toctree::
   :maxdepth: 2

   local-docker
   local-no-docker

   
Server Setup
------------

.. toctree::
   :maxdepth: 2

   server_setup


.. _document_ingestion_index:
   
Document Ingestion
------------------

.. toctree::
   :maxdepth: 2

   ingest/generic_ingestion
   
.. Accessing ClarityNLP Securely
.. -----------------------------
.. The following section is useful if you need to interact directly with the ClarityNLP API via a HTTP client or a third-party app.


..   :maxdepth: 2

..   retrieve-access-token
..   add-third-party-app
   

.. Data Ingestion
.. --------------

.. To begin interacting with ClarityNLP, make sure you have ingested documents into Solr.


..   :maxdepth: 1

..   ingest/generic_ingestion
..   ingest/file_ingestion
