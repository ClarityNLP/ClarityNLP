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

// A sparse matrix class based on the algorithms in SuiteSparse.

#include <map>
#include <cmath>
#include <limits>
#include <cstdint>
#include <cassert>
#include <algorithm>
#include <stdexcept>
#include "error.hpp"
#include "random.hpp"
#include "vector_utils.hpp"

//-----------------------------------------------------------------------------
template <typename T>
inline
unsigned int SparseMatrix<T>::Size() const
{
    if (!col_offsets_.empty())
        return col_offsets_[width_];
    else
        return 0;
}

//-----------------------------------------------------------------------------
template <typename T>
void SparseMatrix<T>::Clear()
{
    if (data_.size() > 0)
        data_.clear();

    if (row_indices_.size() > 0)
        row_indices_.clear();

    if (col_offsets_.size() > 0)
        col_offsets_.clear();

    size_ = 0;
    is_loading_ = false;
    width_ = 0;
    height_ = 0;
}

//-----------------------------------------------------------------------------
template <typename T>
inline
SparseMatrix<T>::SparseMatrix()
    : height_(0), width_(0), is_loading_(false), size_(0)
{
}

//-----------------------------------------------------------------------------
template <typename T>
inline
SparseMatrix<T>::SparseMatrix(const unsigned int height, 
                              const unsigned int width, 
                              const unsigned int nzmax)
    : height_(height), width_(width), 
      is_loading_(false), size_(nzmax)
{
    Reserve(height_, width_, size_);
}

//-----------------------------------------------------------------------------
template <typename T>
inline
SparseMatrix<T>::SparseMatrix(const unsigned int height,
                 const unsigned int width,
                 const unsigned int nzmax,
                 const unsigned int* col_offsets,
                 const unsigned int* row_indices,
                 const T* data)
    : height_(height), width_(width), 
      is_loading_(false), size_(nzmax),
      col_offsets_(col_offsets, col_offsets + width+1),
      row_indices_(row_indices, row_indices + nzmax),
      data_(data, data + nzmax)
{
}

//-----------------------------------------------------------------------------
template <typename T>
inline
SparseMatrix<T>::SparseMatrix(const SparseMatrix<T>& m)
    : height_(m.height_), width_(m.width_),
      is_loading_(m.is_loading_), size_(m.size_),
      col_offsets_(m.col_offsets_), row_indices_(m.row_indices_), 
      data_(m.data_)
{
}

//-----------------------------------------------------------------------------
template <typename T>
inline
void SparseMatrix<T>::BeginLoad()
{
    size_ = 0;
    is_loading_ = true;
}

//-----------------------------------------------------------------------------
template <typename T>
inline
void SparseMatrix<T>::EndLoad()
{
    Compress();
    is_loading_ = false;
}

//-----------------------------------------------------------------------------
template <typename T>
void SparseMatrix<T>::Reserve(const unsigned int height, 
                              const unsigned int width,
                              const unsigned int nzmax)
{
    // (width+1) must fit in an unsigned int
    if (width == std::numeric_limits<unsigned int>::max())
        throw std::runtime_error("SparseMatrix::Reserve: width too large");

    // The col_offsets array requires (width+1) entries when compressed, and
    // nzmax entries when loading.  Allocate the max of these.

    unsigned int s = std::max(nzmax, width+1);
    if (col_offsets_.size() < s)
        col_offsets_.resize(s);

    // the row_indices array requires nzmax entries
    if (row_indices_.size() < nzmax)
        row_indices_.resize(nzmax);

    // the data array requires nzmax entries
    if (data_.size() < nzmax)
        data_.resize(nzmax);

    height_    = height;
    width_     = width;
    size_      = 0;
}

