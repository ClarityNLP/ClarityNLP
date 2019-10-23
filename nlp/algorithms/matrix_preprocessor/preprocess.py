#!/usr/bin/env python3
"""


OVERVIEW


This is a command-line tool for pruning duplicate rows and columns from a
term-frequency matrix.

The presence of duplicate rows and/or columns means that the matrix does not
have full column rank, a condition that can cause numerical problems for
machine learning algorithms.

If any duplicate rows or colums are found, the code removes the duplicates
and then checks again, iterating until all duplicates have been removed.


PREREQUISITES


A C++ compiler is required to use this code.

On Linux, install the build-essential package. If a C++ compiler is not
provided with this package on your system, then install the g++ package as
well.

On MacOSX, install the clang++ command line tools with this command:

    xcode-select --install

Alternatively, you could install the full XCode app and use it to install the
command line tools.


BUILDING THE CODE


After installing a C++ compiler, build the code as follows:

    cd /path/to/matrix_preprocessor
    make

The build process should proceed with no errors and create the subdirectory
build/bin, which should contain these binaries:

    libpreprocess.a
    preprocessor
    test_preprocessor


The first two binaries must be present to use the python driver, which is
called 'preprocess.py'.


INPUTS


The input file is assumed to represent a sparse matrix. The matrix market file
format is assumed. This is a common format supported by Python with the
scipy.io.mmread and scipy.io.mmwrite functions.


Help for all input options can be obtained with the --help option.


OUTPUTS


The type of output depends on whether the --weights flag is present.

If the --weights flag is absent, the output is another term-frequency matrix
in matrix market format. The output file name is reduced_matrix_tf.mtx.

If the --weights flag is present, the output is a term-document matrix
containing tf-idf weights for the entries. In this case the output file name
is reduced_matrix.mtx.

Two index files are also generated, 'reduced_dictionary_indices.txt' and
'reduced_document_indices.txt'. These files contain the surviving row and
column indices from the original term-frequency matrix.

All output files are written to the current directory.


EXAMPLES


1. Prune duplicate rows/columns from the term-frequency matrix 'mymatrix.mtx'.
   Write pruned matrix to reduced_matrix_tf.mtx; generate the two index files
   as well.

   python3 ./preprocess.py --infile /path/to/mymatrix.mtx


2. Same as in example 1, but generate a TF-IDF weighted output matrix. Write
   result matrix to reduced_matrix.mtx; generate the two index files also.

   python3 ./preprocess.py --infile /path/to/mymatrix.mtx --weights

3. Same as 2, but require a mininim row sum of 6 and a mininum column sum of 8
   in the pruned term-frequency matrix. Compute TF-IDF weights also.

   python ./preprocess.py -i /path/to/mymatrix.mtx -r 6 -c 8 -w

"""

import os
import sys
import optparse
import subprocess
from claritynlp_logging import log, ERROR, DEBUG


_VERSION_MAJOR = 0
_VERSION_MINOR = 1

_MODULE_NAME = 'preprocess.py'

_MIN_DOCS_PER_TERM = 3
_MIN_TERMS_PER_DOC = 5
_MAX_ITER          = 1000
_PRECISION         = 4

###############################################################################
def run_tests():
    """
    """
    pass


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
def show_help():
    log(get_version())
    log("""
    USAGE: python3 ./{0} 

    OPTIONS:

         -i, --infile             <quoted string> (required) input filename
                                                  matrix market format
        [-r, --min_docs_per_term] <positive int>  mininum number of docs per
                                                  term, default is 3
                                                  (minimum allowable row sum
                                                  in result matrix)
        [-c, --min_terms_per_doc] <positive int>  minimum number of terms per
                                                  document, default is 5
                                                  (minimum allowable column sum
                                                  in result matrix)
        [-p, --precision]         <positive int>  precision of result matrix
                                                  (default is 4 digits)
        [-hvzbw]

    FLAGS:

        -h, --help           log this information and exit.
        -v, --version        log version information and exit.
        -z, --selftest       Run self-tests and exit.
        -b, --boolean        Replace nonzero entries in input matrix with 1
                             (i.e. use 1 if value present, 0 if not)
        -w, --weights        Compute tf-idf weights in result matrix
                             (i.e. output a term-document matrix instead of
                             a term-frequency matrix)

    """.format(_MODULE_NAME))


###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option = False)
    optparser.add_option('-i', '--infile', action='store', dest='infile')
    optparser.add_option('-r', '--min_docs_per_term', action='store',
                         dest='min_d')
    optparser.add_option('-c', '--min_terms_per_doc', action='store',
                         dest='min_t')
    optparser.add_option('-p', '--precision', action='store', dest='precision')
    optparser.add_option('-b', '--boolean_mode', action='store_true',
                         dest='boolean_mode', default=False)
    optparser.add_option('-w', '--weights', action='store_true',
                         dest='weights', default=False)
    optparser.add_option('-v', '--version', action='store_true',
                         dest='get_version')
    optparser.add_option('-h', '--help', action='store_true',
                         dest='show_help', default=False)
    optparser.add_option('-z', '--selftest', action='store_true',
                         dest='selftest', default=False)

    opts, other = optparser.parse_args(sys.argv)

    if 1 == len(sys.argv) or opts.show_help:
        show_help()
        sys.exit(0)

    if opts.get_version:
        log(get_version())
        sys.exit(0)

    if opts.selftest:
        run_tests()
        sys.exit(0)

    if opts.infile is None:
        log('Error: an input file must be specified.')
        sys.exit(-1)
        
    if not os.path.exists(opts.infile):
        log('Error: file not found: {0}'.format(opts.infile))
        sys.exit(-1)

    infile = opts.infile

    if opts.min_d is None:
        min_docs_per_term = _MIN_DOCS_PER_TERM
    else:
        min_docs_per_term = int(opts.min_d)

    if min_docs_per_term <= 0:
        log('Error: invalid value for min docs per term: {0}'.
              format(min_docs_per_term))
        sys.exit(-1)

    if opts.min_t is None:
        min_terms_per_doc = _MIN_TERMS_PER_DOC
    else:
        min_terms_per_doc = int(opts.min_t)

    if min_terms_per_doc <= 0:
        log('Error: invalid value for min terms per doc: {0}'.
              format(min_terms_per_doc))
        sys.exit(-1)

    if opts.precision is None:
        precision = _PRECISION
    else:
        precision = int(opts.precision)

    if precision <= 0:
        log('Error: invalid value for precision: {0}'.format(precision))
        sys.exit(-1)

    log('options: ')
    log('\t           infile: {0}'.format(infile))
    log('\tmin_docs_per_term: {0}'.format(min_docs_per_term))
    log('\tmin_terms_per_doc: {0}'.format(min_terms_per_doc))
    log('\t        precision: {0}'.format(precision))
    log('\t     boolean_mode: {0}'.format(opts.boolean_mode))
    log('\t          weights: {0}'.format(opts.weights))

    command = []
    exe = os.path.join(os.getcwd(), 'build', 'bin', 'preprocessor')
    command.append(exe)
    command.append('--infile')
    command.append(infile)
    command.append('--min_docs_per_term')
    command.append('{0}'.format(min_docs_per_term))
    command.append('--min_terms_per_doc')
    command.append('{0}'.format(min_terms_per_doc))
    command.append('--precision')
    command.append('{0}'.format(precision))
    if opts.boolean_mode:
        command.append('--boolean_mode')
    if opts.weights:
        command.append('--tf_idf')

    cp = subprocess.run(command,
                        stdout=subprocess.PIPE,
                        universal_newlines=True)

    log(cp.stdout)
