#include <cmath>
#include <iostream>
#include <algorithm>
#include "score.hpp"
#include "term_occurrence_histogram.hpp"

using std::cout;
using std::cerr;
using std::endl;

//-----------------------------------------------------------------------------
void ComputeTfIdf(TermFrequencyMatrix& M, std::vector<double>& scores)
{
    unsigned int* cols = M.ColBuffer();
    TFData* tf_data = M.TFDataBuffer();
    
    const unsigned int height = M.Height();
    const unsigned int width  = M.Width();
    const unsigned int new_nz = M.Size();

    const unsigned int s = std::max(height, width);
    std::vector<unsigned int> histogram(s);
    std::vector<unsigned int> histogram_nz(s);
    
    // Compute scores
    scores.resize(new_nz);

    // sum across the rows of the matrix to compute the number of 
    // times each term occurs
    TermOccurrenceHistogram(tf_data, new_nz, &histogram[0], &histogram_nz[0], height);

    // compute idf score
    double dwidth = static_cast<double>(width);
    std::vector<double> idf(height);
    for (unsigned int r=0; r != height; ++r)
        idf[r] = log(dwidth / static_cast<double>(histogram_nz[r]));

    // initialize the scores
    for (unsigned int s=0; s != new_nz; ++s)
        scores[s] = 1.0 + log(static_cast<double>(tf_data[s].count));

    // multiply each nonzero r in M by idf[r] down the cols
    std::vector<double> D(width);
    for (unsigned int c=0; c != width; ++c)
    {
        unsigned int start = cols[c];
        unsigned int end   = cols[c+1];
        
        double sum_sq = 0.0;
        for (unsigned int offset=start; offset != end; ++offset)
        {
            assert(offset < new_nz);
            unsigned int r = tf_data[offset].row;
            scores[offset] *= idf[r];
            sum_sq += (scores[offset]*scores[offset]);
        }
        
        assert(sum_sq > 0.0);
        D[c] = 1.0 / sqrt(sum_sq);
    }
    
    for (unsigned int c=0; c != width; ++c)
    {
        unsigned int start = cols[c];
        unsigned int end   = cols[c+1];
        for (unsigned int offset=start; offset != end; ++offset)
        {
            assert(offset < new_nz);
            scores[offset] *= D[c];
        }
    }    
}

//-----------------------------------------------------------------------------
void ComputeTfIdf(TermFrequencyMatrix& M)
{
    std::vector<double> scores;
    ComputeTfIdf(M, scores);
}
