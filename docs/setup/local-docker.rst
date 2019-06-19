Getting Up and Running on a Single Machine With Docker
======================================================
  
The instructions below will get you up and running with a Docker-based
ClarityNLP development environment on your laptop or desktop. We walk you
through how to configure and deploy a set of Docker containers comprising a
complete ClarityNLP installation for a single user. There is no need for you to
separately install Solr, MongoDB, PostgreSQL, or any of the other technologies
that ClarityNLP uses. Everything in the Docker containers has been setup and
configured for you.

Multi-user deployments of ClarityNLP should instead follow the instructions
for a production or enterprise deployment.

If you want a single-user deployment without using Docker, then you need our
:ref:`barebonessetup`.


Prerequisites
-------------

Download Source Code
~~~~~~~~~~~~~~~~~~~~
::

  git clone https://github.com/ClarityNLP/ClarityNLP

Initialize Submodules
~~~~~~~~~~~~~~~~~~~~~
::

  cd ClarityNLP
  git checkout <branch> # develop for latest, master for stable, or tagged version
  git submodule update --init --recursive --remote

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

Install mkcert
~~~~~~~~~~~~~~
The mkcert utility automatically creates and installs a local certificate
authority (CA) in the system root store. It also generates locally-trusted
certificates.

macOS
"""""

On macOS, use `Homebrew <https://brew.sh/>`_. ::

  brew install mkcert
  brew install nss # if you use Firefox

or `MacPorts <https://www.macports.org/>`_. ::

  sudo port selfupdate
  sudo port install mkcert
  sudo port install nss # if you use Firefox

Linux
"""""

On Linux, first install certutil. ::

  sudo apt install libnss3-tools
      -or-
  sudo yum install nss-tools
      -or-
  sudo pacman -S nss

Then you can install using `Linuxbrew <https://docs.brew.sh/Homebrew-on-Linux>`_ ::

  brew install mkcert

Windows
"""""""

On Windows, use Chocolatey ::

  choco install mkcert

or use Scoop ::

  scoop bucket add extras
  scoop install mkcert

Generate Development Certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First, create the local certificate authority:
::

  mkcert -install

Run the following command at the root of the ClarityNLP project: ::

  mkcert -cert-file certs/claritynlp.dev.crt -key-file certs/claritynlp.dev.key claritynlp.dev "*.claritynlp.dev"

Extra Prerequisites for Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Windows, install Cygwin and its dependencies ::

  choco install cygwin
  choco install cyg-get git git-completion make

Run the Stack
-------------

The first time running it will take some time to build the Docker images, but
subsequent runs will occur quickly. First, start Docker if it is not already
running. Next, open a terminal (Cygwin on Windows) at the project root and run
the following for local development:
::

  make start-clarity

The stack is running in the foreground, and can be stopped by simultaneously
pressing the ``CTRL`` and ``C`` keys.

After stopping the stack, run this command to remove the containers and
any networks that were created:
::

  make stop-clarity

Tips & Tricks
-------------

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

The user interface components of ClarityNLP can be accessed on your machine via
the ``.dev`` top-level domain. All Docker containers must be up and running to
access these components at the links provided below.

Dashboard
~~~~~~~~~

The dashboard (https://dashboard.claritynlp.dev) is the main user interface
to ClarityNLP.

<link to documentation page for the dashboard>


Solr Administrative User Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Solr UI (https://solr.claritynlp.dev) is the administrative interface to
the ClarityNLP Solr instance. Documentation on how to use the UI can be found
`here <https://lucene.apache.org/solr/guide/6_6/using-the-solr-administration-user-interface.html>`_.

Probably the most useful interface component is the
`query tool <https://lucene.apache.org/solr/guide/6_6/query-screen.html#query-screen>`_, which lets you
submit queries to Solr and find documents of interest. The ClarityNLP Solr
installation includes 7015 sample documents in a core called ``sample``.
  
Luigi Task Monitor
~~~~~~~~~~~~~~~~~~

The Luigi task monitor (https://luigi.claritynlp.dev) provides information on
the currently running ClarityNLP job. ClarityNLP processes documents by dividing
the workload into parallel tasks. These tasks are scheduled by Luigi. The task
monitor displays the number of running tasks, how many have finished, etc.
You can update the task counts by simply refreshing the page.

Ingest Client
~~~~~~~~~~~~~

* Clarity Ingest --> https://ingest.claritynlp.dev

Results Viewer
~~~~~~~~~~~~~~

* Clarity Results --> https://viewer.claritynlp.dev

TBD - describe how to access the API
  
* ClarityNLP API --> https://api.claritynlp.dev
