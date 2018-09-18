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

#include <string>

struct CommandLineOptions
{
    std::string indir;
    std::string outdir;
    int terms_per_doc;
    int docs_per_term;
    int max_iter;
    int precision;    // no. of digits of precision for the output file
    int boolean_mode; // whether to force a boolean term-frequency matrix
};

void PrintUsage(const std::string& program_name);
void PrintOpts(const CommandLineOptions& opts);
void ParseCommandLine(int argc, char* argv[], CommandLineOptions& opts);
bool IsValid(const CommandLineOptions& opts);
