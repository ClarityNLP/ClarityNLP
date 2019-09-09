.. _termset:

termset
=======
ClarityNLP modules in NLPQL that define sets of terms.


Example:
~~~~~~~~

::

    termset EjectionFractionTerms: [
        "ejection fraction",
        "LVEF",
        "EF",
    ];

`termset` can now be passed as an argument to tasks. For example:

::

    define EjectionFractionFunction:
        Clarity.ValueExtraction({
            termset:[EjectionFractionTerms],
            documentset: [ProviderNotes],
            });

Note that `termset` is required in certain tasks such as :ref:`providerassertion` and :ref:`termfinder`.


Lexical Variants
----------------

As an optional step, NLPQL can be pre-processed with :ref:`lexical variants<lexicalvariantsalgo>`.
Learn more about how to use lexical variants :ref:`here<macros>`.
