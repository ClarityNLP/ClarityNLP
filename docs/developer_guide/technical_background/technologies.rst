Technologies We Use
===================

ClarityNLP is built on several popular open-source projects. In this section
we provide a brief overview of each project and describe how it is used by
ClarityNLP.


Docker
------

`Docker <https://www.docker.com/>`_ uses operating system level virtualization
to provide a means of isolating applications from each other and controlling
their access to system resources. Isolated applications run in restricted
environments called *containers*. A container includes the application and all
dependencies so that it can be deployed as self-contained unit.

ClarityNLP can be deployed as a set of Docker containers. The secure
OAuth2-based server configuration assumes this deployment mechanism. You can
find out more about the ClarityNLP setup options and our use of Docker in the
:ref:`setupindex` documentation.


Solr
----

Apache `Solr <https://lucene.apache.org/solr/>`_ is an enterprise search
platform with many advanced features including fault tolerance, distributed
indexing, and the ability to scale to billions of documents. It is fast,
highly configurable, and supports a wide range of user customizations.

ClarityNLP uses Solr as its primary document store. Any documents that
ClarityNLP processes must be retrieved from Solr. We provide instructions on
how to ingest documents into Solr. We also provide some python scripts to help
you with common data sets. See our :ref:`document_ingestion_index`
section for more.


PostgresSQL
-----------

`PostgreSQL <https://www.postgresql.org/>`_ is one of the leading open-source
relational database systems, distinguished by its robust feature set, ACID
compliance, and excellent performance. ClarityNLP uses Postgres to store data
required to manage each NLPQL job. Postgres is also used to store a large
amount of medical vocabulary and concept data.


MongoDB
-------

`MongoDB <https://www.mongodb.com/>`_ is a popular NoSQL document store. A
mongo *document* is a JSON object with user-defined fields and values. There
is no rigid structure imposed on documents. Multiple documents form groups
called *collections*, and one or more collections comprise a *database*.

ClarityNLP uses Mongo to store the results that it finds. The ClarityNLP
built-in and custom tasks all define result documents with fields meaningful
to each task. ClarityNLP augments the result documents with additional
job-specific fields and stores everything in a single collection.


NLP Libraries (spaCy, textacy, nltk)
------------------------------------

The natural language processing libraries `spaCy <https://spacy.io/>`_ and
`nltk <https://www.nltk.org/>`_ provide implementations of the fundamental NLP
algorithms that ClarityNLP needs. These algorithms include sentence
segmentation, part-of-speech tagging, and dependency parsing, among others.
ClarityNLP builds its NLP algorithms on top of the foundation provided by
spaCy and nltk.

`Textacy <https://github.com/chartbeat-labs/textacy>`_ is a higher-level NLP
library built on spaCy. ClarityNLP uses textacy for its :ref:`ngram` task and
for computing text statistics with :ref:`textstats`.


Luigi
-----

`Luigi <https://luigi.readthedocs.io/en/stable/index.html>`_ is a python
library that manages and schedules pipelines of batch processes. A *pipeline*
is an ordered sequence of tasks needed to compute a result. The tasks in the
pipeline can have *dependencies*, which are child tasks that must run and
finish before the parents can be scheduled to run. Luigi handles the task
scheduling, dependency management, restart-on-failure, and other necessary
aspects of managing these pipelines.

The :ref:`apiref` defines a set of core and custom tasks that comprise
the data processing capabilities of ClarityNLP. ClarityNLP uses Luigi to
schedule and manage the execution of these tasks.


Flask
-----

`Flask <http://flask.pocoo.org/>`_ is a "micro" framework for building Web
applications. Flask provides a web server and a minimal set of core features,
as well as an extension mechanism for including features found in more
comprehensive Web frameworks.

The ClarityNLP component that provides the :ref:`nlpwebapis` is built with
Flask.


Client-side Libraries (React, Sails)
------------------------------------



Redis
-----


.. Pandas
.. ------
