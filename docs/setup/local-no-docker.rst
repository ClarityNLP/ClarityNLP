.. _nativesetup:

Local Machine Setup without Docker
==================================

This page provides instructions on how to run ClarityNLP locally on your
machine **without** having to use Docker or OAuth2. We call this a *native*
installation of ClarityNLP. It is much simpler to use Docker, since everything
is provided and configured for you. But if you want more control over your
ClarityNLP installation and you prefer to configure everything yourself, then
these are the instructions you need.

This installation is also useful if you neither need nor want the OAuth2
security layers built into the Docker version of ClarityNLP. A native
installation is emphatically **NOT** appropriate for patient data that must
be protected in a HIPAA-compliant manner. So only store de-identified public
data in your Solr instance if you choose to do this.

Overview
--------

There are five major components in a ClarityNLP installation:
`Solr <https://lucene.apache.org/solr/>`_,
`PostgreSQL <https://www.postgresql.org/>`_,
`MongoDB <https://www.mongodb.com/>`_,
`Luigi <https://luigi.readthedocs.io/en/stable/#>`_, and
`Flask <http://flask.pocoo.org/>`_.

ClarityNLP uses Solr to index, store, and search documents; Postgres to store
job control data and lots of medical vocabulary; Mongo to store results;
Luigi to control and schedule the various processing tasks, and Flask to
provide API endpoints and the underlying web server.

A native installation means that, at a minimum, Luigi and Flask are
installed and run locally on your system. Solr, Postgres, and Mongo can also
be installed and run locally on your system, or one or more of these can be
hosted elsewhere.

A university research group, for example, could have a hosted Solr instance on
a VPN that is accessible to all members of the group. The Solr instance might
contain `MIMIC <https://mimic.physionet.org/>`_ or other de-identified, public
data. Members of the research group running a native ClarityNLP
installation would configure their laptops to use the hosted Solr instance.
This can be accomplished via settings in a ClarityNLP configuration file, as
explained below. These users would install and run Postgres, Mongo, Luigi, and
Flask on their laptops.

At GA Tech we have hosted versions of Solr, Postgres, and MongoDB. Our native
ClarityNLP users only need to install and run Luigi and Flask on their
laptops, and then setup their configuration file to "point" to the hosted
instances.

These flexible configuration options are also available with the
container-based, secure version of ClarityNLP.

The instructions below have been tested on:

- MacOS 10.14 "Mojave"
- MacOS 10.13 "High Sierra"
- Ubuntu Linux 18.04 LTS "Bionic Beaver"

Recent versions of MongoDB, PostgreSQL, and Solr are assumed:

- MongoDB version 3.6 or greater
- PostgreSQL version 10 or 11
- Solr version 7 or 8

Roadmap
-------

This installation and configuration process is somewhat lengthy, so here's a
high-level overview of what we'll be doing.

First, we'll need to setup and install the source code, the necessary python
libraries, and all of the associated python and non-python dependencies. We
will perform the installation inside of a custom
`conda <https://www.anaconda.com>`_-managed environment
so that ClarityNLP will not interfere with other software on your system.

Next we'll install and/or configure Solr, PostgreSQL, and MongoDB,
depending on whether you have access to hosted instances or not.

Then we'll ingest some test documents into Solr and run a sample NLPQL file so
that we can verify that the system works as expected.

After that we'll show you where you can find instructions for ingesting your
own documents into Solr, after which you will be ready to do your own
investigations.

The instructions below denote MacOS-specific instructions with **[MacOS]**,
Ubuntu-specific instructions with **[Ubuntu]**, and instructions valid for
all operating systems with **[All]**.


Install the Prerequisites
-------------------------

**[MacOS]** Install the `Homebrew package manager <https://brew.sh>`_
by following the instructions provided at the Homebrew website. We prefer to
use Homebrew since it allows packages to be installed and uninstalled without
superuser privileges.

After installing homebrew, open a terminal window and update your homebrew
installation with:
::
   brew update
   brew upgrade

Next, use homebrew to install the ``git`` version control system, the ``curl``
command line data transfer tool, and the ``wget`` file transfer tool with
these commands:
::
   brew install git curl wget

