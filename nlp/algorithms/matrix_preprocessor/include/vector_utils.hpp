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

#include <iostream>
#include <iterator>
#include <algorithm>
#include <cassert>
#include <stdexcept>

//-----------------------------------------------------------------------------
template <typename T>
std::vector<T> operator + (const std::vector<T>& A, const std::vector<T>& B)
{
    const unsigned int size_a = A.size();

    if (B.size() != size_a)
        throw std::logic_error("operator+: vector size mismatch");

    std::vector<T> result(size_a);

    for (unsigned int i=0; i != size_a; ++i)
        result[i] = A[i] + B[i];

    return result;
}

//-----------------------------------------------------------------------------
template <typename T>
void operator += (std::vector<T>& A, const std::vector<T>& B)
{
    const unsigned int size_a = A.size();

    if (B.size() != size_a)
        throw std::logic_error("operator+=: vector size mismatch");

    for (unsigned int i=0; i != size_a; ++i)
        A[i] += B[i];
}

//-----------------------------------------------------------------------------
template <typename T>
void operator -= (std::vector<T>& A, const T val)
{
    const unsigned int size_a = A.size();
    for (unsigned int i=0; i != size_a; ++i)
        A[i] -= val;
}

//-----------------------------------------------------------------------------
template <typename T>
T Sum(std::vector<T>& A)
{
    T result = T(0);
    for (unsigned int q=0u; q<A.size(); ++q)
        result += A[q];
    return result;
}

//-----------------------------------------------------------------------------
template <typename T>
void PrintVector(const T* data, const unsigned int N)
{
    if (0 == N)
        return;

    for (unsigned int i=0; i != N-1; ++i)
    {
        std::cout << data[i] << ", ";
    }
    std::cout << data[N-1] << std::endl;
}

//-----------------------------------------------------------------------------
template <typename T1, typename T2>
void Histogram(T1 src_begin,
               T1 src_end,
               T2 histogram_begin,
               T2 histogram_end)
{
    typedef typename std::iterator_traits<T1>::value_type value_type;
    typedef typename std::iterator_traits<T2>::difference_type difference_type_hist;

    // number of bins
    difference_type_hist num_bins = histogram_end - histogram_begin;

    // zero the histogram array
    std::fill(histogram_begin, histogram_end, 0);

    // bin the values
    for (T1 it=src_begin; it != src_end; ++it)
    {
        value_type value = *it;
        assert(value >= 0);
        assert(value < num_bins);
        histogram_begin[value] += 1;
    }
}

//-----------------------------------------------------------------------------
template <typename T>
void PrefixSum(T src_begin, T src_end)
{
    // src[1] += src[0]
    // src[2] += src[1]
    // etc.

    typedef typename std::iterator_traits<T>::difference_type difference_type;

    for (T it = (src_begin+1); it != src_end; ++it)
    {
        difference_type offset = it - src_begin;
        src_begin[offset] += src_begin[offset-1];
    }
}

//-----------------------------------------------------------------------------
template <typename T>
void PrefixSum(T src_begin, T src_end, T dest)
{
    // dest[0] = src[0]
    // dest[1] = dest[0] + src[1];
    // dest[2] = dest[1] + src[2];
    // etc.

    typedef typename std::iterator_traits<T>::difference_type difference_type;

    *dest = *src_begin;
    for (T it = (src_begin+1); it != src_end; ++it)
    {
        difference_type offset = it - src_begin;
        dest[offset] = dest[offset-1] + src_begin[offset];
    }
}

