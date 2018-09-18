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

#include "matrix_market_file.hpp"

#include <fstream>
#include <sstream>
#include <algorithm>
#include <limits>
#include <stdexcept>
#include <cstdint>
#include "utils.hpp"

// This is a rewrite of the file mmio.c from NIST.
// http://math.nist.gov/MatrixMarket

//                Matrix Market internal definitions
//
// MM_matrix_typecode: 4-character sequence
//
//                   ojbect     sparse/     data        storage 
//  					  		dense     	type        scheme
//
// string position:  [0]        [1]			[2]         [3]
//
// Matrix typecode:  M(atrix)   C(oord)     R(eal)      G(eneral)
//  					        A(array)    C(omplex)   H(ermitian)
//  										P(attern)   S(ymmetric)
//  							    		I(nteger)   K(skew-symmetric)

extern const std::string MTX_EXTENSION("MTX");

static const char CHAR_A       = 'A';
static const char CHAR_C       = 'C';
static const char CHAR_G       = 'G';
static const char CHAR_H       = 'H';
static const char CHAR_I       = 'I';
static const char CHAR_K       = 'K';
static const char CHAR_M       = 'M';
static const char CHAR_P       = 'P';
static const char CHAR_R       = 'R';
static const char CHAR_S       = 'S';
static const char CHAR_SPACE   = ' ';
static const char CHAR_COMMENT = '%';

static const std::string MM_MTX_STR("matrix");
static const std::string MM_ARRAY_STR("array");
static const std::string MM_DENSE_STR("array");
static const std::string MM_COORDINATE_STR("coordinate");
static const std::string MM_SPARSE_STR("coordinate");
static const std::string MM_COMPLEX_STR("complex");
static const std::string MM_REAL_STR("real");
static const std::string MM_INT_STR("integer");
static const std::string MM_GENERAL_STR("general");
static const std::string MM_SYMM_STR("symmetric");
static const std::string MM_HERM_STR("hermitian");
static const std::string MM_SKEW_STR("skew-symmetric");
static const std::string MM_PATTERN_STR("pattern");

//-----------------------------------------------------------------------------
bool IsMatrixMarketFile(const std::string& filename)
{
    std::string ext = FileExtension(filename);
    return (MTX_EXTENSION == ext);
}

//-----------------------------------------------------------------------------
void mm_clear_typecode(char mm_typecode[4])
{
    mm_typecode[0] = CHAR_SPACE;
    mm_typecode[1] = CHAR_SPACE;
    mm_typecode[2] = CHAR_SPACE;
    mm_typecode[3] = CHAR_G;
}

void mm_set_matrix         (char typecode[4]) {typecode[0] = CHAR_M;}
void mm_set_coordinate     (char typecode[4]) {typecode[1] = CHAR_C;}
void mm_set_array          (char typecode[4]) {typecode[1] = CHAR_A;}
void mm_set_dense          (char typecode[4]) {mm_set_array(typecode);}
void mm_set_sparse         (char typecode[4]) {mm_set_coordinate(typecode);}
void mm_set_complex        (char typecode[4]) {typecode[2] = CHAR_C;}
void mm_set_real           (char typecode[4]) {typecode[2] = CHAR_R;}
void mm_set_pattern        (char typecode[4]) {typecode[2] = CHAR_P;}
void mm_set_integer        (char typecode[4]) {typecode[2] = CHAR_I;}
void mm_set_symmetric      (char typecode[4]) {typecode[3] = CHAR_S;}
void mm_set_general        (char typecode[4]) {typecode[3] = CHAR_G;}
void mm_set_skew           (char typecode[4]) {typecode[3] = CHAR_K;}
void mm_set_hermitian      (char typecode[4]) {typecode[3] = CHAR_H;}
void mm_initialize_typecode(char typecode[4]) {mm_clear_typecode(typecode);}

//-----------------------------------------------------------------------------
bool mm_is_matrix    (const char typecode[4]) {return CHAR_M == typecode[0];}
bool mm_is_sparse    (const char typecode[4]) {return CHAR_C == typecode[1];}
bool mm_is_coordinate(const char typecode[4]) {return CHAR_C == typecode[1];}
bool mm_is_dense     (const char typecode[4]) {return CHAR_A == typecode[1];}
bool mm_is_array     (const char typecode[4]) {return CHAR_A == typecode[1];}
bool mm_is_complex   (const char typecode[4]) {return CHAR_C == typecode[2];}
bool mm_is_real      (const char typecode[4]) {return CHAR_R == typecode[2];}
bool mm_is_pattern   (const char typecode[4]) {return CHAR_P == typecode[2];}
bool mm_is_integer   (const char typecode[4]) {return CHAR_I == typecode[2];}
bool mm_is_symmetric (const char typecode[4]) {return CHAR_S == typecode[3];}
bool mm_is_general   (const char typecode[4]) {return CHAR_G == typecode[3];}
bool mm_is_skew      (const char typecode[4]) {return CHAR_K == typecode[3];}
bool mm_is_hermitian (const char typecode[4]) {return CHAR_H == typecode[3];}