**[Ubuntu]** Update your system using the ``apt`` package manager with:
::
   sudo apt update
   sudo apt upgrade
   
Then use ``apt`` to install the three tools:
::
   sudo apt install git curl wget

**[All]** Solr requires the java runtime to be installed on your system. In a
terminal window run this command:
::
   java --version

If you see a message about the command ``java`` not being found, then you need
to install the java runtime. Please visit the
`Oracle Java download site <https://www.oracle.com/downloads/>`_ and
follow the instructions to download and install the latest version of the
Java runtime environment (JRE).
   
Next, visit the Conda website and install either the
`Anaconda <https://www.anaconda.com>`_ python distribution or its much smaller 
`Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_
cousin. Anaconda provides a full python-based numerical computing and machine
learning stack. Miniconda provides a minimal python installation. Both give
you the ``conda`` package manager, an essential tool for resolving labyrinthine
dependencies among python and non-python packages. The installation package and
instructions for both are provided at the Anaconda website. For these
instructions we will assume that you choose the smaller Miniconda distribution.

**Important: download the Miniconda installation package for the latest**
**python 3 release, not python 2.7.**

After installing Miniconda, update to the latest version of ``conda`` with:
::

   conda update -n base -c defaults conda


Clone the ClarityNLP GitHub Repository
--------------------------------------

Open a terminal window on your system and change directories to wherever you
want to install ClarityNLP. Create a new folder called ``ClarityNLPNative``,
to emphasize that it will hold a version of ClarityNLP configured for running
locally on your system without Docker or OAuth2. You can create this
folder, clone the repo, and initialize all submodules with these commands:
::
   cd /some/location/on/your/disk
   mkdir ClarityNLPNative
   cd ClarityNLPNative
   git clone https://github.com/ClarityNLP/ClarityNLP.git
   cd ClarityNLP

This command sequence will give you an up-to-date checkout of the master
branch of the main ClarityNLP project. It will also checkout the latest master
branch of all git submodules (additional code that ClarityNLP needs).

The master branch of the git repository holds the most stable and well-tested
version of ClarityNLP. If you instead want the latest development code, with
the caveat that it will be less mature than the code in the master branch,
checkout the ``develop`` branch of the repo with these additional commands:
::
   git checkout develop

After checking out your desired branch of the repository, change to the
``native_setup`` folder of the repo with:
::
   cd native_setup

   
Create the Conda Environment for ClarityNLP
-------------------------------------------

From the ``ClarityNLPNative/ClarityNLP/native_setup`` folder, create a
new conda managed environment with:
::
   conda create --name claritynlp python=3.6   
   conda activate claritynlp
   conda config --env --append channels conda-forge
   conda install --file conda_requirements.txt
   pip install -r conda_pip_requirements.txt

The conda version of ``pip`` knows about conda environments and will install
the packages listed in ``conda_pip_requirements.txt`` into the claritynlp
custom environment, NOT the system folders.

You can activate the claritynlp custom environment with the command
::

   conda activate claritynlp

Whenever the claritynlp environment is active, the command line in the
terminal window displays ``(claritynlp)`` to the left of the prompt. If the
default environment is active it will display ``(base)`` instead.

**Always activate the claritynlp environment whenever you want to do**
**anything with ClarityNLP from a terminal window.**

   
Install Additional Model Files
------------------------------

ClarityNLP uses the `spacy <https://spacy.io/>`_ and
`nltk <https://www.nltk.org/>`_ natural language processing
libraries, which require additional support files. From the same terminal
window in the ``native_setup`` folder, run these commands to install the
support files:
::
   conda activate claritynlp   # if not already active
   python -m spacy download en_core_web_sm
   python ../nlp/install_models.py

 
Setup MongoDB
-------------
  
ClarityNLP stores results in `MongoDB <https://www.mongodb.com/>`_. If you do
not have access to a hosted MongoDB installation, you will need to install it
on your system.

**[MacOS]** Use Homebrew to install MongoDB with:
::
   brew install mongodb-community@4.2

The ``@4.2`` in the installation command specifies the version of the
``mongodb-community`` software package, which is ``4.2`` as of this
writing. Check the MongoDB website for the latest version and use that if
you prefer.

