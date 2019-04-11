Getting Up and Running Locally With Docker
==========================================
The steps below will get you up and running with a local ClarityNLP development environment.

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

| Follow the `installation instructions <https://docs.docker.com/install/#supported-platforms>`_.
|
| These are the recommended Docker settings for ClarityNLP. In Docker, they can be updated via Docker > Preferences > Advanced.

* Memory: >8GB
* Disk: >256GB recommended, but can run on much less (depends on data needs)

Install Docker Compose
~~~~~~~~~~~~~~~~~~~~~~
Follow the `installation guide <https://docs.docker.com/compose/install/>`_.

Install mkcert
~~~~~~~~~~~~~~
mkcert automatically creates and installs a local CA in the system root store, and generates locally-trusted certificates.

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
First, create local CA: ::

  mkcert -install

Run the following command at the root of the ClarityNLP project: ::

  mkcert -cert-file certs/claritynlp.dev.crt -key-file certs/claritynlp.dev.key claritynlp.dev "*.claritynlp.dev"

Run the Stack
-------------

The first time running it will take some time to build the Docker images, but subsequent runs will occur quickly.
Open a terminal at the project root and run the following for local development: ::

  make start-clarity

| The stack is running in the foreground, and can be stopped via CMD+C (Mac/Linux) or Ctrl+C (Windows).
|
| In order to remove the containers and any networks that were created:

::

  make stop-clarity

Tips & Tricks
-------------

In order to verify containers are running: ::

  docker ps

The Luigi container will monitor for active tasks. It is expected to see the following output throughout the logs. ::

  LUIGI_SCHEDULER   | 2018-10-16 19:46:19,149 luigi.scheduler INFO     Starting pruning of task graph
  LUIGI_SCHEDULER   | 2018-10-16 19:46:19,149 luigi.scheduler INFO     Done pruning task graph


ClarityNLP Links
----------------
* ClarityNLP Dashboard --> https://dashboard.claritynlp.dev
* ClarityNLP API --> https://api.claritynlp.dev
* ClarityNLP Solr --> https://solr.claritynlp.dev
* ClarityNLP Luigi --> https://luigi.claritynlp.dev
* Clarity Ingest --> https://ingest.claritynlp.dev
* Clarity Results --> https://viewer.claritynlp.dev
