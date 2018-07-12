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
bare infinitive              walk
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



References
==========

.. [1] http://users.monash.edu/~damian/papers/extabs/Plurals.html