After the installation finishes, run the command
``brew info mongodb-community``, which displays information about how to start
the MongoDB server. You can either configure the server to start automatically
each time your system reboots, or you can start the server manually. We will
assume manual startup, which can be accomplished by opening another terminal
window and running this command (assumes the default path to the mongo config
file):
::
   mongod --config /usr/local/etc/mongod.conf

After the server initializes it will deactivate the prompt in the terminal
window, indicating that it is running.

**[Ubuntu]** Use ``apt`` to install MongoDB with:
::
   sudo apt install mongodb

The installation process on Ubuntu should automatically start the MongoDB
server. Verify that it is active with:
::
   sudo systemctl status mongodb

You should see a message stating that the ``mongodb.service`` is active and
running. If it is not, start it with:
::
   sudo systemctl start mongodb

Then repeat the status check to verify that it is running.
   
**[All]** Now start up the Mongo **client** and find out if it can
communicate with the running MongoDB server. From a terminal window start the
MongoDB client by running ``mongo``. If the client launches successfully you
should see a ``>`` prompt. Enter ``show databases`` at the prompt and press
enter. The system should respond with at least the *admin* database. If you
see this your installation should be OK. You can stop the client by typing
``exit`` at the prompt.

If you have access to a hosted MongoDB instance, you will need to know the
hostname for your ``mongod`` server as well as the port number that it listens
on. If your hosted instance requires user accounts, you will also need to know
your username and password. These will be entered into the ``project.cfg``
file in a later step below.
   
  
Setup PostgreSQL
----------------

Now we need to install and configure PostgreSQL. ClarityNLP uses Postgres for
job control and for storing OMOP vocabulary and concept data.

**[MacOS]** Perhaps the easiest option for installing Postgres on MacOSX is to
download and install
`Postgres.app <https://postgresapp.com/>`_, which takes care of most of the
setup and configuration for you. If you do not have access to a hosted Postgres
server, download the .dmg file from the Postgres.app website, run the
installer, and click `initialize` to create a new server. 

After everything is installed and running, you will see an elephant icon in
the menu bar at the upper right corner of your screen. Click the icon and a
menu will appear. The button in the lower right corner of the menu can be used
to start and stop the database server. For now, click the button and stop the
server, since we need to make a small change to the postgres configuration
file.

**[Ubuntu]** Install postgres with:
::
   sudo apt install postgresql

The installation process should automatically start the postgres server, as it
did with the MongoDB installation. For now, stop the server with:
::
   sudo systemctl stop postgresql
   

Edit the PostgreSQL Config File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will need to follow these configuration steps as well if you have a
hosted Postgres instance. You may need to ask your local database admin to
perform the configuration, depending on whether or not you have superuser
privileges for your particular installation. The location of the data
directory on your hosted instance will likely differ from that provided below,
which is specific to a local installation.

**[MacOS]** With the Postgres server stopped, click the elephant icon, click
the ``Open Postgres`` menu item, and then click the ``Server Settings``
button on the dialog that appears. Note the location of the data directory,
which defaults to ``~/Library/Application Support/Postgres/var-11``. The
``postgresql.conf`` file is located in the data directory and contains various
important parameters that govern the operation of the database. We need to
edit one of those params to make the data ingest process run more smoothly.

**[Ubuntu]** The postgres config file for Postgres 10 is stored by default in
``/etc/postgresql/10/main/postgresql.conf``. If you installed Postgres 11 the
10 should be replaced by an 11. This file is owned by the special ``postgres``
user. To edit the file, switch to this user account with:
::
   sudo -i -u postgres
   whoami

The ``whoami`` command should display ``postgres``.

