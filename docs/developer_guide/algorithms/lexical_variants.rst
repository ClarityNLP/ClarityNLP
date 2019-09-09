.. _lexicalvariantsalgo:

Lexical Variants
****************

Overview
========

ClarityNLP uses the term *lexical variants* to mean either *plurals*,
*verb inflections*, or both. Pluralization is a familiar concept and is assumed
to be self-explanatory. English verbs have four inflected forms (i.e. a
different ending depending on use), which are as follows, using the verb
'walk' as an example:

===========================  ==============
Description                  Inflected Form
===========================  ==============
bare infinitive (base form)  walk
3rd person singular present  walks
present participle           walking
past tense (preterite)       walked
past participle              walked
===========================  ==============

*Regular* English verbs have inflected forms that can be computed from
relatively straightforward rules (but there are many exceptions). *Irregular*
verbs have inflected forms for the past tense and/or past participle that
violate the rules.

ClarityNLP includes a pluralizer and a verb inflector that attempt to compute
the plurals and inflected forms of English words. The verb inflector ignores
archaic forms and focuses primarily on contemporary American English.

Plurals
=======

The ClarityNLP pluralizer generates plural forms of words and phrases. Several
functions are offered depending on whether the part of speech of the term to
be pluralized is known. The source code for the pluralizer can be found in
``nlp/algorithms/vocabulary/pluralize.py``. The pluralizer is mainly a wrapper
around the Python port of Damian Conway's well-known ``inflect`` module [1]_.
An error-correction mechanism has also been incorporated to improve the module's
performance on medical text.

Inputs
------

A single string, representing the word or phrase to be pluralized.

Outputs
-------

A list of strings containing all known plural forms for the input.

Functions
---------

The functions provided by the ``pluralize`` module are (all arguments are
strings):
::

   plural_noun(noun)
   plural_verb(verb)
   plural_adj(adjective)
   plural(text_string)

Use the more specific functions if the part of speech of the input text is
known. Use ``plural`` if nothing is known about the text.

.. _verb_inflections:

Verb Inflections
================

The verb inflector module computes verb inflections from a given verb in base
form. The base form of a verb is also known as "plain form", "dictionary form",
"bare infinitive form", or as the "principal part" of the verb. Here is a list
of some common verbs and their base forms:

======== ==========
Verb     Base Form
======== ==========
running  run
walks    walk
eaten    eat
were     be
======== ==========

It is not possible to unambiguously compute the base form of a verb from an
arbitrary inflected form. Observe:

=====  ==================================================================
Verb   Possible Base Forms
=====  ==================================================================
clad   clad (to cover with material), clothe (to cover with clothes)
cleft  cleave (to split), cleft (to separate important parts of a clause)
fell   fell (to make something fall), fall (to take a tumble)
lay    lay (to set down), lie (to rest on a surface)
=====  ==================================================================

The only way to *unambiguously* recover the base form from an arbitrary
inflection is to supply additional information such as meaning, pronounciation,
or usage.

Lemmatizers attempt to solve this problem, but with decidedly mixed results.
Neither the NLTK WordNet lemmatizer nor the Spacy lemmatizer worked reliably
enough on this module's test data to allow users to input verbs in arbitrary
inflections. Lemmatization is still an area of active NLP research, so these
results are not necessarily surprising.

Therefore, for all of these reasons, **the ClarityNLP verb inflector requires
the input verb to be provided in base form**.

Source Code
===========

The source code for the verb inflector is located in
``nlp/algorithms/vocabulary/verb_inflector.py``. Supporting files in the same
directory are ``inflection_truth_data.txt``, ``irregular_verbs.py``, and the
files in the ``verb_scraper`` directory. The purpose of the supporting files
and software will be described below.

Inputs
------

The entry point to the verb inflector is the ``get_inflections`` function,
which takes a single string as input. The string is a **verb in base form** as
described above.

Outputs
-------

The ``get_inflections`` function returns all inflections for the verb whose
base form is given. The inflections are returned as a five-element list,
interpreted as follows:

=======  ==========================================
Element  Interpretation
=======  ==========================================
0        [string] the base form of the verb
1        [list] third-person singular present forms
2        [list] present participle forms
3        [list] simple past tense (preterite) forms
4        [list] past participle forms
=======  ==========================================

The lists returned in components 1-4 are all lists of strings. Even if only
a single variant exists for one of these components, it is still returned
as a single-element list, for consistency.

Example
-------

