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

#include <string>
#include <sstream>
#include <fstream>
#include <iostream>
#include "matrix_market_file.hpp"

//-----------------------------------------------------------------------------
template <typename T>
void Print(const SparseMatrix<T>& M)
{
    // Print a SparseMatrix to the screen.

    const unsigned int* col_buf = M.LockedColBuffer();
    const unsigned int* row_buf = M.LockedRowBuffer();
    const T*                buf = M.LockedDataBuffer();

    if (0 == M.Size())
    {
        std::cout << "Matrix is empty." << std::endl;
        return;
    }

    for (unsigned int c=0; c != M.Width(); ++c)
    {
        unsigned int start = col_buf[c];
        unsigned int end   = col_buf[c+1];
        for (unsigned int offset=start; offset != end; ++offset)
        {
            assert(offset >= 0);
            assert(offset < M.Size());
            unsigned int row_index = row_buf[offset];
            T                 data = buf[offset];
            std::cout << "(" << row_index << ", " << c << "): " << data << std::endl;
        }
    }

    std::cout << "Col indices: "; std::cout.flush();
    for (unsigned int i=0; i != M.Width(); ++i)
        std::cout << col_buf[i] << ", ";
    std::cout << col_buf[M.Width()] << std::endl;

    std::cout << "Row indices: "; std::cout.flush();
    for (unsigned int i=0; i != M.Size(); ++i)
        std::cout << row_buf[i] << ", ";
    std::cout << std::endl;

    std::cout << "Data:        "; std::cout.flush();
    for (unsigned int i=0; i != M.Size(); ++i)
        std::cout << buf[i] << ", ";
    std::cout << std::endl;
}

//-----------------------------------------------------------------------------
template <typename T>
bool WriteMatrixMarketFile(const std::string& file_path,
                           const SparseMatrix<T>& A,
                           const unsigned int precision)
{
    // Write a MatrixMarket file with no comments.  Note that the
    // MatrixMarket format uses 1-based indexing for rows and columns.

    std::ofstream outfile(file_path);
    if (!outfile)
        return false;

    unsigned int height = A.Height();
    unsigned int width  = A.Width();
    unsigned int nnz    = A.Size();
    
    // write the 'banner'
    outfile << MM_BANNER << " matrix coordinate real general" << std::endl;

    // write matrix dimensions and number of nonzeros
    outfile << height << " " << width << " " << nnz << std::endl;

    outfile << std::fixed;
    outfile.precision(precision);
    
    const unsigned int* cols_a = A.LockedColBuffer();
    const unsigned int* rows_a = A.LockedRowBuffer();
    const T*            data_a = A.LockedDataBuffer();
    unsigned int width_a = A.Width();

    for (unsigned int c=0; c != width_a; ++c)
    {
        unsigned int start = cols_a[c];
        unsigned int end   = cols_a[c+1];
        for (unsigned int offset=start; offset != end; ++offset)
        {
            unsigned int r = rows_a[offset];
            T val = data_a[offset];
            outfile << r+1 << " " << c+1 << " " << val << std::endl;
        }
    }

    outfile.close();
    return true;
}

