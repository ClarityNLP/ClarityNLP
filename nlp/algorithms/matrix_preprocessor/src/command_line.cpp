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
#include "utils.hpp"
#include "command_line.hpp"

using std::cout;
using std::cerr;
using std::endl;

//-----------------------------------------------------------------------------
void PrintOpts(const CommandLineOptions& opts)
{
    cout << "\n      Command line options: \n" << endl;
    cout << "\t             indir: " << opts.indir << endl;
    cout << "\t            outdir: " << opts.outdir << endl;
    cout << "\t     docs_per_term: " << opts.docs_per_term << endl;
    cout << "\t     terms_per_doc: " << opts.terms_per_doc << endl;
    cout << "\t          max_iter: " << opts.max_iter << endl;
    cout << "\t         precision: " << opts.precision << endl;
    cout << "\t      boolean_mode: " << opts.boolean_mode << endl;
    cout << endl;
}

//-----------------------------------------------------------------------------
void PrintUsage(const std::string& program_name)
{
    cout << endl;
    cout << "Usage: " << program_name << endl;
    cout<< "          --indir  <path> " << endl; 
    cout << "        [--outdir  (defaults to current directory)] " << endl;
    cout << "        [--docs_per_term  3] " << endl;
    cout << "        [--terms_per_doc  5] " << endl;
    cout << "        [--maxiter  1000] " << endl;
    cout << "        [--precision  4] " << endl;
    cout << "        [--boolean_mode  0] " << endl;
    cout << endl;
}

//-----------------------------------------------------------------------------
void ParseCommandLine(int argc, char* argv[], CommandLineOptions& opts)
{
    std::string tmp;

    // set defaults
    opts.indir         = std::string("");
    opts.outdir        = std::string("");
    opts.docs_per_term = 3;
    opts.terms_per_doc = 5;
    opts.max_iter      = 1000;
    opts.precision     = 4;
    opts.boolean_mode  = 0; 
    
    for (int k=1; k<argc; k += 2)
    {
        if ( ('-' == argv[k][0]) && ('-' == argv[k][1]))
        {
            char c = argv[k][2];
            if ('m' == c)
            {
                // --maxiter
                int max_iter = atoi(argv[k+1]);
                if (max_iter <= 0)
                    InvalidValue(std::string(argv[k]));
                opts.max_iter = max_iter;
            }
            else if ('p' == c)
            {
                // --precision
                int precision = atoi(argv[k+1]);
                if (precision <= 0)
                    InvalidValue(std::string(argv[k]));
                if (precision > std::numeric_limits<double>::max_digits10)
                    precision = std::numeric_limits<double>::max_digits10;
                opts.precision = precision;
            }
            else if ('i' == c)
            {
                // --indir
                opts.indir = std::string(argv[k+1]);
            }
            else if ('o' == c)
            {
                // --outdir
                opts.outdir = std::string(argv[k+1]);
            }
            else if ('d' == c)
            {
                // --docs_per_term
                int docs_per_term = atoi(argv[k+1]);
                if (docs_per_term <= 0)
                    InvalidValue(std::string(argv[k]));
                opts.docs_per_term = docs_per_term;
            }
            else if ('t' == c)
            {
                // --terms_per_doc
                int terms_per_doc = atoi(argv[k+1]);
                if (terms_per_doc <= 0)
                    InvalidValue(std::string(argv[k]));
                opts.terms_per_doc = terms_per_doc;
            }
            else if ('b' == c)
            {
                // --boolean_mode
                int boolean_mode = atoi(argv[k+1]);
                if (boolean_mode < 0)
                    InvalidValue(std::string(argv[k]));

                // interpret any nonzero value as true
                opts.boolean_mode = (0 == boolean_mode ? 0 : 1);
            }
        }
    }
}

//-----------------------------------------------------------------------------
bool IsValid(const CommandLineOptions& opts)
{
    // user must specify the intput directory
    if (opts.indir.empty())
    {
        cerr << "preprocessor error: required command line argument --indir not found" << endl;
        return false;
    }

    // max iterations > 0
    if (opts.max_iter <= 0)
    {
        cerr << "preprocessor error: iteration count must be a positive integer" << endl;
        return false;
    }

    // docs_per_term > 0
    if (opts.docs_per_term <= 0)
    {
        cerr << "preprocessor error: docs_per_term must be a positive integer" << endl;
        return false;
    }

    // terms_per_doc > 0
    if (opts.terms_per_doc <= 0)
    {
        cerr << "preprocessor error: terms_per_doc must be a positive integer" << endl;
        return false;
    }

    return true;
}
