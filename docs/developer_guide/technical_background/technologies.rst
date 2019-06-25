Technologies We Use
===================

ClarityNLP depends on a set of leading open-source projects listed below. In
this section we provide a brief overview of each project and describe how it
is used by ClarityNLP.

Docker
------

`Docker <https://www.docker.com/>`_ uses operating system level virtualization
to provide a means of isolating applications from each other and controlling
their access to system resources. Isolated applications run in restricted
environments called *containers*. A container includes the application and all
dependencies so that it can be deployed as self-contained unit.

ClarityNLP can be deployed as a set of Docker containers. The secure
OAuth2-based server configuration assumes this deployment mechanism. You can
find out more about ClarityNLP setup options and its use of Docker in our
:ref:`setupindex` documentation.


Solr
----

Apache `Solr <https://lucene.apache.org/solr/>`_ is an enterprise search
platform with many advanced features including fault tolerance, distributed
indexing, and the ability to scale to billions of documents. It is fast,
highly configurable, and supports a wide range of user customizations.

ClarityNLP uses Solr as its primary document store. Any documents that
ClarityNLP processes must be retrieved from Solr. We provide documentation on
how to ingest your documents into Solr, as well as some python scripts to help
you with common data sets. See our :ref:`document_ingestion_index`
section for more.


PostgresSQL
-----------

`PostgreSQL <https://www.postgresql.org/>`_ is one of the leading open-source
relational database systems, distinguished by its robust feature set, ACID
compliance, and excellent performance. ClarityNLP uses Postgres to store data
relevant to NLPQL job management and control. Postgres is also used to store
a large amount of medical vocabulary and concept data.


MongoDB
-------


`MongoDB <https://www.mongodb.com/>`_ is a popular NoSQL document store.


NLP Libraries (spaCy, textacy, nltk)
------------------------------------


Flask
-----


Luigi
-----


Pandas
------


Client-side Libraries (React, Sails)
------------------------------------

Redis
-----

