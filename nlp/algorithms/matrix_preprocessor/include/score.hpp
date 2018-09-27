#pragma once

#include <vector>
#include "term_frequency_matrix.hpp"

void ComputeTfIdf(TermFrequencyMatrix& M);
void ComputeTfIdf(TermFrequencyMatrix& M, std::vector<double>& scores);
