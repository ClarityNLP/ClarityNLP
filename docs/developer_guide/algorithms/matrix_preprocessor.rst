Term-Frequency Matrix Preprocessor
**********************************

Overview
========

`Term-frequency matrices` feature prominently in text processing and
information retrieval algorithms. In these problems one typically has a set of
documents and a list of words (the `dictionary`). A
term-frequency matrix is constructed from the dictionary and
the document set by counting the number of occurrences of each dictionary word
in each document. If the rows of the matrix index the words and the columns
index the documents, then the matrix element at coordinates (r, c) represents
the number of occurrences of dictionary word `r` in document `c`. Thus each
entry of the matrix is either zero or a positive integer.

Construction of such a matrix is conceptually simple, but problems can arise if
the matrix contains duplicate rows or columns. The presence of duplicate
columns, for instance, means that those documents are *identical* with respect
to the given dictionary. The linear algebra algorithms that underlie many text
processing and information retrieval tasks can exhibit instability or extremely
slow convergence if duplicates are present. Mathematically, a term-frequency
matrix with duplicate columns has a rank that is numerically less than the
column count. Under such conditions it is advantageous to remove the duplicated
columns (and/or rows) and work with a smaller full-rank matrix.

The matrix preprocessor is a command-line tool that scans a term-frequency
matrix looking for duplicate rows and columns. If it finds any duplicates it
prunes them and keeps only one row or column from the set of duplicates. After
pruning it scans the matrix again, since removal of rows or columns could
create further duplicates. This process of scanning and checking for duplicates
proceeds iteratively until either nothing is left (a rare occurrence) or a
stable matrix is achieved. The resulting matrix is written to disk, along with
the surviving row and column index lists.


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

|    ``cd nlp/algorithms/matrix_preprocessor``
|    ``make``

The build process should run to completion with no errors, after which these
binaries should be present in the ``build/bin`` folder: ``libpreprocess.a``,
``preprocessor``, and ``test_preprocessor``.


Inputs
======

The matrix preprocessor requires a single input file representing a sparse
matrix. The input file must be in MatrixMarket_ format, a popular and efficient
format for sparse matrices.

.. _MatrixMarket: https://math.nist.gov/MatrixMarket/

Python supports the MatrixMarket format via the ``scipy`` module and the
functions ``scipy.io.mmwrite`` and ``scipy.io.mmread``.

Input Options
-------------



Outputs
=======

Examples
========



Important Note
==============

The matrix preprocessor was designed for sparse matrices. The term-
frequency matrices that occur in text processing problems are typically
extremely sparse, with occupancies of only a few percent. Dense matrices should
be handled with different techniques.



