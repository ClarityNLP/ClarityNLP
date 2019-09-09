.. _serversetupdoc:

Server Setup
============

The instructions below will get you up and running with a Docker-based
ClarityNLP instance on your server. We walk you through how to configure and
deploy a set of Docker containers comprising a complete ClarityNLP installation.
There is no need for you to separately install Solr, MongoDB, PostgreSQL, or
any of the other technologies that ClarityNLP uses.


Prerequisites
-------------

Download Source Code
~~~~~~~~~~~~~~~~~~~~
::

  git clone https://github.com/ClarityNLP/ClarityNLP

Edit Config File
~~~~~~~~~~~~~~~~

Open the env.sh file for editing.

If you are using a domain name, change ``HOST`` to be your domain name.

If you are using an IP address with no domain name, do nothing to ``HOST``.
Please read the Tip and Tricks section below if you are using an IP address with
no domain name.


Install Docker
~~~~~~~~~~~~~~

Follow the `installation instructions <https://docs.docker.com/install/#supported-platforms>`_.

These are the recommended Docker settings for ClarityNLP. In Docker, they can
be updated via Docker > Preferences > Advanced.

* Memory: >8GB
* Disk: >256GB recommended, but can run on much less (depends on data needs)

Install Docker Compose
~~~~~~~~~~~~~~~~~~~~~~
Follow the `installation guide <https://docs.docker.com/compose/install/>`_.


Run the Stack
-------------

The first time running it will take a couple minutes to pull the pre-built images from the
Docker Hub registry. Open a terminal at the project root and run the following:
::

  make start-clarity

To stop the stack, run this command:
::

  make stop-clarity

Tips & Tricks
-------------

ClarityNLP uses Let's Encrypt to provide TLS. By default, ClarityNLP informs
the ACME to use the TLS-ALPN-01 challenge to generate and renew certificates.
When using the TLS-ALPN-01 challenge, the server running ClarityNLP must be
reachable by Let's Encrypt through port 443.

If your server is behind a VPN and port 443 is not reachable by Let's Encrypt,
use a DNS-01 challenge instead. Follow the instructions on configuring a DNS-01
challenge by reading the `Traefik documentation <https://docs.traefik.io/v2.0/https/acme/#dnschallenge>`_.

Let's Encrypt does not issue certificates for public IP addresses, `only domain
names <https://community.letsencrypt.org/t/certificate-for-public-ip-without-domain-name/6082/14>`_.

If you are not using a domain name, a default certificate will be generated.
This certificate is not backed by a CA. ClarityNLP will still function, however
browsers will display a certificate warning to users.

To verify that the Docker containers are running, open a terminal and run:
::

  docker ps

