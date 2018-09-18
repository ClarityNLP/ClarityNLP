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
#include <set>

//-----------------------------------------------------------------------------
template <typename T>
class SparseMatrix
{
    // This is a sparse matrix class based on the algorithms in SuiteSparse.
    //
    // Constraints on matrix dimensions:
    //
    // Let S = std::numeric_limits<unsigned int>::max()
    //
    // Max height of sparse matrix:   S
    // Max width of sparse matrix:    S-1
    // Max nonzeros in sparse matrix: S
    //

public:

    ~SparseMatrix() {}
    SparseMatrix();
    SparseMatrix(const unsigned int height, 
                 const unsigned int width, 
                 const unsigned int nzmax);
    SparseMatrix(const unsigned int height,
                 const unsigned int width,
                 const unsigned int nzmax,
                 const unsigned int* col_offsets,  // width+1 entries
                 const unsigned int* row_indices,  // nzmax entries
                 const T* data);                   // nzmax entries
    SparseMatrix(const SparseMatrix<T>& m);

    // TODO: add assignment operator, move copy c'tor and move assignment operator

    unsigned int Height()    const  {return height_;}
    unsigned int Width()     const  {return width_;}
    unsigned int Size()      const;
    
    // these buffer functions assume that the matrix has data
    unsigned int* ColBuffer()  {return &col_offsets_[0];}
    unsigned int* RowBuffer()  {return &row_indices_[0];}
    T*            DataBuffer() {return &data_[0];}

    const unsigned int* LockedColBuffer()  const {return &col_offsets_[0];}
    const unsigned int* LockedRowBuffer()  const {return &row_indices_[0];}
    const T*            LockedDataBuffer() const {return &data_[0];}

    // matrix loading; data is loaded as triplets and then compressed
    void BeginLoad();
    void EndLoad();

    // reserve space for matrix
    void Reserve(const unsigned int height, const unsigned int width, const unsigned int nzmax);

    // load a matrix element; must call BeginLoad first
    void Load(const unsigned int row, const unsigned int col, const T& value);
    
    // delete all data
    void Clear();

    // get the element at row r and column c
    T Get(const unsigned int r, const unsigned int c);

    // extract a sub-matrix of dimension height x width, starting at (r0, c0)
    void SubMatrix(SparseMatrix<T>& result,
                   const unsigned int r0,
                   const unsigned int c0,
                   const unsigned int height,
                   const unsigned int width) const;

    // remove entries from the matrix if absolute value <= epsilon
    void RemoveZeros(const T& epsilon = T(0));

    // return indices of all rows whose elements have an absolute value <= epsilon
    void NonZeroRowIndices(std::set<unsigned int>& row_indices, const T& epsilon = T(0));

    //void ResizeToFit();

    void SubMatrixCols(SparseMatrix<T>& result,
                       const std::vector<unsigned int>& col_indices) const;

    // Extract a submatrix consisting of the given cols, but with any resulting
    // zero-rows removed.  This function produces the most compact result.
    // Forward and reverse row index maps are returned.
    void SubMatrixColsCompact(SparseMatrix<T>& result,
                              const std::vector<unsigned int>& col_indices,
                              std::vector<unsigned int>& old_to_new_rows,
                              std::vector<unsigned int>& new_to_old_rows) const;

    // same as SubMatrixColsCompact but only returns row information
    void SubMatrixRowsCompact(const std::vector<unsigned int>& col_indices,
                              std::vector<unsigned int>& old_to_new_rows,
                              std::vector<unsigned int>& new_to_old_rows) const;

private:

    unsigned int height_;
    unsigned int width_;

    bool is_loading_;

    unsigned int size_;      // number of nonzero elements, used only for loading

    // The matrix is stored in compressed column format.  These arrays are
    // also used for loading the elements, which can be done in random order.

    std::vector<unsigned int> col_offsets_; // max(nzmax, width+1) entries
    std::vector<unsigned int> row_indices_; // nzmax entries
    std::vector<T> data_;                   // nzmax entries

    // convert to compressed column format
    void Compress();
    void SetSize(const unsigned int sz) {size_ = sz;}
    void SetHeight(const unsigned int h) {height_ = h;}
};
