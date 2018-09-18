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

#include "error.hpp"
#include <stdexcept>

//-----------------------------------------------------------------------------
void ThrowRuntimeException(std::ifstream& infile)
{
    std::ios_base::iostate state = infile.rdstate();

    if (state & infile.eof())
        throw std::runtime_error("CsvFileReader: unexpected end of file");
    else if (state & infile.fail())
        throw std::runtime_error("CsvFileReader: logical i/o error (failbit set)");
    else if (state & infile.bad())
        throw std::runtime_error("CsvFileReader: read error (badbit set)");
    else
        throw std::runtime_error("CsvFileReader: unknown file read error");
}