//-----------------------------------------------------------------------------
template <typename T>
inline
void SparseMatrix<T>::Load(const unsigned int row, 
                           const unsigned int col, 
                           const T& value)
{
    if (!is_loading_)
        throw std::runtime_error("SparseMatrix::Load: matrix not in load mode");
    if (col >= width_)
        throw std::runtime_error("SparseMatrix::Load: col index out of bounds");
    if (row >= height_)
        throw std::runtime_error("SparseMatrix::Load: row index out of bounds");

    assert(size_ < col_offsets_.size());
    col_offsets_[size_] = col;

    assert(size_ < row_indices_.size());
    row_indices_[size_] = row;

    assert(size_ < data_.size());
    data_[size_] = value;
    ++size_;
}

//-----------------------------------------------------------------------------
template <typename T>
inline
void SparseMatrix<T>::Compress()
{
    if (0 == size_)
        throw std::runtime_error("SparseMatrix::Compress: matrix has no data");

    // Check the columns to see if they are already sorted in nondecreasing
    // order.  If not, sort the column indices and reorder the rows and 
    // data arrays to match.

    bool sorted = true;
    if (size_ >= 2)
    {
        for (unsigned int i=0; i != (size_ - 1); ++i)
        {
            if (col_offsets_[i] > col_offsets_[i+1])
            {
                sorted = false;
                break;
            }
        }
    }        

    // Whether the column data is sorted or not, bin the column indices,
    // and compute a prefix sum of the binned data to generate the compressed
    // column representation of the column indices.

    // copy the column indices
    std::vector<unsigned int> col_temp(col_offsets_);
    std::vector<unsigned int> counts(width_);

    // size_ elements have been loaded
    Histogram(col_offsets_.begin(), col_offsets_.begin() + size_, 
              counts.begin(), counts.end());
    PrefixSum(counts.begin(), counts.end());
    std::copy(counts.begin(), counts.end(), col_offsets_.begin()+1);
    col_offsets_[0] = 0;

    if (!sorted)
    {
        unsigned int offset_a, offset_b, row_index, c;

        // need temp copies of the row and data arrays
        std::vector<unsigned int> row_temp (row_indices_);
        std::vector<T>            data_temp(data_);

        for (unsigned int k=1; k <= size_; ++k)
        {
            // offset into the unsorted arrays
            offset_a = size_ - k;

            // the row index of the nonzero element at this offset
            row_index = row_temp[offset_a];
            
            // the column index of this element
            c = col_temp[offset_a];
            assert(c <= (width_));

            // destination offset + 1
            offset_b = counts[c];
            if (0 == offset_b)
                continue;

            row_indices_[offset_b-1] = row_index;
            data_[offset_b-1]        = data_temp[offset_a];
                
            // one fewer element in the source array <= row_index
            counts[c] -= 1;
        }
    }

    // set the size
    col_offsets_[width_] = size_;

    // May still have duplicates - need to find duplicates and sum. TBD
}

//-----------------------------------------------------------------------------
template <typename T>
T SparseMatrix<T>::Get(const unsigned int r, const unsigned int c)
{
    if (r >= height_)
        throw std::logic_error("Get: row index out of bounds.");
    if (c >= width_)
        throw std::logic_error("Get: col index out of bounds.");

    T val = T(0);

    // scan all nonzero elements for column c; if row r is present, 
    // return the associated value, otherwise return 0
    unsigned int start = col_offsets_[c];
    unsigned int end   = col_offsets_[c+1];
    for (unsigned int offset = start; offset != end; ++offset)
    {
        unsigned int row = row_indices_[offset];
        if (r == row)
        {
            val = data_[offset];
            break;
        }
    }

    return val;
}

