Custom Local Setup
==================

Use this setup only when you are not using Docker, and just wish to run the main
NLP Flask API standalone. You might do this if you already have a Solr, Postgres
and MongoDB hosted elsewhere, or you don't want to host them locally.


Note: These instructions are only needed if you are not installing via Docker
(which is recommended). In that case, you can skip past this setup.

Installing Requirements
-----------------------

::
   
   pip3 install -r requirements.txt
   pip3 install -U pytest
   python3 -m spacy download en
   python3 -m spacy download en_core_web_md

If you want to use conda, you can setup the environment using `spec-file.txt`.

Install models:

::

  python3 install_models.py

Properties File
---------------
In the ``ClarityNLP/nlp`` directory, copy `example.cfg` to `project.cfg` and
update with your settings.
  
Vocabulary
----------
ClarityNLP can access OMOP vocabulary data in a local PostgreSQL database. To
setup the database, the vocabulary files must first be downloaded and unzipped,
then copied into the database.

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

Postgres
--------

To setup the Postgres database, first install postgresql if it is not already
installed on your system. Instructions for downloading and installing the
database can be found at the `PostgreSQL homepage <https://www.postgresql.org/>`_.

An important location for the postgres installation is the "data directory".
For purposes of this guide we will assume that it is located at ``usr/local/var/postgres``.
If that is NOT the location on your system, substitute the path to your
postgres data directory in the following instructions.

After installing the database, we need to shutdown the database server and edit
the postgres config file. Check to see if the postgres server is running by
opening a terminal and running the command ``pg_isready``.  If this command
reports ``accepting connections``, it means that the server is running and it
therefore needs to be stopped. Shutdown the server manually with this command:
::
    pg_ctl -D /usr/local/var/postgres stop

Verify that the server has been stopped by running ``pg_isready`` once again.
If the server has been stopped the command should report ``no response``.

Open a text editor, browse to the data directory, and open the file
``postgresql.conf``. Search the file for the entry ``max_wal_size``. If the
entry is commented out, uncomment it and set its value to at least 30GB. By
doing this we prevent checkpoints from occurring too frequently and slowing
down the data ingest process. Save the file after editing.

Restart the postgres server with this command:
::
    pg_ctl -D /usr/local/var/postgres start

Creating Accounts
^^^^^^^^^^^^^^^^^

With the database server installed, configured, and running, we now need to
create a user account. Open a terminal and browse to
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
   GRANT ALL PRIVILIGES ON DATABASE mimic_v5 to mimic_v5;
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

The data copying process could take a long time, possibly more than one
hour. As the copy progresses, it should generate the following output:
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

After the copy finishes, log out with the command ``\q``.

Update Property File
^^^^^^^^^^^^^^^^^^^^

Open the file ``ClarityNLP/nlp/project.cfg`` in a text editor. Search the file
for the ``[pg]`` section. Set the entries as follows:
::
   [pg]
   host=localhost
   dbname=mimic_v5
   user=mimic_v5
   password=i3lworks
   port=5432

Verify the value of the port by opening the postgres.conf file and searching for
the ``port`` entry. Set the port value above to match the port number in the
postgresql.conf file, even if the port entry in that file is commented out.

Solr
----
Install and configure Solr by following the instructions on the
Developer Guide/Technical Background/Solr page of this documentation.

Ingest Data
^^^^^^^^^^^
TBD

Map Fields
^^^^^^^^^^
The final task for configuring Solr is to setup a mapping of fields in your
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
   url=http://solr.hdap.gatech.edu:8983/solr/mimic
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

You can also use different locations for the temp and log directories if you
want.

Running Locally
---------------

Running the Luigi Central Scheduler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
``which luigi``.

Next, open a terminal and enter this command to launch Luigi. You can replace
the bracketed entries by ``pid``, ``logs``, and ``statefile`` if dedicated
directories for these do not exist:
::
   luigid --background --pidfile <PATH_TO_PIDFILE> --logdir <PATH_TO_LOGDIR> --state-path <PATH_TO_STATEFILE>

Running MongoDB
^^^^^^^^^^^^^^^

If you run MongoDB locally, start the ``mongod`` server by supplying the path
to your local config file as follows:
::
   mongod --config /path/to/mongod.conf

If you do not use a custom config file, omit the ``config`` argument.

Verify that the mongo server is running by typing ``mongo`` into a terminal to
start the mongo client. It should connect to the database and prompt for input.
Exit the client by typing ``quit()`` in the terminal.

Runnning Postgres
^^^^^^^^^^^^^^^^^

If your Postgres server is not already running, start it using the ``pg_ctl``
command above. Verify that your server is available by running ``pg_isready``.
It should report ``accepting connections``.

Ping Solr
^^^^^^^^^

Verify that you can communicate with your Solr instance by pinging it. Open a
Web browser and visit the URL formed by appending ``/admin/ping`` to your Solr
URL. For instance, using the example URL above, the ping URL would be:
``http://solr.hdap.gatech.edu:8983/solr/mimic/admin/ping``. The Web browser
should display a status of ``OK`` if it is connected. If you get an HTTP 404
error, then recheck your URL.


Run Flask app
^^^^^^^^^^^^^

ClarityNLP uses Flask as the underlying web framework. From the
``ClarityNLP/nlp`` directory, launch the web server as follows:
::
   export FLASK_APP=api.py
   python3 -m flask run

If you want to run Flask in development mode with an active debugger,
use this command sequence:
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

