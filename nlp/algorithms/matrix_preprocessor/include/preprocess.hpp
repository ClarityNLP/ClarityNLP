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

#include <vector>
#include "term_frequency_matrix.hpp"

bool preprocess_tf(TermFrequencyMatrix& A,
                   std::vector<unsigned int>& term_indices,
                   std::vector<unsigned int>& doc_indices,
                   const unsigned int MAX_ITER,
                   const unsigned int MIN_DOCS_PER_TERM,
                   const unsigned int MIN_TERMS_PER_DOC);