//-----------------------------------------------------------------------------
template <typename T>
void SparseMatrix<T>::SubMatrix(SparseMatrix<T>& result,
                                const unsigned int r0,
                                const unsigned int c0,
                                const unsigned int new_height,
                                const unsigned int new_width) const
{
    // one past the end of each range
    unsigned int r1 = r0 + new_height;
    unsigned int c1 = c0 + new_width;

    if ( (r0 >= height_) || (r1 > height_))
        throw std::logic_error("SubMatrix: invalid row limits");
    if ( (c0 >= width_) || (c1 > width_))
        throw std::logic_error("SubMatrix: invalid column limits");

    // count the number of nonzeros in the submatrix

    unsigned int new_size = 0;
    for (unsigned int c=c0; c != c1; ++c)
    {
        // number of nonzeros in source column c
        new_size += (col_offsets_[c+1] - col_offsets_[c]);
    }

    if (0u == new_size)
        throw std::logic_error("SparseMatrix::SubMatrix: submatrix is the zero matrix");

    // allocate memory in the result; won't allocate if sufficient memory available
    result.Reserve(new_height, new_width, new_size);

    // Load the elements within the row and column bounds into the new matrix.
    // No need to call result.Clear(), since that will result in a new allocation.

    unsigned int* cols_b = result.ColBuffer();
    unsigned int* rows_b = result.RowBuffer();
    T* data_b            = result.DataBuffer();

    unsigned int count = 0;
    for (unsigned int c=c0; c != c1; ++c)
    {
        cols_b[c-c0] = count;

        unsigned int start = col_offsets_[c];
        unsigned int end   = col_offsets_[c+1];
        for (unsigned int offset = start; offset != end; ++offset)
        {
            unsigned int row = row_indices_[offset];
            if ( (row >= r0) && (row < r1))
            {
                rows_b[count] = row - r0;
                data_b[count] = data_[offset];
                ++count;
            }
        }
    }

    cols_b[c1] = count;
    //assert(new_size == count);

    // set the size of the new matrix explicitly, since Load() has been bypassed
    result.SetSize(count);
}

//-----------------------------------------------------------------------------
template <typename T>
void SparseMatrix<T>::RemoveZeros(const T& epsilon)
{
    // This function removes zeros from a matrix.  Removal of zeros may
    // result in some unused row indices, if the removed zeros are the
    // only entries in those rows.  Regardless, this function does not
    // change the height of the matrix.

    unsigned int nz_count = 0;

    for (unsigned int c=0; c != width_; ++c)
    {
        // column c in the uncompacted matrix begins at this offset
        unsigned int start = col_offsets_[c];
        
        // column c in the compacted matrix begins at the next location
        // after the compacted nonzero elements
        col_offsets_[c] = nz_count;

        // column c in the uncompacted matrix ends at this offset
        unsigned int end = col_offsets_[c+1];

        for (unsigned int offset=start; offset != end; ++offset)
        {
            T val = data_[offset];
            if (std::abs(val) > epsilon)
            {
                // keep this value
                row_indices_[nz_count] = row_indices_[offset];
                data_[nz_count] = val;
                ++nz_count;
            }
        }
    }

    col_offsets_[width_] = nz_count;
    size_ = nz_count;
}

//-----------------------------------------------------------------------------
template <typename T>
void SparseMatrix<T>::NonZeroRowIndices(std::set<unsigned int>& row_index_set,
                                        const T& epsilon)
{
    row_index_set.clear();

    // save indices of rows with values > epsilon
    for (unsigned int s=0; s<size_; ++s)
    {
        T val = data_[s];
        if (std::abs(val) > epsilon)
        {
            unsigned int row = row_indices_[s];
            row_index_set.insert(row);
        }
    }
}