//-----------------------------------------------------------------------------
bool mm_is_valid(const char typecode[4])
{
    if (!mm_is_matrix(typecode))
        return false;

    if (mm_is_dense(typecode) && mm_is_pattern(typecode))
        return false;

    if (mm_is_real(typecode) && mm_is_hermitian(typecode))
        return false;

    if (mm_is_pattern(typecode) && (mm_is_hermitian(typecode) || mm_is_skew(typecode)))
        return false;

    return true;
}

//-----------------------------------------------------------------------------
int mm_read_banner(std::istream& infile, char matcode[4])
{
    std::string line, banner, mtx, crd, data_type, storage_scheme;

    mm_clear_typecode(matcode);

    if (!std::getline(infile, line))
        return MM_PREMATURE_EOF;

    std::istringstream data(line);

    // check for the matrix market file identifier
    data >> banner;
    if (MM_BANNER != banner)
        return MM_NO_HEADER;

    data >> mtx;
    if (mtx.empty())
        return MM_PREMATURE_EOF;
    ToLower(mtx);

    data >> crd;
    if (crd.empty())
        return MM_PREMATURE_EOF;
    ToLower(crd);
    
    data >> data_type;
    if (data_type.empty())
        return MM_PREMATURE_EOF;
    ToLower(data_type);

    data >> storage_scheme;
    if (storage_scheme.empty())
        return MM_PREMATURE_EOF;
    ToLower(storage_scheme);

    // first field should be "mtx"
    if (MM_MTX_STR != mtx)
        return MM_UNSUPPORTED_TYPE;
    mm_set_matrix(matcode);

    // second field determines sparse or dense
    if (MM_SPARSE_STR == crd)
        mm_set_sparse(matcode);
    else if (MM_DENSE_STR == crd)
        mm_set_dense(matcode);
    else
        return MM_UNSUPPORTED_TYPE;

    // third field
    if (MM_REAL_STR == data_type)
        mm_set_real(matcode);
    else if (MM_COMPLEX_STR == data_type)
        mm_set_complex(matcode);
    else if (MM_PATTERN_STR == data_type)
        mm_set_pattern(matcode);
    else if (MM_INT_STR == data_type)
        mm_set_integer(matcode);
    else
        return MM_UNSUPPORTED_TYPE;
    
    // fourth field
    if (MM_GENERAL_STR == storage_scheme)
        mm_set_general(matcode);
    else if (MM_SYMM_STR == storage_scheme)
        mm_set_symmetric(matcode);
    else if (MM_HERM_STR == storage_scheme)
        mm_set_hermitian(matcode);
    else if (MM_SKEW_STR == storage_scheme)
        mm_set_skew(matcode);
    else
        return MM_UNSUPPORTED_TYPE;

    return 0;
}

//-----------------------------------------------------------------------------
int mm_read_mtx_crd_size(std::istream& infile, 
                         unsigned int& height, 
                         unsigned int& width, 
                         unsigned int& nz)
{
    std::string line;
    height = width = nz = 0;

    // skip the comment lines
    while (true)
    {
        if (!std::getline(infile, line))
            return MM_PREMATURE_EOF;

        if (CHAR_COMMENT != line[0])
            break;
    }

    // the matrix dimentions and nz count must fit within 32 bits
    uint64_t height_val, width_val, nz_val;
    uint64_t max_uint = 
        static_cast<uint64_t>(std::numeric_limits<unsigned int>::max());
    
    height = width = nz = 0;

    // find the first line that contains three integers
    while (true)
    {
        if (!line.empty())
        {
            std::istringstream data(line);

            data >> height_val;
            data >> width_val;
            data >> nz_val;

            if ( (height_val > max_uint) ||
                 (width_val  > max_uint) ||
                 (nz_val     > max_uint))
            {
                throw std::logic_error("sparse matrix too large");
            }

            height = static_cast<unsigned int>(height_val);
            width  = static_cast<unsigned int>(width_val);
            nz     = static_cast<unsigned int>(nz_val);
            return 0;
        }
        else
        {
            if (!std::getline(infile, line))
                return MM_PREMATURE_EOF;
        }
    }

    return MM_UNSUPPORTED_TYPE;
}
