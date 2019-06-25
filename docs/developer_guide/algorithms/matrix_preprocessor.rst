Term-Frequency Matrix Preprocessor
**********************************

Overview
========

`Term-frequency matrices` feature prominently in text processing and
topic modeling algorithms. In these problems one typically starts with
a set of documents and a list of words (the `dictionary`). A
term-frequency matrix is constructed from the dictionary and
the document set by counting the number of occurrences of each dictionary word
in each document. If the rows of the matrix index the words and the columns
index the documents, the matrix element at coordinates `(r, c)` represents
the number of occurrences of dictionary word `r` in document `c`. Thus each
entry of the matrix is either zero or a positive integer.

Construction of such a matrix is conceptually simple, but problems can arise if
the matrix contains duplicate rows or columns. The presence of duplicate
columns means that the documents at those indices are *identical*
with respect to the given dictionary. The linear algebra algorithms underlying
many text processing and information retrieval tasks can exhibit instability or
extremely slow convergence if duplicates are present. Mathematically, a
term-frequency matrix with duplicate columns has a rank that is numerically
less than the column count. Under such conditions it is advantageous to remove
the duplicated columns (and/or rows) and work with a smaller,
fuller-rank matrix.

The `ClarityNLP matrix preprocessor` is a command-line tool that scans a
term-frequency matrix looking for duplicate rows and columns. If it finds any
duplicates it prunes them and keeps only one row or column from each set of
duplicates. After pruning it scans the matrix again, since removal of rows or
columns could create further duplicates. This process of scanning and checking
for duplicates proceeds iteratively until either a stable matrix is achieved or
nothing is left (a rare occurrence, mainly for ill-posed problems). The
resulting matrix is written to disk, along with the surviving row and column
index lists.


Source Code
===========

The source code for the matrix preprocessor is located in
``nlp/algorithms/matrix_preprocessor``.  The code is written in C++ with a
python driver ``preprocess.py``.

Building the Code
-----------------

A C++ compiler is required to build the matrix preprocessor.

On Linux systems, use your package manager to install the ``build-essential``
package, which should contain the Gnu C++ compiler and other tools needed to
build C++ code. After installation, run the command ``g++ --version``, which
should print out the version string for the Gnu C++ compiler. If this command
produces a ``command not found`` error, then use your package manager to
explicitly install the ``g++`` package.

On MacOSX, install the xcode command-line tools with this command:
``xcode-select --install``. After installation run the command
``clang++ --version``, which should generate a version string for the clang
C++ compiler.

After verifying that the C++ compiler works, build the matrix preprocessor code
with these commands:
::
   cd nlp/algorithms/matrix_preprocessor
   make

The build process should run to completion with no errors, after which these
binaries should be present in the ``build/bin`` folder: ``libpreprocess.a``,
``preprocessor``, and ``test_preprocessor``.


Inputs
======

The matrix preprocessor requires a single input file. The input file must be
in MatrixMarket_ format, a popular and efficient format for
sparse matrices.

.. _MatrixMarket: https://math.nist.gov/MatrixMarket/

Python supports the MatrixMarket format via the ``scipy`` module and the
functions ``scipy.io.mmwrite`` and ``scipy.io.mmread``.

Input Options
-------------

The matrix preprocessor supports the following set of command line options. All
are optional except for ``--infile``, which specifies the file containing the
term-frequency matrix to be processed:

+--------------------------------+----------+------------------------------------------------------+
|       Option                   | Argument |                Explanation                           |
+--------------------------------+----------+------------------------------------------------------+
|``-i``, ``--infile``            | string   | path to input file, MatrixMarket format              |
+--------------------------------+----------+------------------------------------------------------+
|``-r``, ``--min_docs_per_term`` | integer  | min number of docs per dictionary term, default 3    |
+--------------------------------+----------+------------------------------------------------------+
|``-c``, ``--min_terms_per_doc`` | integer  | min number of dictionary terms per doc, default 5    |
+--------------------------------+----------+------------------------------------------------------+
|``-p``, ``--precision``         | integer  | precision of values in output file, default 4 digits |
|                                |          | (valid only if ``--weights`` flag is present)        |
+--------------------------------+----------+------------------------------------------------------+
|``-w``, ``--weights``           | none     | if present, generate TF-IDF weights for entries      |
|                                |          | and output a floating point term-document matrix     |
+--------------------------------+----------+------------------------------------------------------+
| ``-b``, ``--boolean``          | none     | if present, enable boolean mode, in which nonzero    |
|                                |          | values in the input matrix are set to 1              |
+--------------------------------+----------+------------------------------------------------------+
| ``-h``, ``--help``             | none     | print user help to stdout                            |
+--------------------------------+----------+------------------------------------------------------+
| ``-v``, ``--version``          | none     | print version information to stdout                  |
+--------------------------------+----------+------------------------------------------------------+

The ``--min_docs_per_term`` option is the cutoff value for pruning rows. Any
dictionary term that appears in fewer than this many documents will be pruned.
In other words, a row of the input matrix will be pruned if its row sum is less
than this value.

Similarly, the ``--min_terms_per_doc`` option is the cutoff value for pruning
columns. Any document that contains fewer than this many dictionary words will
be pruned. In other words, a column of the input matrix will be pruned if its
column sum is less than this value.

Outputs
=======

The matrix preprocessor generates three output files.

One file, ``reduced_dictionary_indices.txt``, is a list of row indices from the
original matrix that survived the pruning process. Another file,
``reduced_document_indices.txt``, contains a list of original document indices
that survived the pruning process.

The third file, in MatrixMarket format, is the pruned matrix. The contents and
name of this file depend on whether the ``--weights`` flag was used for the
run.

If the ``--weights`` flag was absent, the output is another term-frequency
matrix in MatrixMarket format. The output file name is ``reduced_matrix_tf.mtx``
and it contains nonnegative integer entries.

If the ``--weights`` flag was present, the output is a term-document matrix
containing TF_IDF weights for the entries. In this case the output file name
is ``reduced_matrix.mtx`` and it contains floating point entries. The precision
of each entry is set by the ``--precision`` flag.

All output files are written to the current directory.

Examples
========

1. Prune duplicate rows/columns from the input term-frequency matrix.
   Write pruned matrix to ``reduced_matrix_tf.mtx``; generate the two index files
   as well:
   ::
      python3 ./preprocess.py --infile /path/to/mymatrix.mtx


2. Same as in example 1, but generate an output term-document matrix containing
   TF-IDF weights. Write result matrix to ``reduced_matrix.mtx``; generate the
   two index files also:
   ::
      python3 ./preprocess.py --infile /path/to/mymatrix.mtx --weights

3. Same as 2, but require a mininim row sum of 6 and a mininum column sum of 8
   in the pruned term-frequency matrix. Compute TF-IDF weights and output a
   floating point term-document matrix.
   ::
      python ./preprocess.py -i /path/to/mymatrix.mtx -r 6 -c 8 -w


Important Note
==============

The matrix preprocessor was designed for sparse matrices. The term-frequency
matrices that occur in typical text processing problems are extremely sparse,
with occupancies of only a few percent. Dense matrices should be handled with
different techniques.

