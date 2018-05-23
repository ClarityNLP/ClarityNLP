Section Tagging
***************

Overview
========

The section tagger ingests clinical documents and uses textual clues to
partition the documents into sections. Sections consist of groups of
sentences sharing a common purpose such as "History of Present Illness",
"Medications", or "Discharge Instructions". Effective section tagging 
can reduce the amount of text to be processed for natural language
processing tasks. This document describes the Clarity section
tagger and how it works.

The starting point for the section tagger is the open-source SecTag database
of J. Denny and colleagues [1]_.

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
application writes results (input file with tag annotations) to stdout.

SecTag Database
---------------

The section tagger requires three input files for its operation, all of which
can be found in the ``nlp/sec_tag/data`` folder. These files are
``concepts_and_synonyms.txt``, a list of clinical concepts and associated
synonyms; ``graph.txt``, a list of graph vertices and associated codes
for the concept graph, and ``normalize.py``, which contains a map of
frequently-encountered synonyms and their "normalized" forms [2]_.

Generation of these files requires an installation of the SecTag database. The
SecTag SQL files were originally written for MySQL, so that database server
will be assumed here. These files do not need to be generated again unless
new concepts and/or synonyms are added to the SecTag database.

To populate the database, install MySQL and create a root account. Start the
MySQL server, log in as root and enter these commands, which creates a user
named "sectag" with a password of "sectag":

.. code-block:: sql
    :linenos:

       CREATE USER 'sectag'@'localhost' IDENTIFIED BY 'sectag';
       CREATE DATABASE SecTag_Terminology;
       GRANT ALL ON SecTag_Terminology.* TO 'sectag'@'localhost';
       GRANT FILE ON *.* TO 'sectag'@'localhost';

The user name and the password can be changed, but the database connection
string at the end of ``sec_tag_db_extract.py`` will need to be updated to
match.

After running these commands, log out as the MySQL root user.
       
Next, download the sec_tag.zip file from Joshua Denny's website at Vanderbilt
using the link in [1]_. Unzip the file and find ``SecTag_Terminology.sql``.

Populate the database as the sectag user with this command, entering the
password 'sectag' when prompted:

    ``mysql -p -u sectag SecTag_Terminology < SecTag_Terminology.sql``

The SecTag database name is "SecTag_Terminology". Additional information on
the contents of the database can be found in [1]_ and [2]_.

Concepts and Synonyms
---------------------

The section tagger operates by scanning the report text and recognizing
synonyms for an underlying set of concepts. The synonyms recognized in the text
are mapped to their associated concepts and the document sections are tagged
with the concepts. The SecTag database provides an initial set of concepts and
synonyms which Clarity expands upon.

For example, concept 158 "history_present_illness" has synonyms
"indication", "clinical indication", and "clinical presentation", among
others.  The synonyms represent the various orthographic forms by which the
concept could appear in a clinical note.

The code in ``sec_tag_db_extract.py`` extracts the concepts and synonyms from
the SecTag database; adds new synonyms to the list; adds a few new concepts;
corrects various errors occurring in the SecTag database, and writes output to
the ``nlp/sec_tag/data`` folder. Run the extraction code with this command:

    ``python3 ./sec_tag_db_extract.py``

Each concept has a "treecode", which is a string consisting of integers
separated by periods, such as ``6.41.149.234.160.165`` (the treecode for the
concept "chest_xray"). The numbers encode a path through the
concept graph from a small set of general concepts to a much larger set of
very specific leaf node concepts. The code 6 represents the concept
"objective_data", which is very general and broad in scope. The code 6.41
represents the concept "laboratory_and_radiology_data", which is a form of
"objective_data", but more specific. The code 6.41.149 represents the concept
"radiographic_studies", which is a more specific form of
"laboratory_and_radiology_data". The concepts increase in specificity as the
code strings increase in length. Each node in the concept graph has a unique
code that represents a path through the graph from the highest-level concepts
to it.

SecTag Errors
-------------

There are a few errors in the SecTag database. Two concepts are misspelled.
These are concept 127, "principal_diagnosis", misspelled as
"principle_diagnosis", and concept 695, "level_of_consciousness", misspelled as
"level_of_cousciousness". Clarity's db extraction code corrects both of these
misspellings.

Concept 308, "sleep_habits", has as concept text "sleep_habits,_sleep". The
extraction program converts this to just "sleep_habits".

Concept 2921, "preoperative_medications" is missing a treecode. A closely
related concept, number 441 "postoperative_medications" has treecode
``5.37.106.127`` and no children. This concept hierarchy resolves to:

|    ``patient_history:          5``
|    ``medications:              5.37``
|    ``medications_by_situation: 5.37.106``
|    ``preoperative_medications: 5.37.106.127``

The extraction program assigns the treecode ``5.37.106.500`` to the concept
"preoperative_medications".

The final error that the extraction program corrects is for concept 745,
'appearance'.  This entry has an invalid treecode and is an isolated concept
at level 10. This strange entry is skipped entirely and is not written to the
output files.

Each concept and synonym has a unique integer identifier. The values of these
identifiers are all less than 500 for concepts and 6000 for synonyms. The new
concepts added by the extraction program begin numbering at 500 and the new
synonyms at 6000.

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

Initialization and Sentence Tokenization
----------------------------------------