.. code-block:: python
   :linenos:

   inflections = verb_inflector.get_inflections('outdo')
   # returns ['outdo',['outdoes'],['outdoing'],['outdid'],['outdone']]

   inflections = verb_inflector.get_inflections('be')
   # returns ['be',['is'],['being'],['was','were'],['been']]


Algorithms
==========

The verb inflector uses different algorithms for the various inflections. A
high-level overview of each algorithm will be presented next. The verb
inflector uses a list of 558 irregular verb preterite and past participle
forms scraped from Wikipedia and Wiktionary to support its operations.

It should be stated that the rules below have been gleaned from various
grammar sources scattered about the Internet. Some grammar sites present
subsets of these rules; others present some rules without mentioning
any exceptions; and other sites simply present incorrect information. We
developed these algorithms iteratively, over a period of time, adjusting for
exceptions and violations as we found them. This is still a work in progress.


Algorithm for the Third-Person Singular Present
----------------------------------------------

The third-person singular present can be formed for most verbs, either regular
or irregular, by simply adding an ``s`` character to the end. Some highly
irregular verbs such as ``be`` and a few others are stored in a list
of exceptions. If the base form of the verb appears in the exception list,
the verb inflector performs a simple lookup and returns the result.

If the base form is not in the exception list, the verb inflector checks to
see if it ends in a consonant followed by ``y``. If so, the terminating ``y``
is changed to an ``i`` and an ``es`` is added, such as for the verb ``try``,
which has the third-person singular present form ``tries``.

If the base form instead ends in a consonant followed by ``o``, an ``es`` is
appended to form the result. An example of such a verb would be ``echo``, for
which the desired inflection is ``echoes``.

If the base form has neither of these endings, the verb inflector checks to
see if it ends in a sibilant sound. The sibilant sounds affect the spelling
of the third-person singular inflection in the presence of a silent-e ending [2]_.
The CMU pronouncing dictionary [3]_ is used to detect the presence of sibilant
sounds. The phonemes for these sounds are based on the ARPAbet [4]_ phonetic
transcription codes and appear in the next table:

================================  ========
Sibilant Sound                    Phoneme
================================  ========
voiceless alveolar sibilant       S
voiced alveolar sibilant          Z
voiceless postalveolar fricative  SH
voiced postalveolar fricitave     ZH
voiceless postalveolar affricate  CH
voiced postalveolar affricate     JH
================================  ========

If the base form ends in a sibilant sound and has no silent-e ending, an ``es``
is appended to form the desired inflection. Otherwise, an ``s`` is appended to
of the base form and returned as the result.

Algorithm for the Present Participle
------------------------------------

The verb inflector keeps a dictionary of known exceptions to the rules for
forming the present participle. Most of these exceptional verbs are either not
found in the CMU pronouncing dictionary, or are modal verbs, auxiliaries, or
other irregular forms. Some verbs also have multiple accepted spellings for the
present participle, so the verb inflector keeps a list of these as well. If the
base form of the given verb appears as an exception, a simple lookup is
performed to generate the result.

If the base form of the verb is not a known exception, the verb inflector
determines whether the base form ends in ``ie``. If it does, the ``ie`` is
changed to ``ying`` and appended to the base form to generate the result. An
example of such a verb is ``tie``, which has the form ``tying`` as the present
participle.

Next the verb inflector checks the base form for an ``ee``, ``oe``, or ``ye``
ending. If one of these endings is present, the final ``e`` is retained, and
``ing`` is appended to the base form and returned as the result.

If the base form ends in vowel-``l``, British spelling tends to double the final
``l`` before appending ``ing``, but American spelling does not. For many verbs both
the British and American spellings are common, so the verb inflector generates
both forms and returns them as the result. There appears to be one exception to
this rule, though. If the vowel preceding the final ``l`` is an ``i``, the rule
does not seem to apply (such as for the verb ``sail``, whose present participle
form is ``sailing``, not ``sailling``).

If none of these tests succeed, the verb inflector checks for pronounciation-
dependent spellings using the CMU pronouncing dictionary. If the base form has
a silent-e ending, the final ``e`` is dropped and ``ing`` is appended to the
base verb to form the result, unless the base form is a known exception to this
rule, in which case the final ``e`` is retained.

The verb inflector next checks for a pronunciation-dependent spelling caused by
consonant doubling. The rules for consonant doubling are presented in the next
section. The verb inflector doubles the final consonant if necessary, appends
``ing``, and returns that as the result.

If none of the tests succeeds, the verb inflector appends ``ing`` to the base
form and returns that as the result.

