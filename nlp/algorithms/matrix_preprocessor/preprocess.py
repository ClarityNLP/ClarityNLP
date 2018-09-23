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

    OPTIONS:

         -i <quoted string> input filename, matrix market format
        [-d <positive int>  mininum number of docs per term, default is 3]
                            (minimum allowable row sum in result matrix)
        [-t <positive int>  minimum number of terms per doc, default is 5]
                            (minimum allowable column sum in result matrix)
        [-p <positive int>  precision of result matrix, default is 4 digits]
        [-hvzbw]

    FLAGS:

        -h, --help           Print this information and exit.
        -v, --version        Print version information and exit.
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
    optparser.add_option('-d', '--min_docs_per_term', action='store',
                         dest='min_d')
    optparser.add_option('-t', '--min_terms_per_doc', action='store',
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

    if opts.precision is None:
        precision = _PRECISION
    else:
        precision = int(opts.precision)

    if precision <= 0:
        print('Error: invalid value for precision: {0}'.format(precision))
        sys.exit(-1)

    print('options: ')
    print('\t           infile: {0}'.format(infile))
    print('\tmin_docs_per_term: {0}'.format(min_docs_per_term))
    print('\tmin_terms_per_doc: {0}'.format(min_terms_per_doc))
    print('\t        precision: {0}'.format(precision))
    print('\t     boolean_mode: {0}'.format(opts.boolean_mode))
    print('\t          weights: {0}'.format(opts.weights))

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

    print(cp.stdout)
