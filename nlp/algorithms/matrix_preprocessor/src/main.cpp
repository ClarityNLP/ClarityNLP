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
#include <fstream>
#include <string>
#include <vector>
#include <limits>
#include "preprocess.hpp"
#include "command_line.hpp"
#include "sparse_matrix_decl.hpp"
#include "sparse_matrix_impl.hpp"
#include "sparse_matrix_io.hpp"
#include "term_frequency_matrix.hpp"
#include "timer.hpp"
#include "utils.hpp"
#include "score.hpp"

using std::cout;
using std::cerr;
using std::endl;

bool WriteIndicesToFile(const std::string& filepath,
                        const std::vector<unsigned int>& valid_indices,
                        const unsigned int N);

//-----------------------------------------------------------------------------
int main(int argc, char* argv[])
{
    Timer timer;
    double elapsed_s;

    // print usage info if no command line args were specified
    std::string prog_name(argv[0]);
    if (1 == argc)
    {
        PrintUsage(prog_name);
        return 0;
    }

    CommandLineOptions opts;
    ParseCommandLine(argc, argv, opts);
    if (!IsValid(opts))
        return -1;

    if (!FileExists(opts.infile))
    {
        cerr << "\npreprocessor: the specified input file "
             << opts.infile << " does not exist." << endl;
        return -1;
    }

    std::string infile = opts.infile;
    std::string outfile    = std::string("reduced_matrix.mtx");
    std::string outfile_tf = std::string("reduced_matrix_tf.mtx");
    std::string outdict    = std::string("reduced_dictionary_indices.txt");
    std::string outdocs    = std::string("reduced_document_indices.txt");

    // print command line options to the screen
    PrintOpts(opts);

    bool boolean_mode = (0 != opts.boolean_mode);
    
    SparseMatrix<double> A;
    unsigned int height, width, nonzeros;

    // load the input matrix and measure the load time
    cout << "Loading input matrix " << infile << endl;
    timer.Start();
    if (!LoadMatrixMarketFile(infile, A, height, width, nonzeros))
    {
        cerr << "\npreprocessor: could not load file " << infile << endl;
        return -1;
    }
    timer.Stop();
    elapsed_s = static_cast<double>(timer.ReportMilliseconds() * 0.001);
    cout << "\tInput file load time: " << elapsed_s << "s." << endl;

    // do the row and column pruning and measure the runtime
    timer.Start();

    TermFrequencyMatrix M(A.Height(),
                          A.Width(),
                          A.Size(),
                          A.LockedColBuffer(),
                          A.LockedRowBuffer(),
                          A.LockedDataBuffer(),
                          boolean_mode);

    // allocate the index sets for the terms and docs
    std::vector<unsigned int> term_indices(height);
    std::vector<unsigned int> doc_indices(width);
  
    bool ok = preprocess_tf(M, term_indices, doc_indices,
                            opts.max_iter, opts.min_docs_per_term, opts.min_terms_per_doc);

    timer.Stop();
    elapsed_s = static_cast<double>(timer.ReportMilliseconds() * 0.001);
    cout << "Processing time: " << elapsed_s << "s." << endl;
    cout << endl;

    if (!ok)
    {
        cerr << "\npreprocessor: matrix has dimension zero." << endl;
        cerr << "no output files will be written" << endl;
        return -1;
    }

    cout << "Iterations finished." << endl;
    cout << "\tNew height: " << M.Height() << endl;
    cout << "\tNew width: " << M.Width() << endl;
    cout << "\tNew nonzero count: " << M.Size() << endl;

    if (opts.tf_idf)
    {
        // compute TF-IDF weights
        std::vector<double> scores;
        ComputeTfIdf(M, scores);

        //
        // write the result matrix (with tf-idf scoring) to disk
        //

        cout << "Writing output matrix '" << outfile << "'" << endl;
        timer.Start();
        if (!M.WriteMtxFile(outfile, &scores[0], opts.precision))
        {
            cerr << "\npreprocessor: could not write file "
                 << outfile << endl;
            return -1;
        }
        timer.Stop();
        elapsed_s = static_cast<double>(timer.ReportMilliseconds() * 0.001);
        cout << "Output file write time: " << elapsed_s << "s." << endl;
    }
    else
    {
        //
        // write the pruned term-frequency matrix to disk
        //

        cout << "Writing pruned term-frequency matrix '" << outfile_tf << "'" << endl;
        timer.Start();
        if (!M.WriteMtxFile(outfile_tf))
        {
            cerr << "\npreprocessor: could not write file "
                 << outfile_tf << endl;
            return -1;
        }
        timer.Stop();
        elapsed_s = static_cast<double>(timer.ReportMilliseconds() * 0.001);
        cout << "Output term-frequency matrix write time: " << elapsed_s << "s." << endl;
    }

    //
    // write the reduced dictionary and document indices to disk
    //
    cout << "Writing dictionary index file '" << outdict << "'" << endl;
    timer.Start();
    if (!WriteIndicesToFile(outdict, term_indices, M.Height()))
    {
        cerr << "\npreprocessor: could not write file "
             << outdict << endl;
    }
    timer.Stop();
    elapsed_s = static_cast<double>(timer.ReportMilliseconds() * 0.001);
    
    cout << "Writing document index file '" << outdocs << "'" << endl;
    timer.Start();
    if (!WriteIndicesToFile(outdocs, doc_indices, M.Width()))
    {
        cerr << "\npreprocessor: could not write file "
             << outdocs << endl;
    }
    timer.Stop();
    elapsed_s += static_cast<double>(timer.ReportMilliseconds() * 0.001);
    cout << "Dictionary + documents write time: " << elapsed_s << "s." << endl;    

    return 0;
}

//-----------------------------------------------------------------------------
bool WriteIndicesToFile(const std::string& filepath,
                        const std::vector<unsigned int>& valid_indices,
                        const unsigned int N)
{
    if (valid_indices.size() < N)
    {
        cerr << "\npreprocessor: index set too small " << endl;
        cerr << "valid_indices size: " << valid_indices.size() 
             << ", N: " << N << endl;
        return false;
    }

    std::ofstream ostream(filepath);
    if (!ostream)
        return false;
    
    for (unsigned int s=0; s != N; ++s)
    {
        unsigned int index = valid_indices[s];
        ostream << index << endl;
    }

    ostream.close();
    return true;
}