You should see a display that looks similar to this. There are 15 containers
and all should have a status of ``Up`` when the system has fully initialized:
::
   CONTAINER ID        IMAGE                                  COMMAND                  CREATED              STATUS              PORTS                                      NAMES
   55ac065604e5        claritynlp_ingest-api                  "/app/wait-for-it-ex…"   54 seconds ago       Up 24 seconds       1337/tcp                                   INGEST_API
   ce2baf43bab0        claritynlp_nlp-api                     "/api/wait-for-it-ex…"   56 seconds ago       Up 54 seconds       5000/tcp                                   NLP_API
   c028e60d1fab        redis:4.0.10                           "docker-entrypoint.s…"   About a minute ago   Up 56 seconds       6379/tcp                                   REDIS
   4e1752025734        jpillora/dnsmasq                       "webproc --config /e…"   About a minute ago   Up 56 seconds       0.0.0.0:53->53/udp                         DNSMASQ
   2cf1dd63257a        mongo                                  "docker-entrypoint.s…"   About a minute ago   Up 55 seconds       27017/tcp                                  NLP_MONGO
   34385b8f4306        claritynlp_nlp-postgres                "docker-entrypoint.s…"   About a minute ago   Up 56 seconds       5432/tcp                                   NLP_POSTGRES
   500b36b387b7        claritynlp_ingest-client               "/bin/bash /app/run.…"   About a minute ago   Up 56 seconds       3000/tcp, 35729/tcp                        INGEST_CLIENT
   f528b68a7490        claritynlp_dashboard-client            "/bin/bash /app/run.…"   About a minute ago   Up 56 seconds       3000/tcp, 35729/tcp                        DASHBOARD_CLIENT
   8290a3846ae0        claritynlp_results-client              "/bin/bash /app/run.…"   About a minute ago   Up 56 seconds       3000/tcp, 35729/tcp                        RESULTS_CLIENT
   77fce3ae48fc        claritynlp_identity-and-access-proxy   "pm2-dev process.json"   About a minute ago   Up 57 seconds       6010/tcp                                   IDENTITY_AND_ACCESS_PROXY
   b6610c74ec4c        claritynlp_nlp-solr                    "docker-entrypoint.s…"   About a minute ago   Up 56 seconds       8983/tcp                                   NLP_SOLR
   45503f0fd389        claritynlp_identity-provider           "docker-entrypoint.s…"   About a minute ago   Up 57 seconds       5000/tcp                                   IDENTITY_PROVIDER
   6dc0f7f21a48        claritynlp_nginx-proxy                 "/app/docker-entrypo…"   About a minute ago   Up 56 seconds       0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp   NGINX_PROXY
   1d601b064a1c        axiom/docker-luigi:2.7.1               "/sbin/my_init --qui…"   About a minute ago   Up 57 seconds       8082/tcp                                   LUIGI_SCHEDULER
   7ab4b8e19c86        mongo:3.4.2                            "docker-entrypoint.s…"   About a minute ago   Up 58 seconds       27017/tcp                                  INGEST_MONGO

The Luigi container will monitor for active tasks. Once everything initializes,
you should periodically see the following lines in the console output:
::

  LUIGI_SCHEDULER   | 2018-10-16 19:46:19,149 luigi.scheduler INFO     Starting pruning of task graph
  LUIGI_SCHEDULER   | 2018-10-16 19:46:19,149 luigi.scheduler INFO     Done pruning task graph


ClarityNLP Links
----------------

The user interface (UI) components of ClarityNLP can be accessed on your
machine by opening a web browser and entering the URLs provided below.


Dashboard
~~~~~~~~~

The :ref:`ui_dashboard` is the main user interface to ClarityNLP. It provides
controls for ingesting documents, creating NLPQL files, accessing results and
lots more.

Dashboard URL: https://<host>/dashboard


Solr Administrative User Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Solr provides an administrative user interface that you can use to configure
and explore your ClarityNLP Solr instance. The Apache project provides full
documentation on the admin UI which you can find
`here <https://lucene.apache.org/solr/guide/6_6/using-the-solr-administration-user-interface.html>`_.

Perhaps the most useful component of this UI is the
`query tool <https://lucene.apache.org/solr/guide/6_6/query-screen.html#query-screen>`_,
which lets you submit queries to Solr and find documents of interest. The
ClarityNLP Solr installation provides more than 7000 documents in a core called
``sample``.

Solr Admin Interface URL: https://<host>/solr


Luigi Task Monitor
~~~~~~~~~~~~~~~~~~

The Luigi project provides a task monitor that displays information on
the currently running ClarityNLP job. ClarityNLP processes documents by dividing
the workload into parallel tasks that are scheduled by Luigi. The task
monitor displays the number of running tasks, how many have finished, any
failures, etc. You can update the task counts by simply refreshing the page.

Lugi Task Monitor URL: https://<host>/luigi


Ingest Client
~~~~~~~~~~~~~

The :ref:`ui_ingest_client` provides an easy-to-use interface to help you load new
documents into your ClarityNLP Solr instance. It also helps you map the fields
in your documents to the fields that ClarityNLP expects.

Ingest Client URL: https://<host>/ingest


Results Viewer
~~~~~~~~~~~~~~

The :ref:`ui_results_viewer` helps you examine the results from each of your
ClarityNLP runs. It highlights specific terms and values and provides an
evaluation mechanism that you can use to score the results that ClarityNLP
found.

Clarity Results Viewer URL: https://<host>/results


NLP API
~~~~~~~

<TODO - example of how to POST an NLPQL file using Postman or curl with access tokens>

.. * ClarityNLP API --> https://<host>/api
