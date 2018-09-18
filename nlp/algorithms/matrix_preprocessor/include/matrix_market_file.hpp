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

// This is a rewrite of the file mmio.h from NIST.
// http://math.nist.gov/MatrixMarket

#include <string>

const int MM_COULD_NOT_READ_FILE = 11;
const int MM_PREMATURE_EOF       = 12;
const int MM_NOT_MTX             = 13;
const int MM_NO_HEADER           = 14;
const int MM_UNSUPPORTED_TYPE    = 15;
const int MM_LINE_TOO_LONG       = 16;
const int MM_INVALID_VALUE       = 17;

const std::string MM_BANNER("%%MatrixMarket");
const int MM_MAX_LINE_LENGTH = 1025;
const int MM_MAX_TOKEN_LENGTH = 64;

// extension for MatrixMarket files
extern const std::string MTX_EXTENSION;

// returns true if the given file is in MatrixMarket format
bool IsMatrixMarketFile(const std::string& filename);

int mm_read_banner      (std::istream& infile, char mm_typecode[4]);
int mm_read_mtx_crd_size(std::istream& infile, 
                         unsigned int& height, 
                         unsigned int& width, 
                         unsigned int& nz);

bool mm_is_matrix    (const char mm_typecode[4]);
bool mm_is_sparse    (const char mm_typecode[4]);
bool mm_is_coordinate(const char mm_typecode[4]);
bool mm_is_dense     (const char mm_typecode[4]);
bool mm_is_array     (const char mm_typecode[4]);
bool mm_is_complex   (const char mm_typecode[4]);
bool mm_is_real      (const char mm_typecode[4]);
bool mm_is_pattern   (const char mm_typecode[4]);
bool mm_is_integer   (const char mm_typecode[4]);
bool mm_is_symmetric (const char mm_typecode[4]);
bool mm_is_general   (const char mm_typecode[4]);
bool mm_is_skew      (const char mm_typecode[4]);
bool mm_is_hermitian (const char mm_typecode[4]);
bool mm_is_valid     (const char mm_typecode[4]);

