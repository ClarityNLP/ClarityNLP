#!/usr/bin/env python3
"""
"""

import os
import sys
import optparse
import subprocess

_VERSION_MAJOR = 0
_VERSION_MINOR = 1

_MODULE_NAME = 'preprocess.py'

_MIN_DOCS_PER_TERM = 3
_MIN_TERMS_PER_DOC = 5
_MAX_ITER          = 1000
_PRECISION         = 4
_BOOLEAN_MODE      = 0

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
    print(get_version())
    print("""
    USAGE: python3 ./{0} 

         -i <quoted string> input file, matrix market format
        [-d <positive int>  mininum number of docs per term, default is 3]
        [-t <positive int>  minimum number of terms per doc, default is 5]
        [-m <positive int>  max iterations, default is 1000]
        [-p <positive int>  precision of result matrix, default is 4 digits]
        [-b <int>           boolean mode, 0=False, 1=True, default is False]
        [-hvz]

    OPTIONS:

        -i, --infile             <quoted string>  Path to .mtx input file.
        -d, --min_docs_per_term  <int>   A term must appear in at least this
                                         many docs to not prune its row.
        -t, --min_terms_per_doc  <int>   A document must contain at least this
                                         many terms to not prune its column.
        -m, --max_iter           <int>   Maximum number of iterations.
        -p, --precision          <int>   Number of digits of precision to use
                                         for entries in the result matrix.
        -b, --boolean_mode       <int>   Use 1 for all nonzero entries in the
                                         input matrix.
                                           
    FLAGS:

        -h, --help           Print this information and exit.
        -v, --version        Print version information and exit.
        -z, --selftest       Run self-tests and exit.

    """.format(_MODULE_NAME))


###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option = False)
    optparser.add_option('-i', '--infile', action='store', dest='infile')
    optparser.add_option('-d', '--min_docs_per_term', action='store',
                         dest='min_d')
    optparser.add_option('-t', '--min_terms_per_doc', action='store',
                         dest='min_t')
    optparser.add_option('-m', '--max_iter', action='store', dest='max_iter')
    optparser.add_option('-p', '--precision', action='store', dest='precision')
    optparser.add_option('-b', '--boolean_mode', action='store',
                         dest='boolean_mode')
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
        print(get_version())
        sys.exit(0)

    if opts.selftest:
        run_tests()
        sys.exit(0)

    if opts.infile is None:
        print('Error: an input file must be specified.')
        sys.exit(-1)
        
    if not os.path.exists(opts.infile):
        print('Error: file not found: {0}'.format(opts.infile))
        sys.exit(-1)

    infile = opts.infile

    if opts.min_d is None:
        min_docs_per_term = _MIN_DOCS_PER_TERM
    else:
        min_docs_per_term = int(opts.min_d)

    if min_docs_per_term <= 0:
        print('Error: invalid value for min docs per term: {0}'.
              format(min_docs_per_term))
        sys.exit(-1)

    if opts.min_t is None:
        min_terms_per_doc = _MIN_TERMS_PER_DOC
    else:
        min_terms_per_doc = int(opts.min_t)

    if min_terms_per_doc <= 0:
        print('Error: invalid value for min terms per doc: {0}'.
              format(min_terms_per_doc))
        sys.exit(-1)

    if opts.max_iter is None:
        max_iter = _MAX_ITER
    else:
        max_iter = int(opts.max_iter)

    if max_iter <= 0:
        print('Error: invalid value for max iterations: {0}'.format(max_iter))
        sys.exit(-1)

    if opts.precision is None:
        precision = _PRECISION
    else:
        precision = int(opts.precision)

    if precision <= 0:
        print('Error: invalid value for precision: {0}'.format(precision))
        sys.exit(-1)

    if opts.boolean_mode is None:
        boolean_mode = _BOOLEAN_MODE
    else:
        boolean_mode = int(opts.boolean_mode)

    if boolean_mode > 0:
        boolean_mode = 1
    else:
        boolean_mode = 0


    print('options: ')
    print('\t           infile: {0}'.format(infile))
    print('\tmin_docs_per_term: {0}'.format(min_docs_per_term))
    print('\tmin_terms_per_doc: {0}'.format(min_terms_per_doc))
    print('\t         max_iter: {0}'.format(max_iter))
    print('\t        precision: {0}'.format(precision))
    print('\t     boolean_mode: {0}'.format(boolean_mode))

    command = []
    exe = os.path.join(os.getcwd(), 'build', 'bin', 'preprocessor')
    command.append(exe)
    command.append('--infile')
    command.append(infile)
    command.append('--min_docs_per_term')
    command.append('{0}'.format(min_docs_per_term))
    command.append('--min_terms_per_doc')
    command.append('{0}'.format(min_terms_per_doc))
    command.append('--maxiter')
    command.append('{0}'.format(max_iter))
    command.append('--precision')
    command.append('{0}'.format(precision))
    command.append('--boolean_mode')
    command.append('{0}'.format(boolean_mode))

    cp = subprocess.run(command,
                        stdout=subprocess.PIPE,
                        universal_newlines=True)

    print(cp.stdout)
