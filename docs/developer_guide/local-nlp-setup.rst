Custom Local Setup
==================

This page provides instructions on how to run ClarityNLP locally on your
machine **without** having to use Docker. It is much simpler to use Docker,
since everything is provided and configured for you. But if you want more
control over your ClarityNLP installation and prefer to configure everything
yourself, then these are the instructions you need.

For now, we will assume that you want to install and run everything on
a Mac laptop (we use Macs for development).

Prerequisites
-------------

First of all, install the `Homebrew package manager <https://brew.sh>`_
by following the instructions provided at the Homebrew website. We like to use
Homebrew since it does not require sudo privileges to install or remove
packages.

Next install the latest stable version of python3. There are several options
for installing python3. One option is to install it with Homebrew by running
the command ``brew install python3``.

Another option, the one we recommend if your system has the required disk space,
is to install the `Anaconda <https://www.anaconda.com>`_ python distribution,
which gives you numpy, scipy, matplotlib, and a full python-based numerical
computing and machine learning stack. The installation package and instructions
are provided at the Anaconda website. Important: make sure you download the
installation package for the latest python3 release, **not** python 2.7.


Installing Additional Python Requirements
-----------------------------------------

After installing Homebrew and python3, open a terminal window and change
directories to the ``ClarityNLP/nlp`` folder. Run these commands to install
additional python packages required by ClarityNLP:
::
   
   pip3 install -r requirements.txt
   pip3 install -U pytest
   python3 -m spacy download en
   python3 -m spacy download en_core_web_md

Next, install some additional model files required by the Natural Language
Toolkit (nltk):
::

  python3 install_models.py

  
Project Properties File
-----------------------
In the ``ClarityNLP/nlp`` directory, copy ``example.cfg`` to ``project.cfg``.
We will update the different settings in this file as we proceed.
  
MongoDB
-------
  
ClarityNLP writes results to `MongoDB <https://www.mongodb.com/>`_, so you need a MongoDB server running on
your system. Use Homebrew to install MongoDB with this command:
::
   brew install mongodb

After the installation finishes, run the command ``brew info mongodb``. This
will display information about how to start the MongoDB server. You can either
configure the server to start automatically each time your system reboots, or
you can start the server manually. We will assume manual startup, which can be
accomplished by opening another terminal window and running this command (which
assumes the default path to the mongo config file):
::
   mongod --config /usr/local/etc/mongod.conf

From a **different** terminal window, start the MongoDB client by running
``mongo``. If the client launches successfully you should see a ``>`` prompt.
Enter ``show databases`` at the prompt and press enter. The system should
respond with at least the *admin* and *test* databases. If you see this your
installation should be OK. You can stop the client by typing ``exit`` at the
prompt. Stop the mongo server by running <CTRL>-C in the server window.

MongoDB listens by default on port 27017, which is what we assume in these
instructions. Make sure your ``project.cfg`` file contains the following
entries in the ``[mongo]`` section:
::
   [mongo]
   host=localhost
   port=27017
   db=nlp
   working_index=job_id
   working_collection=pipeline_temp

  
OMOP Vocabulary Files
---------------------

ClarityNLP accesses OMOP vocabulary data in a local PostgreSQL database. To
setup the database, the vocabulary files must first be downloaded and unzipped,
then imported into the database.

Follow these steps to download and unzip the vocabulary data. The zip file is
approximately 0.5 GB in size and will take some time to download.

::

   cd /tmp
   mkdir vocabs
   cd vocabs
   wget http://healthnlp.gtri.gatech.edu/clarity-files/omop_vocabulary_set.zip
   unzip omop_vocabulary_set.zip
   rm omop_vocabulary_set.zip

You should see the following files after unzipping:
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

PostgreSQL
----------

Now we need to install and configure PostgreSQL. Perhaps the easiest option
for MacOSX is to download and install
`Postgres.app <https://postgresapp.com/>`_, which takes care of most of the
setup and configuration for you. Download the .dmg file from the Postgres.app
website, run the installer, and click `initialize` to create a new server.

After everything is installed and running, you will see an elephant icon in
the menu bar at the upper right portion of your screen. Click the icon and a
menu will appear. The button in the lower right corner can be used to start
and stop the database server. For now, click the button and stop the server.