**[All]** Open a text editor, browse to the location indicated above and open
the file ``postgresql.conf``. Search the file for the entry ``max_wal_size``,
which governs the size of the write-ahead log (hence the WAL acronym). If the
entry happens to be commented out, uncomment it. Set its value to 30GB (if
the value is already greater than 30GB don't change it). By
doing this we prevent checkpoints from occurring too frequently and slowing
down the data ingest process. Save the file after editing.

**[Ubuntu]** Log out as the ``postgres`` user with:
::
   exit

Then restart the Postgres server with either:

**[MacOS]** Click on the elephant icon and press the start button.

**[Ubuntu]** Use ``systemctl`` to start it:
::
   sudo systemctl start postgresql

Create the Database and a User Account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the database server installed, configured, and running, we now need to
create a user account. Open a terminal and browse to
``ClarityNLPNative/ClarityNLP/utilities/nlp-postgres``. From this folder
run the command appropriate to your operating system to start ``psql``:

**[MacOS]**
::
   psql postgres

**[Ubuntu]**
::
   sudo -u postgres psql
   
Then run this command sequence (we suggest using a better password) to setup
the database:
::
   CREATE USER clarity_user WITH LOGIN PASSWORD 'password';
   CREATE DATABASE clarity;
   \connect clarity
   \i ddl/ddl.sql
   \i ddl/omop_vocab.sql
   \i ddl/omop_indexes.sql
   GRANT USAGE ON SCHEMA nlp TO clarity_user;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA nlp TO clarity_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA nlp TO clarity_user;

These commands create the database, setup the tables and indexes, and grant
the ``clarity_user`` sufficient privileges to use it with ClarityNLP.


Load OMOP Vocabulary Files
^^^^^^^^^^^^^^^^^^^^^^^^^^

**THIS STEP IS OPTIONAL.** The OMOP vocabulary and concept data is used
by the ClarityNLP synonym expansion macros. Synonym expansion is an optional
feature of ClarityNLP. If you are unfamiliar with OMOP or do not forsee a
need for such synonym expansion you can safely skip this step. The ingestion
process is time-consuming and could take from one to two hours or more,
depending on the speed of your system. If you only want to explore basic
features of ClarityNLP you do not need to load this data, and you can skip
ahead to the Solr setup instructions.

If you do choose to load the data, then keep your ``psql`` terminal window
open. **From a different terminal window** follow these steps to download and
prepare the data for ingest:
::
   cd /tmp
   mkdir vocabs
   cd vocabs
   wget http://healthnlp.gtri.gatech.edu/clarity-files/omop_vocabulary_set.zip
   unzip omop_vocabulary_set.zip
   rm omop_vocabulary_set.zip

You should see these files in ``/tmp/vocabs`` after unzipping:
::

   DOMAIN.csv
   CONCEPT_CLASS.csv
   CONCEPT.csv
   CONCEPT_ANCESTOR.csv
   RELATIONSHIP.csv
   CONCEPT_SYNONYM.csv
   VOCABULARY.csv
   CONCEPT_RELATIONSHIP.csv
   DRUG_STRENGTH.csv
   
Go back to your ``psql`` window and begin the process of loading data into the
database with:
::

   \i dml/copy_vocab.sql

As mentioned above, the loading process could take a **long** time, possibly
more than two hours, depending on the speed of your system. As the load
progresses, it should gradually generate the following output:
::
   SET
   COPY 2465049
   COPY 2781581
   COPY 23396378
   COPY 21912712
   COPY 3878286
   COPY 27
   COPY 446
   COPY 321
   COPY 40

Once you start the loading process, just let it run...it will eventually
finish. After loading completes, log out with the command
``\q``. You can close this window and the ``tmp/vocabs`` window.

Setup Solr
----------
ClarityNLP uses `Solr <http://lucene.apache.org/solr/>`_ as its document store.
If you do not have access to a hosted Solr instance you will need to install it
on your system.

**[MacOS]** Use Homebrew to install Solr with:
::
   brew install solr

When the installation finishes run the command ``brew info solr`` to learn
how to start Solr. You can either have it start on boot or on demand with the
command
::
   solr start

Start the solr server.
   
**[Ubuntu]** Ubuntu does not seem to provide a suitable apt package for Solr,
so you will need to download the Solr distribution from the Apache web site.
Open a web browser to the
`Solr download site <https://lucene.apache.org/solr/downloads.html>`_ and
download the binary release for the latest version of Solr 8. For now we will
assume that you download the 8.1.1 **binary** release, which is in the file
``solr-8.1.1.tgz``.

Open a terminal window and run these commands to unzip the distribution into
your home directory:
::
   cd ~
   mkdir solr
   tar -C solr -zxvf ~/Downloads/solr-8.1.1.tgz
   mv ~/solr/solr-8.1.1 ~/solr/8.1.1

Open a text editor and add this line to your ``.bashrc`` file, which places
the Solr binaries on your path:
::
   export PATH=~/solr/8.1.1/bin:$PATH

Close the text editor, exit the terminal window, and open a new terminal window
to update your path. Run ``which solr`` and verify that
``~/solr/8.1.1/bin/solr`` is found.

Start your Solr server by running:
::
   solr start
   
**[All]** After starting Solr, check to see that it is running by opening a
web browser to ``http://localhost:8983`` (or the appropriate URL for your
hosted instance). You should see the Solr admin dashboard. If you do, your
Solr installation is up and running.

