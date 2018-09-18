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

#include <cstdint>
#include <limits>
#include <cassert>
#include <algorithm>
#include <stdexcept>
#include <sstream>
#include <cmath>
#include <map>
#include <iostream>
#include <fstream>
#include <algorithm>
#include "term_frequency_matrix.hpp"
#include "matrix_market_file.hpp"

using std::cout;
using std::endl;

//-----------------------------------------------------------------------------
unsigned int TermFrequencyMatrix::Size() const
{
    assert(col_offsets_[width_] == size_);
    return col_offsets_[width_];
}

//-----------------------------------------------------------------------------
TermFrequencyMatrix::TermFrequencyMatrix()
    : height_(0), width_(0), size_(0), capacity_(0)
{
}

//-----------------------------------------------------------------------------
TermFrequencyMatrix::TermFrequencyMatrix(const SparseMatrix<double>& S,
                                         bool boolean_mode)
{
    Init(S, boolean_mode);
}

//-----------------------------------------------------------------------------
void TermFrequencyMatrix::Init(const SparseMatrix<double>& S,
                               bool boolean_mode)
{
    height_ = S.Height();
    width_ = S.Width();
    size_ = S.Size();
    capacity_ = size_;

    col_offsets_.reserve(width_ + 1);
    tf_data_.reserve(size_);

    const unsigned int* source_cols = S.LockedColBuffer();
    const unsigned int* source_rows = S.LockedRowBuffer();
    const double* source_data       = S.LockedDataBuffer();

    unsigned int index = 0;
    for (unsigned int c=0; c != width_; ++c)
    {
        unsigned int start = source_cols[c];
        unsigned int end   = source_cols[c+1];

        // the offset is the same in both arrays, thanks to ptr indexing
        col_offsets_[c] = start;

        for (unsigned int offset=start; offset != end; ++offset)
        {
            tf_data_[index].row = source_rows[offset];

            // Set any negative values to 0 and truncate any fractions.
            if (boolean_mode)
                tf_data_[index].count = 1;
            else
            {
                double val = source_data[offset];
                if (val < 0.0)
                    tf_data_[index].count = 0;
                else
                    tf_data_[index].count = static_cast<unsigned int>(val);
            }

            ++index;
        }
    }

    col_offsets_[width_] = source_cols[width_];
    assert(index = size_);
    assert(col_offsets_[width_] == size_);
}

//-----------------------------------------------------------------------------
void TermFrequencyMatrix::Print(const std::string& msg)
{
    std::cout << msg << std::endl;
    std::cout << "Height: " << height_ << ", width: " << width_ 
              << ", size: " << size_ << ", capacity: " << capacity_ << endl;

    std::vector<unsigned int> data(height_ * width_, 0);
    for (unsigned int c=0; c != width_; ++c)
    {
        unsigned int start = col_offsets_[c];
        unsigned int end   = col_offsets_[c+1];
        for (unsigned int offset=start; offset != end; ++offset)
        {
            unsigned int r = tf_data_[offset].row;
            data[r*width_ + c] = tf_data_[offset].count;
        }
    }

    for (unsigned int r=0; r != height_; ++r)
    {
        for (unsigned int c=0; c != width_; ++c)
        {
            cout << data[r*width_ + c] << ' ';
        }
        cout << endl;
    }

    std::cout << "Col indices: "; std::cout.flush();
    for (unsigned int i=0; i != width_; ++i)
        std::cout << col_offsets_[i] << ", ";
    std::cout << col_offsets_[width_] << std::endl;

    std::cout << "TF Data: "; std::cout.flush();
    for (unsigned int i=0; i != size_; ++i)
        std::cout << "{" << tf_data_[i].row << ", " 
                  << tf_data_[i].count << "}, ";
    std::cout << std::endl;    
}

//-----------------------------------------------------------------------------
void TermFrequencyMatrix::SortRows()
{
    for (unsigned int c=0; c != width_; ++c)
    {
        unsigned int start = col_offsets_[c];
        unsigned int end   = col_offsets_[c+1];
        std::sort(&tf_data_[start], &tf_data_[end],
                  [](const TFData& d1, const TFData& d2)
                  {
                      return d1.row < d2.row;
                  });
    }
}

