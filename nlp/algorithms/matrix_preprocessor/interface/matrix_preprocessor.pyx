import numpy
cimport numpy as np
import cython

#IF UNAME_SYSNAME == "Darwin":
#    MACOSX_DEPLOYMENT_TARGET=10.7

from libcpp.string cimport string
from libcpp cimport bool
from cython.operator import dereference

from libcpp.vector cimport vector

import argparse
import sys

cdef extern from "term_frequency_matrix.hpp":
    cdef cppclass TermFrequencyMatrix:
        #TermFrequencyMatrix(const SparseMatrix[double]& S, bool boolean_mode)

        TermFrequencyMatrix(const unsigned int height,
                            const unsigned int width,
                            const unsigned int nnz,
                            const unsigned int* indptr,
                            const unsigned int* indices,
                            const double* data,
                            const bool boolean_mode)
        
        unsigned int Width()
        unsigned int Height()
        unsigned int Size()
        unsigned int Capacity()
        #bool WriteMtxFile(const string& file_path, const double* scores, 
        #                  const unsigned int precision)
        #const unsigned int* LockedColBuffer()
        #const TFData* LockedDataBuffer()
    cdef struct TFData:
        TFData()
        unsigned int row
        unsigned int count 

cdef extern from "preprocess.hpp":
    bool _preprocess_tf "preprocess_tf"(TermFrequencyMatrix& A,
                                        vector[unsigned int]& term_indices,
                                        vector[unsigned int]& doc_indices,
                                        vector[double]& scores,
                                        const unsigned int MAX_ITER,
                                        const unsigned int DOCS_PER_TERM,
                                        const unsigned int TERMS_PER_DOC)

@cython.boundscheck(False)
@cython.wraparound(False)


cdef class TermFreqMatrix:
    cdef TermFrequencyMatrix *_thisptr
    #def __cinit__(self, Sparse A, bool b_mode):
    #    self.thisptr = new TermFrequencyMatrix(dereference(A.get()), b_mode)
    def __cinit__(self,
                  unsigned int height,
                  unsigned int width,
                  unsigned int nnz,
                  #unsigned int[:] indptr,
                  #unsigned int[:] indices,
                  int[:] indptr,
                  int[:] indices,
                  double[:] data,
                  bool boolean_mode):
        self._thisptr = new TermFrequencyMatrix(height, width, nnz,
                                                <unsigned int*> (&indptr[0]),
                                                <unsigned int*> (&indices[0]),
                                                &data[0],
                                                boolean_mode)
    def __dealloc__(self):
        if self._thisptr != NULL:
            del self._thisptr
    def width(self):
        return self._thisptr.Width()
    def height(self):
        return self._thisptr.Height()
    def size(self):
        return self._thisptr.Size()
    def capacity(self):
        return self._thisptr.Capacity()
        
    #def LockedColBuffer(self):
    #    return self._thisptr.LockedColBuffer()
    #def LockedDataBuffer(self):
    #    return self._thisptr.LockedDataBuffer()
    cdef TermFrequencyMatrix* get(self):
        return self._thisptr


# cdef preprocess_tf(A,
#                    term_indices,
#                    doc_indices,
#                    scores,
#                    MAX_ITER,
#                    DOCS_PER_TERM,
#                    TERMS_PER_DOC):
#     return _preprocess_tf(A, term_indices, doc_indices, scores,
#                           MAX_ITER, DOCS_PER_TERM, TERMS_PER_DOC)
