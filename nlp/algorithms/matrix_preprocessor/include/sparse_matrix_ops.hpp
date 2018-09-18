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

#include <stdexcept>

//-----------------------------------------------------------------------------
template <typename T>
bool HasNaNs(const SparseMatrix<T>& A)
{
    // return true if any element is NaN
    unsigned int nz = A.Size();
    const T* data = A.LockedDataBuffer();
    for (unsigned int i=0; i != nz; ++i)
    {
        if (std::isnan(data[i]))
            return true;
    }

    return false;
}

//-----------------------------------------------------------------------------
template <typename T>
void Transpose(const SparseMatrix<T>& A, SparseMatrix<T>& B)
{
    // Compute the transpose of A and return in B.

    const unsigned int* cols_a = A.LockedColBuffer();
    const unsigned int* rows_a = A.LockedRowBuffer();
    const T*            data_a = A.LockedDataBuffer();

    // will not reallocate if sufficient space is available in B
    B.Reserve(A.Width(), A.Height(), A.Size());

    unsigned int* cols_b = B.ColBuffer();
    unsigned int* rows_b = B.RowBuffer();
    T*            data_b = B.DataBuffer();

    unsigned int nzmax   = A.Size();
    unsigned int width_a = A.Width();
    unsigned int width_b = B.Width();  // also height of A

    // Compute a histogram of the row indices of matrix A, then compute a
    // prefix sum for the histogram.  The prefix sum will be used in a 
    // counting sort below.  The prefix sum can also be copied directly into 
    // cols_b, but shifted by one position, since the CSC format requires a 
    // zero element in the first position, and the column index array has 
    // (width_b + 1) elements.

    std::vector<unsigned int> counts(width_b);
    Histogram(rows_a, rows_a + nzmax, counts.begin(), counts.end());
    PrefixSum(counts.begin(), counts.end());
    std::copy(counts.begin(), counts.end(), &cols_b[1]);
    cols_b[0] = 0;

    // The cols_b array for the transposed matrix is now complete.

    // The interpretation of the 'counts' array is as follows: 
    // counts[i] is equal to the number of elements in rows_a that are 
    // less than or equal to i.

    // Now perform a counting sort on the elements in rows_a and data_a
    // simultaneously.  Traverse the arrays *BACKWARDS* for stability.
    // The indexing below works with unsigned ints and avoids wrap-around
    // at zero.  The result of this is that the row indices of the
    // destination matrix are sorted in nondecreasing order.

    unsigned int start, num_nonzero, offset_a, offset_b, row_index;
    for (unsigned int q=1; q <= width_a; ++q)
    {
        // column index for the source matrix
        unsigned int c = width_a - q;

        // the number of nonzero entries in column c
        start = cols_a[c];
        assert(cols_a[c+1] >= start);
        num_nonzero = cols_a[c+1] - start;

        // For each nonzero entry, compute offset_a, the offset into the 
        // rows_a and data_a arrays.  From this get the row index, then use
        // the cumulative sum in 'counts' to compute offset_b, the destination 
        // offset.  This offset is 1-based, so subtract 1 to get the true 
        // destination offset.  Note also that the elements are traversed
        // in reverse order.
        for (unsigned int k=1; k <= num_nonzero; ++k)
        {
            // offset into the source arrays
            offset_a = start + (num_nonzero - k);

            // the row index of the nonzero element at this offset
            row_index = rows_a[offset_a];
            assert(row_index >= 0);
            assert(row_index < A.Height());
            
            // destination offset + 1
            offset_b = counts[row_index];

            // If offset_b == 0, there are no entries in rows_a that are
            // less than or equal to row_index, which means that this
            // index does not exist in column c.  This situation occurs with 
            // counting sort whenever the N elements being sorted only contain 
            // a subset of the range 0..(N-1) that excludes 0.
            if (0 == offset_b)
                continue;

            rows_b[offset_b-1] = c;
            data_b[offset_b-1] = data_a[offset_a];

            // one fewer element in the source array <= row_index
            counts[row_index] -= 1;
        }
    }
}

//-----------------------------------------------------------------------------
template <typename T>
void Scal(const T& alpha, SparseMatrix<T>& X)
{
    // Compute X = alpha*X
    //     X is a sparse matrix
    //     alpha is a real constant

    T* data_X = X.DataBuffer();
    const int nzmax = X.Size();

    for (unsigned int i=0; i != nzmax; ++i)
        data_X[i] *= alpha;
}

