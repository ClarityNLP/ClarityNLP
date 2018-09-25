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

#include <iostream>
#include <limits>
#include <stdexcept>
#include <algorithm>
#include <getopt.h>
#include "utils.hpp"
#include "command_line.hpp"

using std::cout;
using std::cerr;
using std::endl;

//-----------------------------------------------------------------------------
void PrintOpts(const CommandLineOptions& opts)
{
    cout << "\n      Command line options: \n" << endl;
    cout << "\t            infile: " << opts.infile << endl;
    cout << "\t min_docs_per_term: " << opts.min_docs_per_term << endl;
    cout << "\t min_terms_per_doc: " << opts.min_terms_per_doc << endl;
    cout << "\t         precision: " << opts.precision << endl;
    cout << "\t      boolean_mode: " << opts.boolean_mode << endl;
    cout << "\t            tf-idf: " << opts.tf_idf << endl;
    cout << endl;
}

//-----------------------------------------------------------------------------
void PrintUsage(const std::string& program_name)
{
    cout << endl;
    cout << "Usage: " << program_name << endl;
    cout<< "          --infile  <path> " << endl; 
    cout << "        [--min_docs_per_term  3] " << endl;
    cout << "        [--min_terms_per_doc  5] " << endl;
    cout << "        [--precision  4] " << endl;
    cout << "        [--boolean_mode] " << endl;
    cout << "        [--tf-idf] " << endl;
    cout << endl;
}

//-----------------------------------------------------------------------------
void ParseCommandLine(int argc, char* argv[], CommandLineOptions& opts)
{
    // set defaults
    opts.infile = std::string("");
    opts.min_docs_per_term = 3;
    opts.min_terms_per_doc = 5;
    opts.max_iter          = 1000;
    opts.precision         = 4;
    opts.boolean_mode      = 0;
    opts.tf_idf            = 0;

    option longopts[] = {
        { "infile",            required_argument, NULL, 'i' },
        { "min_docs_per_term", required_argument, NULL, 'd' },
        { "min_terms_per_doc", required_argument, NULL, 't' },
        { "precision"        , required_argument, NULL, 'p' },
        { "tf_idf",            no_argument,       NULL, 'w' },
        { "boolean_mode",      no_argument,       NULL, 'b' },
        {0, 0, 0, 0}
    };

    int c;
    while ( (c = getopt_long(argc, argv, "i:d:t:p:wb", longopts, NULL)) != -1)
    {
        switch(c)
        {
        case 'i':
            opts.infile = std::string(optarg);
            break;
        case 'd':
            opts.min_docs_per_term = std::atoi(optarg);
            break;
        case 't':
            opts.min_terms_per_doc = std::atoi(optarg);
            break;
        case 'p':
            opts.precision = std::atoi(optarg);
            break;
        case 'w':
            opts.tf_idf = 1;
            break;
        case 'b':
            opts.boolean_mode = 1;
            break;
        case 0:
            // keep going, getopt_long did a variable assignment
            break;
        case ':':
            // missing option argument
            cerr << "required argument missing for option " << optopt << endl;
            break;
        case '?':
        default:
            // invalid option
            cerr << "invalid option: " << optopt << endl;
        }
    }
}

//-----------------------------------------------------------------------------
bool IsValid(const CommandLineOptions& opts)
{
    // user must specify the input file
    if (opts.infile.empty())
    {
        cerr << "preprocessor error: required command line argument --infile not found" << endl;
        return false;
    }

    // max iterations > 0
    if (opts.max_iter <= 0)
    {
        cerr << "preprocessor error: iteration count must be a positive integer" << endl;
        return false;
    }

    // min_docs_per_term > 0
    if (opts.min_docs_per_term <= 0)
    {
        cerr << "preprocessor error: min_docs_per_term must be a positive integer" << endl;
        return false;
    }

    // min_terms_per_doc > 0
    if (opts.min_terms_per_doc <= 0)
    {
        cerr << "preprocessor error: min_terms_per_doc must be a positive integer" << endl;
        return false;
    }

    return true;
}