//-----------------------------------------------------------------------------
bool TermFrequencyMatrix::CompareAsBoolean(const TermFrequencyMatrix& rhs) const
{
    if (height_ != rhs.Height())
        return false;
    if (width_ != rhs.Width())
        return false;
    if (size_ != rhs.Size())
        return false;

    for (unsigned int c=0; c != width_; ++c)
    {
        if (col_offsets_[c] != rhs.col_offsets_[c])
            return false;

        unsigned int start1 = col_offsets_[c];
        unsigned int end1   = col_offsets_[c+1];
        unsigned int nz1    = end1 - start1;

        unsigned int start2 = rhs.col_offsets_[c];
        unsigned int end2   = rhs.col_offsets_[c+1];
        unsigned int nz2    = end2 - start2;

        if (nz1 != nz2)
            return false;
    }

    return true;
}

//-----------------------------------------------------------------------------
bool TermFrequencyMatrix::operator==(const TermFrequencyMatrix& rhs) const
{
    if (height_ != rhs.Height())
        return false;
    if (width_ != rhs.Width())
        return false;
    if (size_ != rhs.Size())
        return false;

    unsigned int unequal_col_count = 0;
    for (unsigned int c=0; c != width_; ++c)
    {
        if (col_offsets_[c] != rhs.col_offsets_[c])
        {
            ++unequal_col_count;
            continue;
            //cout << "TermFrequencyMatrix::operator==: unequal col_offsets "
            //    << "at col " << c << endl;
            //return false;
        }

        unsigned int start1 = col_offsets_[c];
        unsigned int end1   = col_offsets_[c+1];
        unsigned int nz1    = end1 - start1;

        unsigned int start2 = rhs.col_offsets_[c];
        unsigned int end2   = rhs.col_offsets_[c+1];
        unsigned int nz2    = end2 - start2;

        if (nz1 != nz2)
        {
            ++unequal_col_count;
            continue;
            //cout << "TermFrequencyMatrix::operator==: unequal nz values: "
            //     << " at column " << c << endl;
            //cout << "start1: " << start1 << ", start2: " << start2 
            //     << ", end1: " << end1   << ",   end2: " << end2
            //     << ", nz1: "  << nz1    << ",    nz2: " << nz2 << endl;
            //return false;
        }

        unsigned int offset1 = start1;
        unsigned int offset2 = start2;
        for (; offset1 != end1; ++offset1, ++offset2)
        {
            if (tf_data_[offset1] != tf_data_[offset2])
            {
                ++unequal_col_count;
                break;
                //return false;
            }
        }
    }
    
    //cout << "TermFrequencyMatrix::operator==: unequal_col_count = " << unequal_col_count << endl;

    return (unequal_col_count == 0);
}

//-----------------------------------------------------------------------------
bool TermFrequencyMatrix::operator!=(const TermFrequencyMatrix& rhs) const
{
    return !(this->operator==(rhs));
}

//-----------------------------------------------------------------------------
bool TermFrequencyMatrix::WriteMtxFile(const std::string& file_path)
{
    // Write a MatrixMarket file with no comments.  Note that the
    // MatrixMarket format uses 1-based indexing for rows and columns.

    std::ofstream outfile(file_path);
    if (!outfile)
        return false;

    // write the 'banner'
    outfile << MM_BANNER << " matrix coordinate integer general" << std::endl;

    // write matrix dimensions and number of nonzeros
    outfile << height_ << " " << width_ << " " << size_ << std::endl;

    for (unsigned int c=0; c != width_; ++c)
    {
        unsigned int start = col_offsets_[c];
        unsigned int end   = col_offsets_[c+1];
        for (unsigned int offset=start; offset != end; ++offset)
        {
            unsigned int r = tf_data_[offset].row;
            double count = tf_data_[offset].count;
            outfile << r+1 << " " << c+1 << " " << count << std::endl;
        }
    }

    outfile.close();
    return true;
}

//-----------------------------------------------------------------------------
bool TermFrequencyMatrix::WriteMtxFile(const std::string& file_path, 
                                       const double* scores,
                                       const unsigned int precision)
{
    // Write a MatrixMarket file with no comments.  Note that the
    // MatrixMarket format uses 1-based indexing for rows and columns.

    std::ofstream outfile(file_path);
    if (!outfile)
        return false;

    // write the 'banner'
    outfile << MM_BANNER << " matrix coordinate real general" << std::endl;

    // write matrix dimensions and number of nonzeros
    outfile << height_ << " " << width_ << " " << size_ << std::endl;

    outfile << std::fixed;
    outfile.precision(precision);
    
    for (unsigned int c=0; c != width_; ++c)
    {
        unsigned int start = col_offsets_[c];
        unsigned int end   = col_offsets_[c+1];
        for (unsigned int offset=start; offset != end; ++offset)
        {
            unsigned int r = tf_data_[offset].row;
            double val = scores[offset];
            outfile << r+1 << " " << c+1 << " " << val << std::endl;
        }
    }

    outfile.close();
    return true;
}