//-----------------------------------------------------------------------------
template <typename T>
bool LoadMatrixMarketFile(const std::string& file_path, 
                          SparseMatrix<T>& A,
                          unsigned int& height,
                          unsigned int& width,
                          unsigned int& nnz)
{
    std::ifstream infile(file_path);
    if (!infile)
        return false;

    char mm_typecode[4];

    // read the matrix market banner (header)
    if (0 != mm_read_banner(infile, mm_typecode))
        return false;

    if (!mm_is_valid(mm_typecode))
        return false;

    // this reader supports these matrix types:
    //
    //  sparse, real/integer/pattern, general/symm/skew
    //

    if (!mm_is_sparse(mm_typecode))
    {
        std::cerr << "Only sparse MatrixMarket files are supported." << std::endl;
        return false;
    }

    if (!mm_is_real(mm_typecode) && !mm_is_integer(mm_typecode) && !mm_is_pattern(mm_typecode))
    {
        std::cerr << "Only real, integer, and pattern MatrixMarket formats are supported." << std::endl;
        return false;
    }

    if (!mm_is_general(mm_typecode) && !mm_is_symmetric(mm_typecode) && !mm_is_skew(mm_typecode))
    {
        std::cerr << "Only general, symmetric, and skew-symmetric MatrixMarket formats are supported." 
                  << std::endl;
        return false;
    }

    // read the number of rows, cols, nonzeros
    if (0 != mm_read_mtx_crd_size(infile, height, width, nnz))
    {
        std::cerr << "could not read matrix coordinate information" << std::endl;
        height = width = nnz = 0;
        return false;
    }

    // read the data according to the type 

    bool is_real      = mm_is_real(mm_typecode);
    bool is_int       = mm_is_integer(mm_typecode);
    bool is_symmetric = mm_is_symmetric(mm_typecode);
    bool is_skew      = mm_is_skew(mm_typecode);

    unsigned int reserve_size = nnz;
    if (is_symmetric || is_skew)
        reserve_size *= 2;

    A.Clear();
    A.Reserve(height, width, reserve_size);

    // load num random entries of A
    A.BeginLoad();

    T val;
    std::string line;    
    unsigned int row, col, line_count = 0;

    // read the nonzero entries of the matrix, one per line
    
    // Note: the number of nonzero entries is NOT necessarily equal
    // to the SUM of the nonzero entries.  We only want the number
    // of nonzero entries, not their sum.
    
    while (std::getline(infile, line))
    {
        ++line_count;
        
        if (!infile)
            break;

        if (line.empty())
            continue;
        
        std::istringstream data(line);

        data >> row;
        data >> col;

        // the 'pattern' format has no data value
        if (is_real || is_int)
        {
            data >> val;
        }
        else
        {
            val = T(1.0);
        }

        // convert to 0-based indexing
        if ( (row <= 0) || (col <= 0))
        {
            std::stringstream msg;
            msg << "\nError reading file " << file_path << std::endl;
            msg << "Line " << line << " contains an invalid index.";
            std::cerr << msg.str() << std::endl;
            return false;
        }

        row -= 1;
        col -= 1;
        A.Load(row, col, val);

        if (row != col)
        {
            if (is_symmetric)
                A.Load(col, row, val);
            else if (is_skew)
                A.Load(col, row, -val);
        }
    }
    
    A.EndLoad();

    if (line_count != nnz)
    {
        std::stringstream msg;
        msg << "\nError reading file " << file_path << std::endl;
        msg << "Found " << line_count << " nonzero entries, expected " << nnz;
        std::cerr << msg.str() << std::endl;
        return false;
    }

    return true;
}



//-----------------------------------------------------------------------------
template <typename T>
void LoadSparseMatrix(const unsigned int height, 
                    const unsigned int width,
                    const unsigned int nz, 
                    const std::vector<T>& data,
                    const std::vector<unsigned int>& row_indices,
                    const std::vector<unsigned int>& col_offsets,
                    SparseMatrix<T>& A)

{

    std::cout << "Loading sparse matrix..." << std::endl;

    // ensure that row_indices is the same size as data
    if (row_indices.size() != data.size())
    {
        std::ostringstream msg;
        msg << "smallk error (LoadSparseMatrix): invalid input vectors.";
        throw std::runtime_error(msg.str());
    }

    // ensure that data is valid
    if (0 == height)
    {
        std::ostringstream msg;
        msg << "smallk error (LoadSparseMatrix): invalid height input.";
        throw std::runtime_error(msg.str());
    }
    if (0 == width)
    {
        std::ostringstream msg;
        msg << "smallk error (LoadSparseMatrix): invalid width input.";
        throw std::runtime_error(msg.str());
    }
    if (data.size() > height*width)
    {
        std::ostringstream msg;
        msg << "smallk error (LoadSparseMatrix): invalid inputs.";
        throw std::runtime_error(msg.str());
    }
    if (data.empty())
    {
        std::ostringstream msg;
        msg << "smallk error (LoadSparseMatrix): empty data vector.";
        throw std::runtime_error(msg.str());
    }
    if (row_indices.empty())
    {
        std::ostringstream msg;
        msg << "smallk error (LoadSparseMatrix): empty row_indices vector.";
        throw std::runtime_error(msg.str());
    }
    if (col_offsets.empty())
    {
        std::ostringstream msg;
        msg << "smallk error (LoadSparseMatrix): empty col_offsets vector.";
        throw std::runtime_error(msg.str());
    }
    A = SparseMatrix<T>(height, width, nz, &col_offsets[0], &row_indices[0], &data[0]);
        
}

