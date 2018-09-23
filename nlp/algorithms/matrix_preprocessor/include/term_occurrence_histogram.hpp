#pragma once

#include "term_frequency_matrix.hpp"

void TermOccurrenceHistogram(TFData* src,
                             const unsigned int source_count,
                             unsigned int* histogram,
                             unsigned int* histogram_nz,
                             const unsigned int bin_count);