//-----------------------------------------------------------------------------
template <typename T>
void SparseMatrix<T>::SubMatrixCols(SparseMatrix<T>& result,
                                    const std::vector<unsigned int>& col_indices) const
{
    // extract entire columns from the source matrix to form the dest matrix

    unsigned int new_width = col_indices.size();
    if (0u == new_width)
        throw std::logic_error("SparseMatrix: empty column set");
    
    // check the column indices for validty and count nonzeros

    unsigned int new_size = 0;
    for (auto it=col_indices.begin(); it != col_indices.end(); ++it)
    {
        // index of next source column
        unsigned int c = *it;
        if (c >= width_)
            throw std::logic_error("SparseMatrix::SubMatrix: column index out of range");
        
        // number of nonzeros in source column c
        new_size += (col_offsets_[c+1] - col_offsets_[c]);
    }

    if (0u == new_size)
        throw std::logic_error("SparseMatrix::SubMatrix: submatrix is the zero matrix");

    // allocate memory in the result; won't allocate if sufficient memory available
    result.Reserve(height_, new_width, new_size);

    unsigned int* cols_b = result.ColBuffer();
    unsigned int* rows_b = result.RowBuffer();
    T* data_b            = result.DataBuffer();

    unsigned int c_dest = 0;
    unsigned int elt_count = 0;
    for (auto it=col_indices.begin(); it != col_indices.end(); ++it)
    {
        // index of the next source column
        unsigned int c = *it;

        // set element offset for the next dest column
        cols_b[c_dest] = elt_count;

        unsigned int start = col_offsets_[c];
        unsigned int end   = col_offsets_[c+1];
        for (unsigned int offset = start; offset != end; ++offset)
        {
            rows_b[elt_count] = row_indices_[offset];
            data_b[elt_count] = data_[offset];
            ++elt_count;
        }

        // have now completed another column
        ++c_dest;
    }

    cols_b[new_width] = elt_count;
    assert(new_width == c_dest);

    // set the size of the new matrix explicitly, since Load() has been bypassed
    result.SetSize(elt_count);
}

//-----------------------------------------------------------------------------
template <typename T>
void SparseMatrix<T>::SubMatrixColsCompact(SparseMatrix<T>& result,
                                           const std::vector<unsigned int>& col_indices,
                                           std::vector<unsigned int>& old_to_new_rows,
                                           std::vector<unsigned int>& new_to_old_rows) const
{
    const unsigned int UNUSED_ROW = 0xFFFFFFFF;

    // extract entire columns from the source matrix to form the dest matrix

    unsigned int new_width = col_indices.size();
    if (0u == new_width)
        throw std::logic_error("SparseMatrix::SubMatrixColsCompact: empty column set");
    
    // need one entry per original row in the row_map
    if (old_to_new_rows.size() < height_)
        old_to_new_rows.resize(height_);

    std::fill(old_to_new_rows.begin(), old_to_new_rows.begin() + height_, UNUSED_ROW);
    // no need to fill 'new_to_old_rows'

    // check the column indices for validty and count nonzeros

    unsigned int new_size = 0;
    for (auto it=col_indices.begin(); it != col_indices.end(); ++it)
    {
        // index of next source column
        unsigned int c = *it;
        if (c >= width_)
            throw std::logic_error("SparseMatrix::SubMatrixColsCompact: column index out of range");
        
        // number of nonzeros in source column c
        new_size += (col_offsets_[c+1] - col_offsets_[c]);
    }

    if (0u == new_size)
        throw std::logic_error("SparseMatrix::SubMatrixColsCompact: submatrix is the zero matrix");

    // allocate memory in the result; won't allocate if sufficient memory available
    result.Reserve(height_, new_width, new_size);

    unsigned int* cols_b = result.ColBuffer();
    unsigned int* rows_b = result.RowBuffer();
    T* data_b            = result.DataBuffer();

    unsigned int c_dest = 0;
    unsigned int elt_count = 0;
    for (auto it=col_indices.begin(); it != col_indices.end(); ++it)
    {
        // index of the next source column
        unsigned int c = *it;

        // set element offset for the next dest column
        cols_b[c_dest] = elt_count;

        unsigned int start = col_offsets_[c];
        unsigned int end   = col_offsets_[c+1];
        for (unsigned int offset = start; offset != end; ++offset)
        {
            unsigned int row = row_indices_[offset];
            old_to_new_rows[row] = row;
            rows_b[elt_count] = row;
            data_b[elt_count] = data_[offset];
            ++elt_count;
        }

        // have now completed another column
        ++c_dest;
    }

    cols_b[new_width] = elt_count;
    assert(new_width == c_dest);

    // set the size of the new matrix explicitly, since Load() has been bypassed
    result.SetSize(elt_count);

    // determine the new height of the submatrix
    unsigned int new_height = 0;
    for (unsigned int r=0; r != height_; ++r)
    {
        if (UNUSED_ROW != old_to_new_rows[r])
            ++new_height;
    }
    
    new_to_old_rows.resize(new_height);

    // renumber the rows in the submatrix

    unsigned int new_r = 0;
    for (unsigned int r=0; r<height_; ++r)
    {
        if (UNUSED_ROW != old_to_new_rows[r])
        {
            old_to_new_rows[r] = new_r;
            new_to_old_rows[new_r] = r;
            ++new_r;
        }
    }

    // set the height of the new matrix explicitly
    assert(new_r == new_height);
    result.SetHeight(new_height);

    // re-index the rows in the submatrix 
    for (unsigned int s=0; s != elt_count; ++s)
    {
        unsigned int old_row_index = rows_b[s];
        rows_b[s] = old_to_new_rows[old_row_index];
    }

    assert(result.Height() == new_height);
    assert(new_to_old_rows.size() == new_height);
    assert(old_to_new_rows.size() == height_);
}

