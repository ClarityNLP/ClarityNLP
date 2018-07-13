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
Verb Form                    Example
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

ClarityNLP includes a pluralizer and a verb inflector that attempts to compute
the plurals and inflected forms of English words. The verb inflector ignores
archaic forms and focuses on contemporary American English.

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
Neither the NLTK Wordnet lemmatizer nor the Spacy lemmatizer worked reliably
enough on this module's test data to allow users to input verbs in arbitrary
inflections. Lemmatization is still an area of active NLP research, so these
results are not necessarily surprising.

Therefore, for all of these reasons, the ClarityNLP verb inflector requires
the input verb to be provided in base form.

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

If none of these tests have succeeded, the verb inflector then checks for
pronounciation-dependent spellings using the CMU pronouncing dictionary. If
the base form has a silent-e ending, the final ``e`` is dropped and ``ing`` is
appended to the base verb to form the result, unless the base form is a known
exception to this rule, in which case the final ``e`` is retained.

The verb inflector next checks for a pronunciation-dependent spelling caused by
consonant doubling. The rules for consonant doubling are presented in the next
section. The verb inflector doubles the final consonant if necessary, appends
``ing``, and returns that as the result.

If none of the tests succeeds, the verb inflector appends ``ing`` to the base
form and returns that as the result.

Algorithm for Consonant Doubling
--------------------------------



References
==========

.. [1] http://users.monash.edu/~damian/papers/extabs/Plurals.html

.. [2] https://en.wikipedia.org/wiki/English_verbs

.. [3] http://www.speech.cs.cmu.edu/cgi-bin/cmudict

.. [4] https://en.wikipedia.org/wiki/ARPABET