Algorithm for Consonant Doubling
--------------------------------

If the base form of the verb ends in ``c``, a ``k`` should generally be
appended prior to the inflection ending. There are a few exceptions to this
rule that the verb inflector checks for.

If the base form of the verb ends in two vowels followed by a consonant, the
rule is generally to not double the final consonant. One exception to this rule
is if the first vowel is a ``u`` preceded by ``q``. In this case the ``u`` is
pronounced like a ``w``, so the ``qu`` acts as if it were actually ``qw``. This
gives the word an effective consonant-vowel-consonant ending, in which case the
final consonant is doubled. An example of this would be the verb ``equip``,
which requires a doubled ``p`` for inflection (``equipping``, ``equipped``, etc.).

If the base form of the verb has a vowel-consonant ending, and if the consonant
is not a silent-t, then the final consonant is doubled for single syllable
verbs. If the final syllable is stressed, the final consonant is also doubled.
Otherwise the final consonant is not doubled prior to inflection.

Algorithm for the Simple Past Tense
-----------------------------------

If the verb is irregular, its past tense inflection cannot be predicted, so
the verb inflector simply looks up the past tense form in a dict and returns
the result. A lookup is also performed for a small list of regular verbs that
are either known exceptions to the rules, or which have multiple accepted
spellings for the past tense forms.

If the verb is regular and not in the list of exceptions, the verb inflector
checks the base form for an ``e`` ending. If the verb ends in ``e``, a ``d`` is
appended and returned as the result.

If the base form instead ends in a consonant followed by ``y``, the ``y`` is
changed to ``i`` and ``ed`` is appended and returned as the result.

If the base form ends in a vowel followed by ``l``, both the American and
British spellings are returned, as described above for the present participle.
The British spelling appends ``led`` to the base form, while the American
spelling only appends ``ed``.

If the final consonant requires doubling, the verb inflector appends the proper
consonant followed by ``ed`` and returns that as the result.

Otherwise, ``ed`` is appended to the base form and returned as the result.

Algorithm for the Past Participle
---------------------------------

The past participle for irregular verbs is obtained by simple lookup. The past
participle for a small number of regular verbs with multiple accepted
spellings is also obained via lookup. Otherwise, the past participle for
regular verbs is equivalent to the simple past tense form.

Testing the Verb Inflector
==========================

The file ``verb_inflector.py`` includes 114 test cases that can be run via
the ``--selftest`` command line option. A more extensive set of 1364 verbs
and all inflected forms can be found in the file ``inflection_truth_data.txt``.
This list consists of the unique verbs found in two sets: the set of irregular
English verbs scraped from Wikipedia [5]_, and the set of the 1000 most common
English verbs scraped from poetrysoup.com [6]_. The verb_inflector will read
the file, compute all inflections for each verb, and compare with the data
taken from the file using this command:
::
   python3 ./verb_inflector.py -f inflection_truth_data.txt

The code for scraping the verbs and generating the truth data file can be found
in the ``verb_scraper`` folder.

To generate the truth data file, change directories to the ``verb_scraper``
folder and run this command:
::
   python3 ./scrape_verbs.py

Two output files will be generated:

* ``verb_list.txt``, a list of the unique verbs found
* ``irregular_verbs.py``, data structures imported by the verb inflector

In addition to scraping verb data, this code also corrects for some
inconsistencies found between Wikipedia and the Wiktionary entries for each
verb.

Copy ``irregular_verbs.py`` to the folder that contains ``verb_inflector.py``,
which should be the parent of the ``verb_scraper`` folder.

Next, scrape the inflection truth data from Wiktionary for each verb in
``verb_list.txt``:
::
   python3 ./scrape_inflection_data.py

This code loads the verb list, constructs the Wiktionary URL for each verb in
the list, scrapes the inflection data, corrects further inconsistencies, and
writes the output file ``raw_inflection_data.txt``.  Progress updates appear
on the screen as the run progresses.

Finally, generate the truth data file with this command:
::
   python3 ./process_scraped_inflection_data.py


References
==========

.. [1] http://users.monash.edu/~damian/papers/extabs/Plurals.html
.. [2] https://en.wikipedia.org/wiki/English_verbs
.. [3] http://www.speech.cs.cmu.edu/cgi-bin/cmudict
.. [4] https://en.wikipedia.org/wiki/ARPABET
.. [5] https://en.wikipedia.org/wiki/List_of_English_irregular_verbs
.. [6] https://www.poetrysoup.com/common_words/common_verbs.aspx

       