//-----------------------------------------------------------------------------
template <typename T>
unsigned int Scatter(const SparseMatrix<T>& A,
                     const unsigned int col_index,
                     const T& val,
                     unsigned int* w,
                     T* x,
                     const unsigned int mark,
                     SparseMatrix<T>& C,
                     const unsigned int nonzeros_c)
{
    // This is a rewrite of the SuiteSparse algorithm 'cs_scatter'.

    unsigned int nz = nonzeros_c;
    const unsigned int* cols_a = A.LockedColBuffer();
    const unsigned int* rows_a = A.LockedRowBuffer();
    const T*            data_a = A.LockedDataBuffer();
    unsigned int*       rows_c = C.RowBuffer();

    for (unsigned int offset = cols_a[col_index]; offset != cols_a[col_index+1]; ++offset)
    {
        unsigned int row_index = rows_a[offset];
        //std::cout << "A(" << row_index << ", " << col_index << "): " << data_a[offset] << std::endl;
        if (w[row_index] < mark)
        {
            // have not seen this entry yet
            w[row_index] = mark;

            // product has a nonzero at this row index
            rows_c[nz++] = row_index;
            x[row_index] = val * data_a[offset];
        }
        else
        {
            x[row_index] += val * data_a[offset];
        }
    }

    return nz;
}

//-----------------------------------------------------------------------------
template <typename T>
void Multiply(const SparseMatrix<T>& A, 
              const SparseMatrix<T>& B, 
              SparseMatrix<T>& C)
{
    // C = A * B

    // This is a rewrite of the SuiteSparse algorithm 'cs_multiply'.
    const unsigned int* cols_b = B.LockedColBuffer();
    const unsigned int* rows_b = B.LockedRowBuffer();
    const T*            data_b = B.LockedDataBuffer();

    // will not reallocate if sufficient memory is available in C
    C.Reserve(A.Height(), B.Width(), A.Size() + B.Size());

    unsigned int* cols_c = C.ColBuffer();
    unsigned int* rows_c = C.RowBuffer();
    T*            data_c = C.DataBuffer();

    unsigned int nonzeros_c = 0;
    unsigned int height_c = C.Height();
    unsigned int width_c = C.Width();

    // allocate workspaces
    std::vector<unsigned int> w(height_c, 0u);
    std::vector<T>            x(height_c);

    // outer loop iterates over each column of the product matrix C
    for (unsigned int c=0; c<width_c; ++c)
    {
        // could add as many as height_c nonzeros; check space
        if (nonzeros_c + height_c > C.Capacity())
        {
            C.Reserve(height_c, width_c, 2*C.Capacity() + height_c);
            cols_c = C.ColBuffer();
            rows_c = C.RowBuffer();
            data_c = C.DataBuffer();
        }

        cols_c[c] = nonzeros_c;

        // iterate over the elements in the cth column of B
        unsigned int start = cols_b[c];
        unsigned int end   = cols_b[c+1];
        for (unsigned int offset = start; offset != end; ++offset)
        {
            // get the next nonzero element: B(row_index, c)
            unsigned int row_index = rows_b[offset];
            T data_val             = data_b[offset];
            
            //std::cout << "B(" << row_index << ", " << c << "): " << data_b[offset] << std::endl;
            nonzeros_c = Scatter(A, row_index, data_val, &w[0], &x[0], c+1, C, nonzeros_c);
        }

        // copy result into result matrix
        for (unsigned int offset = cols_c[c]; offset < nonzeros_c; ++offset)
            data_c[offset] = x[rows_c[offset]];
    }

    cols_c[width_c] = nonzeros_c;
}

//-----------------------------------------------------------------------------
template <typename T>
void Add(const T& alpha,
         const SparseMatrix<T>& A, 
         const T& beta,
         const SparseMatrix<T>& B, 
         SparseMatrix<T>& C)
{
    // C = alpha*A + beta*B
    
    // This is a rewrite of the SuiteSparse algorithm 'cs_add'.

    // will not reallocate if sufficient memory is available in C
    C.Reserve(A.Height(), B.Width(), A.Size() + B.Size());

    unsigned int* cols_c = C.ColBuffer();
    unsigned int* rows_c = C.RowBuffer();
    T*            data_c = C.DataBuffer();

    unsigned int nonzeros_c = 0;
    unsigned int height_c = C.Height();
    unsigned int width_c = C.Width();

    // allocate workspaces
    std::vector<unsigned int> w(height_c, 0u);
    std::vector<T>            x(height_c);

    // outer loop iterates over each column of the product matrix C
    for (unsigned int c=0; c<width_c; ++c)
    {
        // working on the cth column, which begins here
        cols_c[c] = nonzeros_c;

        nonzeros_c = Scatter(A, c, alpha, &w[0], &x[0], c+1, C, nonzeros_c);
        nonzeros_c = Scatter(B, c, beta,  &w[0], &x[0], c+1, C, nonzeros_c);

        // copy result into result matrix
        for (unsigned int offset = cols_c[c]; offset < nonzeros_c; ++offset)
            data_c[offset] = x[rows_c[offset]];
    }

    cols_c[width_c] = nonzeros_c;
}

