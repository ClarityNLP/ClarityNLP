Section Tagging
***************

Overview
========

The section tagger ingests clinical documents and uses textual clues to
partition the documents into sections. Sections consist of groups of
sentences sharing a common purpose such as "History of Present Illness",
"Medications", or "Discharge Instructions". Effective section tagging 
reduces the amount of text that must be processed to perform a given task.
This document describes the Clarity section tagger and how it works.

The starting point for the section tagger is the open-source SecTag database
of Denny and colleagues [1]_.

Source Code
===========

The source code for the section tagger is located in ``nlp/sec_tag``.
The file ``sec_tag_db_extract.py`` extracts data from the SecTag database,
builds the SecTag concept graph (``concept_graph.py``), and generates data
files required by the section tagger for its operation. These files are written
to the ``data`` folder. The file ``section_tagger.py`` contains the code for
the section tagger itself.

The section tagger can also run interactively from a command line and process
a file of health records in JSON format. The file ``sec_tag_file.py`` provides
a command-line interface to the section tagger. Help can be obtained by running
the file with this command:  ``python3 ./sec_tag_file.py``. This interactive
appliation writes results (input file with tag annotations) to stdout.

SecTag Database
---------------

The section tagger requires two input files for its operation, both of which
can be found in the ``nlp/sec_tag/data`` folder. These files are
``concepts_and_synonyms.txt``, a list of clinical concepts and associated
synonyms, and ``graph.txt``, a list of graph vertices and associated codes
for the concept graph.

Generation of these files requires population of the SecTag database. The
SecTag SQL files were originally written for MySQL, so that database server
will be assumed here.

Install MySQL and create a root account. Start the MySQL server, log in as
root and enter these commands:

.. code-block:: sql
    :linenos:

       CREATE USER 'sectag'@'localhost' IDENTIFIED BY 'sectag';
       CREATE DATABASE SecTag_Terminology;
       GRANT ALL ON SecTag_Terminology.* TO 'sectag'@'localhost';
       GRANT FILE ON *.* TO 'sectag'@'localhost';


After running these commands, log out as the MySQL root user.
       
Next, download the sec_tag.zip file from Joshua Denny's website at Vanderbilt
using the link in [1]_. Unzip the file and find ``SecTag_Terminology.sql``.

Populate the database as the sectag user with this command, entering the
password 'sectag' when prompted:

    ``mysql -p -u sectag SecTag_Terminology < SecTag_Terminology.sql``

Concepts and Synonyms
---------------------

The section tagger operates by recognizing keywords that happen to be synonyms
for an underlying set of concepts. The synonyms in the text are converted to
the underlying concepts and the document sections tagged with the concepts. The
SecTag database provides the list of concepts and an initial set of synonyms.
To illustrate, concept 158 ``history_present_illness`` has synonyms
``indication, clinical indication, clinical presentation, history``, among
others.  Basically the synonyms represent the various forms in which the
concept could appear in a clinical note.

The code in ``sec_tag_db_extract.py`` extracts the concepts and synonyms from
the SecTag database; adds new synonyms to the list; adds a few new concepts;
corrects various errors occurring in the SecTag database, and writes output to
the ``nlp/sec_tag/data`` folder. Run the extraction code with this command:

    ``python3 ./sec_tag_db_extract.py``

Each concept has a "treecode", which is a string consisting of integers
separated by periods, such as ``6.41.149.234.160.165``, the treecode for the
concept ``chest_xray``. The numbers encode a path through the
concept graph from a small set of general concepts to a much larger number of
specific concept leaf nodes. The code 6 represents the concept
"objective_data". The code 6.41 represents the concept
"laboratory_and_radiology_data", which is more specific than "objective_data".
The code 6.41.149 represents the concept "radiographic_studies", which is even
more specific. The concepts become more specific as the code strings increase
in length. Each node in the concept graph has a unique code that represents a
unique path from the highest-level concepts to it.
    
As for errors in the SecTag database, two concepts are misspelled. These are
concept 127, ``principal_diagnosis``, misspelled as ``principle_diagnosis``,
and concept 695, ``level_of_consciousness``, misspelled as
``level_of_cousciousness``. Clarity's db extraction code corrects both of these
misspellings.

Concept 308, ``sleep_habits``, has ``sleep_habits,_sleep`` for the concept
text. The extraction program converts this to ``sleep_habits``.

Concept 2921, ``preoperative_medications`` is missing a treecode. A closely
related concept, number 441 ``postoperative_medications`` has treecode
``5.37.106.127`` and no children. This concept hierarchy resolves to:

|    ``patient_history:          5``
|    ``medications:              5.37``
|    ``medications_by_situation: 5.37.106``
|    ``preoperative_medications: 5.37.106.127``

The extraction program assigns the treecode ``5.37.106.500`` to the concept
``preoperative_medications``.

The final error that the extraction program corrects is for concept 745,
'appearance'.  This entry has an invalid treecode and is an isolated concept
at level 10. This strange entry is skipped entirely and is not written to the
output files.

Each synonym has a unique integer identifier. The values of these identifiers
are less than 6000. The new synonyms added by the extraction program begin
numbering at 6000.

The concepts added by Clarity are:

================================ ===========================
Concept Name                     Treecode
================================ ===========================
renal_course                     5.32.77.79.18.500
preoperative_medications         5.37.106.500
nasopharynx_exam                 6.40.139.191.120.500
hypopharynx_exam                 6.40.139.191.120.501
xray_ankle                       6.41.149.234.160.167.92.500
computed_tomography              6.41.149.234.162.500
cerebral_ct                      6.41.149.234.162.500.1
thoracic_ct                      6.41.149.234.162.500.2
abdominal_ct                     6.41.149.234.162.500.3
renal_and_adrenal_ct             6.41.149.234.162.500.4
extremities_ct                   6.41.149.234.162.500.5
nonradiographic_studies          6.41.500
types_of_nonradiographic_studies 6.41.500.1
nonradiographic_contrast_studies 6.41.500.1.1
magnetic_resonance_imaging       6.41.500.1.1.1
cerebral_mri                     6.41.500.1.1.1.1
thoracic_mri                     6.41.500.1.1.1.2
abdominal_mri                    6.41.500.1.1.1.3
renal_and_adrenal_mri            6.41.500.1.1.1.4
extremities_mri                  6.41.500.1.1.1.5
magnetic_resonance_angiography   6.41.500.1.1.2
cerebral_mra                     6.41.500.1.1.2.1
thoracic_mra                     6.41.500.1.1.2.2
abdominal_mra                    6.41.500.1.1.2.3
renal_and_adrenal_mra            6.41.500.1.1.2.4
extremities_mra                  6.41.500.1.1.2.5
================================ ===========================

Algorithm
=========


References
==========

.. [1] | J. Denny, A. Spickard, K. Johnson, N. Peterson, J. Peterson, R. Miller
       | **Evaluation of a Method to Identify and Categorize Section Headers**
       | **in Clinical Documents**
       | *J Am Med Inform Assoc.* 16:806-815, 2009.
       | https://www.vumc.org/cpm/sectag-tagging-clinical-note-section-headers
