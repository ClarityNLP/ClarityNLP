Running ClarityNLP Locally
==========================

This is the best setup for getting started with ClarityNLP.



Setting up ClarityNLP Locally
-----------------------------

1. Install `Docker for Mac <https://www.docker.com/docker-mac>`_ or `Docker for Windows <https://www.docker.com/docker-windows>`_.

2. Run
::

    git clone https://github.com/ClarityNLP/ClarityNLP

3. Switch to the ClarityNLP directory
::

    cd ClarityNLP

4. Initialize submodules
::

    git submodule update --init --recursive

5. Add .env file, use .env.example as a start:

::

    touch .env
    cat .env.example >> .env

6. Run ClarityNLP (see below).


Running ClarityNLP
------------------
Build images and run containers. This will take 10-20 minutes the first time.
::

    sh run_claritynlp.sh

**Or call Docker Directly:**

::

    docker-compose up --build

(Optional) In a new terminal, verify containers are runnning.
::

    docker ps

The Luigi container will monitor for active tasks. It is expected to see the following output throughout the logs.
::

    LUIGI_SCHEDULER   | 2018-10-16 19:46:19,149 luigi.scheduler INFO     Starting pruning of task graph
    LUIGI_SCHEDULER   | 2018-10-16 19:46:19,149 luigi.scheduler INFO     Done pruning task graph


Shutting down ClarityNLP
------------------------
CMD+C (Mac) or Ctrl+C (Windows) from the window where ClarityNLP was started or you can run the following to
forcefully kill the containers.

::

    sh stop_all_docker_containers.sh



Docker Settings
---------------
These are the recommended setting for ClarityNLP. In Docker, they can be updated via Docker > Preferences > Advanced.

* Memory: >8GB
* Disk: >256GB recommended, but can run on much less (depends on data needs)


ClarityNLP Links
----------------
* `ClarityNLP API <http://localhost:5000>`_
* `ClarityNLP Solr <http://localhost:8983>`_
* `ClarityNLP Luigi <http://localhost:8082>`_
* `Report Type Mapper Docs <http://localhost:3000/>`_
* `Report Type Mapper Client <http://localhost:8000>`_
* `Ingest Client <http://localhost:8500/>`_
* `Results Client <http://localhost:8201/>`_

* ClarityNLP Postgres `jdbc:postgresql://localhost:5433/clarity`
* ClaritNLP Mongo `localhost:27017`
* Ingest Mongo `localhost:27020`




Updating to download latest changes
-----------------------------------
From the command line, run:

::

    git pull
    git submodule update --recursive