Edit the PostgreSQL Config File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Click the elephant icon, click the ``Open Postgres`` menu item, and then click
the ``Server Settings`` button on the dialog that appears. Note the location of
the data directory, which defaults to
``~/Library/Application Support/Postgres/var-11``. The ``postgresql.conf``
file is located in the data directory and contains various important parameters
that govern the operation of the database. We need to edit one of these params
to make the data ingest process run more smoothly.

Open a text editor, browse to the data directory, and open the file
``postgresql.conf``. Search the file for the entry ``max_wal_size``, which
governs the size of the write-ahead log (hence the WAL acronym). If the
entry is commented out, uncomment it and set its value to 30GB. By doing this
we prevent checkpoints from occurring too frequently and slowing down the data
ingest process. Save the file after editing.

Then restart the server by clicking on the elephant icon and pressing the
start button.

Creating Accounts
^^^^^^^^^^^^^^^^^

With the database server installed, configured, and running, we now need to
create a user account. Open a terminal and browse to this location in your
local copy of the ClarityNLP git repo:
``ClarityNLP/utilities/nlp-postgres``. From this location run the following
commands:
::
   psql postgres
   CREATE ROLE mimic_v5 with LOGIN PASSWORD 'i3lworks';
   ALTER ROLE mimic_v5 CREATEDB;
   \q

These commands create a user called ``mimic_v5`` and give that user the
ability to create databases. Next, we will log in as the mimic_v5 user and
run these commands to setup the database:
::
   psql postgres -U mimic_v5
   CREATE DATABASE mimic_v5;
   GRANT ALL PRIVILEGES ON DATABASE mimic_v5 to mimic_v5;
   \connect mimic_v5
   \i ddl/ddl.sql
   \i ddl/omop_vocab.sql
   \i ddl/omop_indexes.sql
   \q

These commands create the database, grant the mimic_v5 user sufficient
privileges to set it up, and run the SQL commands in three files.

Next, log in as a superuser (needed to copy the data) and start loading
data into the database:
::
   psql postgres
   \connect mimic_v5
   \i dml/copy_vocab.sql

The data copying process could take a long time, possibly more than one hour,
depending on the speed of your system. As the copy progresses, it should
generate the following output:
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

After the copying process finishes, log out with the command ``\q``.

Update Config Settings
^^^^^^^^^^^^^^^^^^^^^^

After completing all of these steps, open your ``project.cfg`` file again and
update the settings to match your system. If you have followed the instructions
as given, your ``[pg]`` section should look like this:
::
   [pg]
   host=localhost
   dbname=mimic_v5
   user=mimic_v5
   password=i3lworks
   port=5432

Double-check the port number on your system by clicking on the elephant icon
and selecting the ``Open Postgres`` menu item. You should see a database icon
for the mimic_v5 database that you just configured. Click the icon so that it
gets surrounded by the highlight square, then click the ``Server Settings...``
button above it. Note the port number, and, if necessary, change the value in
your project.cfg file to match it.
   

Solr
----
ClarityNLP uses `Solr <http://lucene.apache.org/solr/>`_ as its document store.
Install Solr with Homebrew by running this command:
::
   brew install solr

After the installation finishes, run the command ``brew info solr`` to see how
to start Solr. You can either have it start on boot or on demand with the
command
::
   solr start

After starting Solr, follow the instructions at 
`Custom Solr Setup <https://clarity-nlp.readthedocs.io/en/latest/developer_guide/technical_background/solr.html>`_
for configuring various field types required by ClarityNLP.


Map Fields
^^^^^^^^^^
The next task for configuring Solr is to setup a mapping of fields in your
data set to the fields that ClarityNLP expects. The minimal set of fields
required by ClarityNLP is:

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

The data fields in your documents can be mapped to this set of fields in the
``project.cfg`` file. Open the file and find the ``[solr]`` section, which
should have these entries:
::
   [solr]
   url=http://localhost:8983/solr/mimic
   text_field=report_text
   id_field=id
   report_id_field=report_id
   source_field=source
   date_field=report_date
   subject_field=subject
   type_field=report_type

Set the ``url`` field to that of your solr instance. The active core should be
the final component of the path.