// //-----------------------------------------------------------------------------
// template <typename T>
// void Gaxpy(const SparseMatrix<T>& A, T* x, T* y)
// {
//     // compute y = Ax + y, where A is sparse and both x and y are dense

//     const unsigned int* cols_a = A.LockedColBuffer();
//     const unsigned int* rows_a = A.LockedRowBuffer();
//     const T*            data_a = A.LockedDataBuffer();
//     const unsigned int width_a = A.Width();
    
//     for (unsigned int c=0; c != width_a; ++c)
//     {
//         unsigned int start = cols_a[c];
//         unsigned int end   = cols_a[c+1];
//         T xc               = x[c];
//         for (unsigned int offset = start; offset != end; ++offset)
//         {
//             unsigned int row = rows_a[offset];
//             y[row] += data_a[offset] * xc;
//         }
//     }
// }

//-----------------------------------------------------------------------------
template <typename T>
void RandomSparseMatrix(Random& rng, SparseMatrix<T>& A, 
                        const unsigned int nonzeros_per_column,
                        const unsigned int min_height, const unsigned int max_height,
                        const unsigned int min_width, const unsigned int max_width)
{
    // Generate a random sparse matrix with 'nonzeros_per_column' nonzero
    // entries in each column.  The entries in each column are in random
    // rows.

    const unsigned int MAX_RETRIES = 256;
    const unsigned int UNUSED = 0xFFFFFFFF;

    std::vector<unsigned int> rows(max_height, 0);

    // generate a random height and width for the sparse matrix
    unsigned int height, width;
    if (min_height == max_height)
        height = min_height;
    else
        height = rng.RandomRangeInt(min_height, max_height);

    if (min_width == max_width)
        width = min_width;
    else
        width  = rng.RandomRangeInt(min_width, max_width);

    unsigned int nz_per_col = nonzeros_per_column;
    if (0 == nz_per_col)
        nz_per_col = 1;
    if (nz_per_col > height)
        nz_per_col = height;

    // aux vector of row indices
    for (unsigned int k=0; k != height; ++k)
        rows[k] = 0xFFFFFFFF;

    // working vector of used indices
    std::vector<unsigned int> used_indices(nz_per_col);

    unsigned int nnz = nz_per_col * width;

    A.Clear();
    A.Reserve(height, width, nnz);
    A.BeginLoad();
    
    for (unsigned int c=0; c != width; ++c)
    {
        // Generate row indices in random order with no duplicates.  A random
        // shuffle of the 'rows' array would work, but it would be extremely
        // slow for large matrices.  So generate 'nz_per_col' random row 
        // indices on [0, height), but be careful to not have any duplicate
        // indices in any single column.
        
        for (unsigned int k=0; k != nz_per_col; ++k)
        {
            unsigned int r = UNUSED;
            for (unsigned int q=0; q<MAX_RETRIES; ++q)
            {
                // generate a random row index on [0, height)
                r = rng.RandomRangeInt(0, height);

                // if r has not already been used for column c, 
                // mark it as being 'in use' and exit
                if (UNUSED == rows[r])
                {
                    // can store anything other than UNUSED here
                    rows[r] = r;
                    used_indices[k] = r;
                    break;
                }
            }

            if (UNUSED == r)
                throw std::runtime_error("row index generation failed after max retries");
            
            // generate random value on (0, 1)
            double val = rng.RandomDouble(0.5, 0.5);

            // load into matrix
            A.Load(r, c, val);
        }

        // finished with column c, so mark all indices as unused again
        for (unsigned int q=0; q != nz_per_col; ++q)
            rows[used_indices[q]] = UNUSED;
    }
    
    A.EndLoad();
}