We need to do some additional configuration of the Solr server and ingest
some test documents. We provide a python script to do this for you.
**This script assumes that you are running a recent version of Solr,**
**version 7 or later.** If you are running an older version this script
**will not work**, since some field type names changed at the
transition from Solr 6 to Solr 7.

Open a terminal window to ``ClarityNLPNative/ClarityNLP/native_setup``.
If you installed Solr on your local system run:
::
   conda activate claritynlp
   python ./configure_solr.py

If you use a hosted Solr instance, you should run these commands instead,
replacing the ``<hostname>`` and ``<port_number>`` placeholders with the values
for your hosted instance:
::
   conda activate claritynlp
   python ./configure_solr.py --hostname <hostname_string> --port <port_number>
   
This script creates a Solr core named ``claritynlp_test``, adds some custom
fields and types, and loads test documents contained in four ``.csv`` files.
You should confirm that the files ``sample.csv``, ``sample2.csv``,
``sample3.csv``, and ``sample4.csv`` were loaded successfully (load statements
appear in the console as the script runs). If the load failed for any reason
an error message will be written to stdout.

If the script ran without error, your ``claritynlp_test`` Solr core should
have ingested 7016 documents. Verify this by opening a web browser to
``http://localhost:8983``, or if you have a hosted Solr instance, to its admin
page. From the core selector at the left of the screen, select the
``claritynlp_test`` core and look in the ``Statistics`` window. The value of
the ``Num Docs`` field should equal 7016.

ClarityNLP expects the ingested documents to have a minimal set of fields, which
appear in the next table:

+-------------+--------------------------------------------------------------------+
| Field Name  | Description                                                        |
+=============+====================================================================+
| id          | a unique ID for this document                                      |
+-------------+--------------------------------------------------------------------+
| report_id   | a unique ID for this document (can use same value as ``id`` field) |
+-------------+--------------------------------------------------------------------+
| source      | the name of the document set, the name of your institution, etc.   |
+-------------+--------------------------------------------------------------------+
| subject     | a patient ID, drug name, or other identifier                       |
+-------------+--------------------------------------------------------------------+
| report_type | type of data in the document, i.e. ``discharge summary``,          |
|             | ``radiology``, etc.                                                |
+-------------+--------------------------------------------------------------------+
| report_date | timestamp in a format accepted by Solr:                            |
|             |                                                                    |
|             | - ``YYYY-MM-DDThh:mm:ssZ``                                         |
|             | - ``YYYY-MM-DDThh:mm:ss.fZ``                                       |
|             | - ``YYYY-MM-DDThh:mm:ss.ffZ``                                      |
|             | - ``YYYY-MM-DDThh:mm:ss.fffZ``                                     |
+-------------+--------------------------------------------------------------------+
| report_text | the actual text of the document, plain text                        |
+-------------+--------------------------------------------------------------------+

The test documents have all been configured with these fields. If you
decide to ingest additional documents into the ``claritynlp_test`` Solr core,
you will need to ensure that they contain these fields as well. Additional
information on document ingestion can be found
`here <https://clarity-nlp.readthedocs.io/en/latest/setup/ingest/generic_ingestion.html>`_.

Python scripts for ingesting some common document types can be found
`here <https://github.com/ClarityNLP/Utilities>`_.


Setup the Project Configuration File
------------------------------------

In the ``ClarityNLPNative/native_setup`` directory you will find a file named
``project.cfg``. This file gets loaded on startup and it configures Clarity to
run locally on your system.

If you plan to use hosted instances of either Solr, Postgres, or MongoDB, you
will need to edit the file and set the values appropriate for your system. The
file has a simple ``key=value`` format for each parameter. The Solr parameters
are located under the ``[solr]`` header, the Postgres params under the ``[pg]``
header, and the MongoDB params under the ``[mongo]`` header.