//-----------------------------------------------------------------------------
template <typename T>
void SparseMatrix<T>::SubMatrixRowsCompact(const std::vector<unsigned int>& col_indices,
                                           std::vector<unsigned int>& old_to_new_rows,
                                           std::vector<unsigned int>& new_to_old_rows) const
{
    const unsigned int UNUSED_ROW = 0xFFFFFFFF;

    unsigned int new_width = col_indices.size();
    if (0u == new_width)
        throw std::logic_error("SparseMatrix::SubMatrixRowsCompact empty column set");
    
    // need one entry per original row in the row_map
    if (old_to_new_rows.size() < height_)
        old_to_new_rows.resize(height_);

    std::fill(old_to_new_rows.begin(), old_to_new_rows.begin() + height_, UNUSED_ROW);
    // no need to fill 'new_to_old_rows'

    // check the column indices for validty and determine new matrix size
    unsigned int new_size = 0;
    for (auto it=col_indices.begin(); it != col_indices.end(); ++it)
    {
        // index of next source column
        unsigned int c = *it;
        if (c >= width_)
            throw std::logic_error("SparseMatrix::SubMatrixRowsCompact: column index out of range");
        
        // number of nonzeros in source column c
        new_size += (col_offsets_[c+1] - col_offsets_[c]);
    }

    if (0u == new_size)
        throw std::logic_error("SparseMatrix::SubMatrixRowsCompact: submatrix is the zero matrix");

    unsigned int c_dest = 0;
    unsigned int elt_count = 0;
    for (auto it=col_indices.begin(); it != col_indices.end(); ++it)
    {
        // index of the next source column
        unsigned int c = *it;

        unsigned int start = col_offsets_[c];
        unsigned int end   = col_offsets_[c+1];
        for (unsigned int offset = start; offset != end; ++offset)
        {
            unsigned int row = row_indices_[offset];
            old_to_new_rows[row] = row;
            ++elt_count;
        }

        // have now completed another column
        ++c_dest;
    }

    assert(new_width == c_dest);

    // determine the new height of the submatrix
    unsigned int new_height = 0;
    for (unsigned int r=0; r != height_; ++r)
    {
        if (UNUSED_ROW != old_to_new_rows[r])
            ++new_height;
    }
    
    new_to_old_rows.resize(new_height);

    // re-index the rows for the (virtual) new matrix
    unsigned int new_r = 0;
    for (unsigned int r=0; r<height_; ++r)
    {
        if (old_to_new_rows[r] != UNUSED_ROW)
        {
            old_to_new_rows[r] = new_r;
            new_to_old_rows[new_r] = r;
            ++new_r;
        }
    }

    assert(new_to_old_rows.size() == new_height);
    assert(old_to_new_rows.size() == height_);
}
