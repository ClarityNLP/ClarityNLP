// Copyright 2014 Georgia Institute of Technology
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include <vector>
#include <string>
#include "sparse_matrix_decl.hpp"
#include "sparse_matrix_impl.hpp"

struct TFData
{
    unsigned int row;    // row index of this nonzero element
    unsigned int count;  // occurrence count

    bool operator==(const TFData& rhs) const
    {return ( (row == rhs.row) && (count == rhs.count));}

    bool operator!=(const TFData& rhs) const
    {return !operator==(rhs);}
};

//-----------------------------------------------------------------------------
class TermFrequencyMatrix
{
    // This is a sparse matrix class representing term-frequency matrices.
    // These matrices must be built from an existing SparseMatrix.
    //
    // Constraints on matrix dimensions:
    //
    // Let S = std::numeric_limits<unsigned int>::max()
    //
    // Max height of sparse matrix:   S
    // Max width of sparse matrix:    S-1
    // Max nonzeros in sparse matrix: S

public:

    ~TermFrequencyMatrix() {}
    TermFrequencyMatrix();

    // A TermFrequencyMatrix must be constructed from an existing SparseMatrix.
    TermFrequencyMatrix(const SparseMatrix<double>& S, bool boolean_mode = false);

    void Init(const SparseMatrix<double>& S, bool boolean_mode = false);

    unsigned int Height()    const  {return height_;}
    unsigned int Width()     const  {return width_;}
    unsigned int Size()      const;
    unsigned int Capacity()  const  {return capacity_;}
    
    // these buffer functions assume that the matrix has been loaded
    unsigned int* ColBuffer()  {return &col_offsets_[0];}
    TFData* TFDataBuffer()     {return &tf_data_[0];}

    const unsigned int* LockedColBuffer()  const {return &col_offsets_[0];}
    const TFData* LockedTFDataBuffer()     const {return &tf_data_[0];}

    void SortRows();
    bool operator==(const TermFrequencyMatrix& rhs) const;
    bool operator!=(const TermFrequencyMatrix& rhs) const;

    // compare locations of nonzeros only - ignore counts
    bool CompareAsBoolean(const TermFrequencyMatrix& rhs) const;
    
    void SetHeight(const unsigned int h) {height_ = h;}
    void SetWidth(const unsigned int w)  {width_ = w;}
    void SetSize(const unsigned int sz)  {size_ = sz;}

    void Print(const std::string& msg);

    bool WriteMtxFile(const std::string& file_path);
    
    // scores are assumed to be aligned with the tf_data
    bool WriteMtxFile(const std::string& file_path,
                      const double* scores,
                      const unsigned int precision);

private:

    unsigned int height_;
    unsigned int width_;

    unsigned int size_;      // number of nonzero elements
    unsigned int capacity_;  // allocated space, >= size_

    // The matrix is stored in a modified compressed column format.  Instead
    // of using separate row and data arrays, the two are combined into a
    // single array.  This makes sorting, hashing, and other operations much
    // easier.
    std::vector<unsigned int> col_offsets_; // width_ + 1 entries
    std::vector<TFData> tf_data_;           // size_ entries (nonzero count)
};