Next, for each field type set its value to match the name of the corresponding
field in your documents. If your Solr instance stores the actual report text
in a field called ``document_text``, then you would use this line for the
first field assignment: ``text_field=document_text``.  For each of the
remaining fields, assign the name of the closest matching field in your
document set. It is important that each field be mapped.


Ingest Data
^^^^^^^^^^^

Follow the instructions for ingesting documents `here <https://clarity-nlp.readthedocs.io/en/latest/setup/ingest/generic_ingestion.html>`_.

Python scripts for ingesting some common document types can be found
`here <https://github.com/ClarityNLP/Utilities>`_.


Temp and Log Directories
------------------------
Setup a temporary directory on your system, make sure that it is writable by
the user running ClarityNLP, and set the value in the ``[tmp]`` and ``[log]``
sections of the ``project.cfg`` file. For instance, if you want the tmp dir
to be ``/tmp``, you would set the values in ``project.cfg`` to be:
::
   [tmp]
   dir=/tmp

   [log]
   dir=/tmp


Running Locally
---------------

1. Start the MongoDB Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Launch the the ``mongod`` server by supplying the path to your local config
file as follows (this command uses the default config file):
::
   mongod --config /usr/local/etc/mongod.conf

Verify that the mongo server is running by typing ``mongo`` into a terminal to
start the mongo client. It should connect to the database and prompt for input.
Exit the client by typing ``exit`` in the terminal.


2. Start the Luigi Central Scheduler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ClarityNLP uses Luigi to schedule and manage the data processing tasks. Luigi
must be manually started each time you run.

To configure Luigi, open the ``project.cfg`` file and find the ``[luigi]``
section. Set the values as follows:
::
   [luigi]
   home=/path/to/luigi
   scheduler=http://localhost:8082
   workers=1
   url=http://localhost:8082

Make sure that the ``home`` entry is set to the location of the luigi binary on
your system. On a Linux or Mac system, you can find this path by running
``which luigi``. If you installed the Anaconda python3 distribution, this path
should be ``/anaconda3/bin/luigi``.

We will run Luigi from a dedicated directory. Open a terminal window and create
it with these commands:
::
   cd ~/tmp
   mkdir luigi
   cd luigi

Enter the next command to launch Luigi:
::
   luigid --pidfile pid --logdir logs --state-path statefile

Luigi should start and the command prompt should become inactive.

You can stop Luigi by entering <CTRL>-C in this window.


3. Start the Postgres Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your Postgres server is not already running, start it by clicking the
elephant icon and pressing the start button at the lower right of the popup
menu. Open another terminal and verify that your server is available by
running ``pg_isready``. It should report ``accepting connections``.


4. Ping Solr
^^^^^^^^^^^^

Verify that you can communicate with your Solr instance by pinging it. Open a
Web browser and visit the URL formed by appending ``/admin/ping`` to your Solr
URL. For instance, using the example URL above, the ping URL would be:
``http://localhost:8983/solr/mimic/admin/ping``. The Web browser should display
a status of ``OK`` if it is connected. If you get an HTTP 404 error, recheck
your URL.


5. Start the ClarityNLP Flask Webserver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ClarityNLP uses Flask as the underlying web framework. From the
``ClarityNLP/nlp`` directory, launch the web server as follows:
::
   export FLASK_APP=api.py
   python3 -m flask run

If you want to run Flask in development mode with an active debugger,
use this command sequence instead:
::
   export FLASK_APP=api.py
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   python3 -m flask run

The default value of ``FLASK_ENV`` is ``production``. The allowed values
for ``FLASK_DEBUG`` are ``1`` (enable) and ``0`` (disable).

The web server prints startup information to the screen as it initializes.
When initialization is complete you should see output similar to this:
::
   * Serving Flask app "nlp.api"
   * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

At this point ClarityNLP is fully initialized and waiting for commands.

Detailed instructions on how to run jobs with ClarityNLP can be found in
our `Cooking with Clarity <https://github.com/ClarityNLP/ClarityNLP/tree/master/notebooks/cooking>`_
sessions. These are `Jupyter <https://jupyter.org/>`_ notebooks presented in a
tutorial format. Simply click on any of the ``.ipynb`` files to open the
notebook in a Web browser. These notebooks provide in-depth explorations of
topics relevant to computational phenotyping.