The section tagger begins its operation with an initialization phase in which
it loads the data files mentioned above and creates various data structures.
One data structure is a mapping of synonyms to concepts, used for fast text
lookups. This is a one-to-many mapping since a given synonym
can be associated with multiple concepts.

After initialization completes, the
section tagger reads the report text and runs the NLTK [3]_ sentence tokenizer
to partition the text into individual sentences. For narrative sections
of text the sentence tokenizer performs well. For sections of text containing
vital signs, lab results, and extensive numerical data the tokenizer
performance is substantially worse. Under these conditions a "sentence" often
comprises large chunks of report text spanning multiple sentences and sentence
fragments.

Synonym Matching
----------------

The section tagger scans each sentence and looks for strings indicating the
start of a new section. Clinical note sections tend to be delimited by one
or more keywords followed by a termination character. The terminator is
usually a colon ":", but dashes and double-dashes also appear as delimeters.
The section tagger employs various regular expressions that attempt to
match all of these possibilities. The winning match is the longest string of
characters among all matches. Any overlapping matches are merged, if possible,
prior to deciding the winning match. Each match represents the possible start
of a new report section.

For each match, the section tagger extracts the matching text and performs a
series of validity checks on it. Dash-terminated matches are checked to see
that they do not end in the middle of a hyphenated word. They are also checked
for lab results stated with a hyphen, such as ``SODIUM-135``, the serum sodium
level. Any such matches are discarded.

If any matches survive these checks, the terminating characters and possible
leading newlines are stripped from the matching text, and any bracketed data
(such as anonymized dates) is removed. The remaining text then gets converted
to lowercase and searched for concept synonyms and thus candidate headers.

The candidate header discovery processes proceeds first by trying an exact
match to the candidate text string. The text itself (after lowercasing) becomes
the lookup key for the synonym map built during initialization. If an exact
match is found, the associated concept(s) are looked up and inserted into the
list of candidate concepts for this portion of report text.

If the exact match fails, the section tagger splits the text into individual
words and tries to match the longest sequence of words, if any, to a known
synonym. It proceeds to do this by removing words from each end of the
word list. It first tries a match anchored to the right, removing words
one-by-one from the left. Any matches found are resolved into concepts and
added to the candidate concept list. If no matches are found, section tagger
tries again, this time with the matches anchored from the left, and words
removed one-by-one from the right. If still no matches are found, the word
list is pruned of stop words and the remaining words replaced by their
"normalized" forms. The sequence of match attempts repeats on this new word
list, first with an exact match, then one anchored right, then one anchored
left. If all of these match attempts fail, section tagger gives up and
concludes that the text does not represent the start of a new section. If at
least one match attempt succeeds, the synonyms are resolved into concepts via
map lookup and returned as candidate concepts for a new section label. If there
is only one candidate concept as the result of this process, that concept
becomes the header for the next section of text. If two or more candidate
concepts remain, the section tagger employs an ambiguity resolution process
to decide on the winning concept.

The Concept Stack
-----------------

The sections in a clinincal note tend to be arranged as flattened hierarchies
extending over several sections. For instance, in a discharge report one
might encounter a section labeled GENERAL_EXAM, followed by a section labeled
HEAD_AND_NECK_EXAM, which represents a more specific type of exam. This section
could be followed by a section labeled EYE_EXAM, which is an even more
specific type of exam. Although these sections would be listed sequentially in
the report, they naturally form a hierarchy of EXAMINATION concepts proceeding
from general to specific. Other section groups in the report exhibit the same
characteristics.

A data structure for managing hierarchies such as this is a stack. The section
tagger manages a "concept stack" as it processes the report text. It uses
the stack to identify these natural concept groups and to resolve ambiguities
as described in the previous section.

The specificity of a concept is determined by its graph treecode. The longer
the treecode, the more specific the concept. Two concepts with identical length
treecodes have the same degree of specificity.

Each time the section tagger recognizes a concept C it updates the stack
according to this set of empirically-determined rules:

Let T be the concept at the top of the stack.

* If C is a more specific concept than T, push C onto the stack.
  In other words keep pushing concepts as they get more specific.
* If C has the same specificity as T, pop T from the stack and push C.
* If C is more general than T, pop all concepts from the stack that have
  specificity >= C. In other words, pop all concepts more specific than C,
  since C could represent the start of a new concept hierarchy.

Thus the section tagger pushes concepts onto the stack as they get more
specific. It pops concepts from the stack if more specific than the most
recently recognized concept.

Concept Ambiguity Resolution
----------------------------


  
References
==========

.. [1] | J. Denny, A. Spickard, K. Johnson, N. Peterson, J. Peterson, R. Miller
       | **Evaluation of a Method to Identify and Categorize Section Headers**
       | **in Clinical Documents**
       | *J Am Med Inform Assoc.* 16:806-815, 2009.
       | https://www.vumc.org/cpm/sectag-tagging-clinical-note-section-headers

.. [2] | J. Denny, R. Miller, K. Johnson, A. Spickard
       | **Development and Evaluation of a Clinical Note Section Header Terminology**
       | *AMIA Annual Symposium Proceedings* 2008, Nov 6:156-160.

.. [3] | **Natural Language Toolkit**
       | https://www.nltk.org/