For instance, if you installed everything locally, but you changed the
PostgreSQL password above when you created the user account, you need to open
``project.cfg`` in a text editor, locate the ``[pg]`` section, find the
``password=password`` entry, and change the text on the right side of the
equals sign to the password that you used. If you used a password
of ``jx8#$04!Q%``, change the password line to ``password=jx8#$04!Q%``.

Make the appropriate changes for Solr, Postgres, and MongoDB to conform to
your desired configuration. Note that the username and password entries for
MongodB are commented out. It is possible to use MongoDB without having to
create a user account. If this is the case for your system, just leave these
entries commented out. Otherwise, uncomment them and set the values appropriate
for your system.

If you followed the instructions above *exactly* and installed everything
locally, you do not need to change anything in this file.

The provided ``project.cfg`` file tells ClarityNLP to use ``/tmp`` as the
location for the log file and various temporary files needed during the run. If
you want to put these files somewhere else, create the desired folders on your
system, make them writable, and set the paths in the ``[tmp]`` and ``[log]``
sections of ``project.cfg``. The paths would look like this after any changes:
::
   [tmp]
   dir=/path/to/my/preferred/tmp/dir

   [log]
   dir=/path/to/my/preferred/log/dir


**Double-check all entries in this file!** You will have problems getting the
system to run if you have typos or other errors for these parameters.
   
Once you are satisifed that the data in the file is correct, copy
``project.cfg`` from the ``native_setup`` folder into the ``nlp`` folder,
which is where ClarityNLP expects to find it:
::
   cp project.cfg ../nlp/project.cfg

   
Running Locally without Docker
------------------------------

Now we're finally ready to run. Here are the instructions for running a job
with your native ClarityNLP system. We open several terminal windows to
start the various servers and schedulers. You can reduce the number of windows
by configuring Mongo, Postgres, and Solr to start as background processes
after each reboot, as mentioned above.

1. Start Solr
^^^^^^^^^^^^^

If you installed Solr locally and chose the manual start method, start Solr by
opening a terminal window and running ``solr start``.

Verify that you can communicate with your Solr core by pinging it. For a local
installation, open a Web browser and visit this URL:
``http://localhost:8983/solr/claritynlp_test/admin/ping``. For a hosted
instance, change ``localhost`` to whatever is appropriate for your system.

The Web browser should display a status of ``OK`` in the final line of output
if it is connected. If you get an HTTP 404 error, make recheck your URL and
make sure that your Solr instance is actually running.


2. Start the MongoDB Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you installed MongoDB locally, launch the the ``mongod`` server with one
of these options:

**[MacOS]** Provide the path to your local MongoDB config file as follows
(this command uses the default location):
::
   mongod --config /usr/local/etc/mongod.conf

**[Ubuntu]**
::
   sudo systemctl start mongodb
   
Verify that the mongo server is running by typing ``mongo`` into a terminal to
start the mongo client. It should connect to the database and prompt for input.
Exit the client by typing ``exit`` in the terminal.

For a hosted MongoDB instance you need to supply the connection params from the
terminal. If your Mongo installation does not require accounts and passwords,
connect to it with this command, replacing the ``<hostname or ip>`` and
``<port number>`` placeholders with values appropriate for your system:
::
   mongo --host <hostname or ip> --port <port number>

If your hosted instance requires a user name and password, you will need to
supply those as well. More info on connecting to a remote Mongo server can
be found `here <https://docs.mongodb.com/manual/mongo/>`_.
   
3. Start the Postgres Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you installed Postgres locally:

**[MacOS]** Start the server by clicking the elephant icon in the
menu bar at the upper right corner of your screen. Press the start button at
the lower right of the popup menu. 

**[Ubuntu]** Start the server with:
::
   sudo systemctl start postgresql

Verify that your server is available by running the command ``pg_isready``
from a terminal window. It should report ``accepting connections``.   

If you use a hosted Postgres instance, check to see that it is up and running
with this command, replacing the hostname and port number with values suitable
for your installation:
::
   pg_isready -h <hostname> -p <port number>

