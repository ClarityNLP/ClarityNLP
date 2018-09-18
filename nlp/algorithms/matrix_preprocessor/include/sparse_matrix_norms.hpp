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

//-----------------------------------------------------------------------------
template <typename T>
T MaxNorm(const SparseMatrix<T>& A)
{
    // find max( |A_ij| )
    const T*           data_a = A.LockedDataBuffer();
    const unsigned int size_a = A.Size();

    T max_norm = T(0);
    for (unsigned int i=0; i != size_a; ++i)
    {
        T val = fabs(data_a[i]);
        if (val > max_norm)
            max_norm = val;
    }

    return max_norm;
}

//-----------------------------------------------------------------------------
template <typename T>
T OneNorm(const SparseMatrix<T>& A)
{
    // compute the max absolute column sum
    const unsigned int* cols_a = A.LockedColBuffer();
    const T*            data_a = A.LockedDataBuffer();
    const unsigned int width_a = A.Width();

    T max_col_sum = T(0), col_sum;
    for (unsigned int c=0; c != width_a; ++c)
    {
        unsigned int start = cols_a[c];
        unsigned int   end = cols_a[c+1];
        col_sum = T(0);
        for (unsigned int offset=start; offset != end; ++offset)
        {
            T val = fabs(data_a[offset]);
            col_sum += val;
        }

        if (col_sum > max_col_sum)
            max_col_sum = col_sum;
    }

    return max_col_sum;
}

//-----------------------------------------------------------------------------
template <typename T>
T InfinityNorm(const SparseMatrix<T>& A)
{
    // the infinity norm is the max absolute row sum; easier to transpose first
    // and return the one norm of the transpose
    SparseMatrix<T> Atranspose;
    Transpose(A, Atranspose);
    return OneNorm(Atranspose);
}

//-----------------------------------------------------------------------------
template <typename T>
T FrobeniusNorm(const SparseMatrix<T>& A)
{
    // compute the sum of the absolute value squared of each element
    const T*           data_a = A.LockedDataBuffer();
    const unsigned int size_a = A.Size();

    T sum = T(0);
    for (unsigned int i=0; i != size_a; ++i)
    {
        T val = fabs(data_a[i]);
        sum += val*val;
    }

    return sqrt(sum);
}

