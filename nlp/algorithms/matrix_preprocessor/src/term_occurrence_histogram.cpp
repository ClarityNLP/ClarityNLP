#include <cassert>
#include <algorithm>
#include "term_occurrence_histogram.hpp"

//-----------------------------------------------------------------------------
void TermOccurrenceHistogram(TFData* src,
                             const unsigned int source_count,
                             unsigned int* histogram,
                             unsigned int* histogram_nz,
                             const unsigned int bin_count)
{
    // zero the histogram arraya
    std::fill(histogram, histogram + bin_count, 0);
    std::fill(histogram_nz, histogram_nz + bin_count, 0);

    // bin the values
    for (unsigned int i=0; i != source_count; ++i)
    {
        unsigned int r = src[i].row;
        assert(r >= 0);
        assert(r < bin_count);

        // this histogram sums the values at each element
        histogram[r] += src[i].count;

        // this histogram counts the number of occupied elements
        histogram_nz[r] += 1;
    }
}