If your Postgres server is running it should respond with
``accepting connections``.


4. Start the Luigi Task Scheduler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ClarityNLP uses Luigi to schedule and manage the data processing tasks. Luigi
must be started manually in a native setup.

We will run Luigi from a dedicated directory, ``~/tmp/luigi``. Open another
terminal window and create ``~/tmp/luigi`` with these commands (this only
needs to be done once):
::
   mkdir -p ~/tmp/luigi
   cd ~/tmp/luigi
   mkdir logs

Launch Luigi with:
::
   conda activate claritynlp
   cd ~/tmp/luigi
   luigid --pidfile pid --logdir logs --state-path statefile

Luigi should start and the command prompt should become inactive. Keep Luigi
running for your entire ClarityNLP session. You only need to start Luigi once,
even if you plan to run multiple ClarityNLP jobs.


5. Start the Flask Web Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ClarityNLP uses Flask as the underlying web framework. Flask must be
started manually in a native setup.

Open yet another terminal window, cd to the
``ClarityNLPNative/ClarityNLP/nlp`` directory, and launch the web server
with:
::
   conda activate claritynlp
   export FLASK_APP=api.py
   python -m flask run

Just like Luigi, the Flask web server only needs to be started once. The web
server prints startup information to the screen as it initializes.
You can safely ignore any ``No section:`` warnings. When initialization
completes you should see output similar to this:
::
   * Serving Flask app "nlp.api"
   * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

At this point ClarityNLP is fully initialized and waiting for commands.

6. Run a Validation Job
^^^^^^^^^^^^^^^^^^^^^^^

Open (yet another) terminal window and cd to
``ClarityNLPNative/ClarityNLP/native_setup``. Run the ``ls`` command
and note the file ``validation0.nlpql``. This is an NLPQL file that runs
several ClarityNLP tasks on a special validation document that was loaded into
the ``claritynlp_test`` Solr core during setup.

When we run this validation job, ClarityNLP will process the validation
document, run the validation tasks, and write results to MongoDB. We can
extract the results into a CSV file for easy viewing and then run a special
python script to check that the results are correct.

You launch a ClarityNLP job by performing an HTTP POST of your NLPQL file to
the ClarityNLP ``nlpql`` API endpoint. Since the local running instance of
ClarityNLP is listening at ``http://localhost:5000``, the appropriate URL
is ``http://localhost:5000/nlpql``.  We will see how to post the file using
the ``curl`` command line tool below. If you are familiar with
`Postman <https://www.getpostman.com/>`_ or other HTTP clients you could
certainly use those instead of ``curl``. Any HTTP client that can POST files
as plain text should be OK.

Before running the NLPQL file, we should first check it for syntax errors.
That can be accomplished by POSTing the NLPQL file to the ``nlpql_tester`` API
endpoint. From your terminal window run these commands to do so:
::
   conda activate claritynlp
   curl -i -X POST http://localhost:5000/nlpql_tester -H "Content-type:text/plain" --data-binary "@validation0.nlpql"

The curl command should generate output that looks similar to this:
::
   HTTP/1.0 200 OK
   Content-Type: text/html; charset=utf-8
   Content-Length: 2379
   Access-Control-Allow-Origin: *
   Server: Werkzeug/0.15.2 Python/3.6.6
   Date: Thu, 06 Jun 2019 00:37:26 GMT

   {
       "owner": "claritynlp",
        "name": "Validation 0",
        "population": "All",
        "context": "Patient",
        
        <lots of content omitted...>
        
        "debug": false,
        "limit": 100,
        "phenotype_id": 1
   }

This is the JSON representation of the NLPQL file generated by the ClarityNLP
front end. If you see JSON output similar to this your syntax is correct. If
you do not get JSON output then something is wrong with your NLPQL syntax.
There should be an error message printed in the Flask window. The
``validation0.nlpql`` file has been checked and should contain no syntax errors.

After the syntax check we're ready to run the job. POST the NLPQL file to the
``nlpql`` endpoint with this command:
::
   curl -i -X POST http://localhost:5000/nlpql -H "Content-type:text/plain" --data-binary "@validation0.nlpql"

The system should accept the job and print out a message stating where you can
download the results. The message should look similar to this:
::
   {
       "job_id": "1",
       "phenotype_id": "1",
       "phenotype_config": "http://localhost:5000/phenotype_id/1",
       "pipeline_ids": [
           1
       ],
       "pipeline_configs": [
           "http://localhost:5000/pipeline_id/1"
       ],
       "status_endpoint": "http://localhost:5000/status/1",
       "results_viewer": "?job=1",
       "luigi_task_monitoring": "http://localhost:8082/static/visualiser/index.html#search__search=job=1",
       "intermediate_results_csv": "http://localhost:5000/job_results/1/phenotype_intermediate",
       "main_results_csv": "http://localhost:5000/job_results/1/phenotype"
    }
   
The ``job_id`` increments each time you submit a new job. The system should
launch approximately 22 tasks to run the commands in this sample file.
If you open a web browser to the ``luigi_task_monitoring`` URL, you can watch
the tasks run to completion in the luigi task status display. Just refresh
the window periodically to update the task counts.

After the job finishes you can download a CSV file to see what ClarityNLP
found. The ``intermediate_results_csv`` file contains all of the raw data
values that the various tasks found.

To check the results, you need to generate a CSV file from the
intermediate data with a comma for the record delimiter, **not a tab**.
A tab character seems to be the default delimiter for Microsoft Excel.

Excel users can correct this as follows. Assuming that you have the
intermediate result file open in Excel, press the key combination
<COMMAND>-A. This should highlight the leftmost column of data in the
spreadsheet. After highlighting, click the ``Data`` menu item, then press the
``Text to Columns`` icon in the ribbon at the top. When the wizard dialog
appears, make sure the ``Delimited`` radio button is highlighted. Click
``Next``. For the delimters, make sure that ``Comma`` is checked and that
``Tab`` is unchecked. Then click the ``Finish`` button. The data should appear
neatly arranged into columns. Then click the ``File|Save As...`` menu item.
On the dialog that appears, set the ``File Format`` combo box selection to
``Comma Separated Values (.csv)``. Make sure that a ``.csv`` extension appears
in the ``Save As`` edit control at the top of the dialog. Give the file a new
name if you want (but with a ``.csv`` extension), then click the ``Save``
button.

Users of other spreadsheet software will need to consult the documentation on
how to save CSV files with a comma for the record separator.

With the file saved to disk in proper CSV format, run this command from the
``ClarityNLPNative/ClarityNLP/native_setup`` folder to check the values:
::
   conda activate claritynlp  # if not already active
   python ./validate_results0.py --file /path/to/your/csv/file.csv

This command runs a python script to check each result. If the script finds no
errors it will print ``All results are valid.`` to stdout. If ClarityNLP is
working properly no errors should be found.


Shutdown
--------

Perform these actions to completely shutdown ClarityNLP on your system:

1. Stop the Flask webserver by entering <CTRL>-C in the flask terminal window.
2. Stop the Luigi task scheduler by entering <CTRL>-C in the luigi terminal
   window.
3. MacOS users can stop the MongoDB database server by entering <CTRL>-C in
   the MongoDB terminal window. Ubuntu users can run the command
   ``sudo systemctl stop mongodb``.
4. Stop Solr by entering ``solr stop -all`` in a terminal window.
5. MacOS users can stop Postgres by first clicking on the elephant icon in
   the menu bar at the upper right corner of the screen. Click the stop
   button on the menu that appears. Ubuntu users can run the command
   ``sudo systemctl stop postgresql``.

Alternatively, you could just terminate Flask and Luigi and keep the other
servers running if you plan to run more jobs later.

If you restart, always start Luigi **before** Flask, exactly as documented
above.
   

Final Words
-----------
   
An introduction to NLPQL can be found
`here <https://claritynlp.readthedocs.io/en/latest/user_guide/index.html>`_.

Additional information on how to run jobs with ClarityNLP can be found in
our
`Cooking with Clarity <https://github.com/ClarityNLP/ClarityNLP/tree/master/notebooks/cooking>`_
sessions. These are `Jupyter <https://jupyter.org/>`_ notebooks presented in a
tutorial format. Simply click on any of the ``.ipynb`` files to open the
notebook in a Web browser. These notebooks provide in-depth explorations of
topics relevant to computational phenotyping.
