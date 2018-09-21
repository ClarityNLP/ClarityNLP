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

using std::cout;
using std::cerr;
using std::endl;

bool WriteStringsToFile(const std::string& filepath,
                        std::vector<std::string>& strings,
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

    //
    // Check to see if the specified directories exist.
    //

    if (!DirectoryExists(opts.indir))
    {
        cerr << "\npreprocessor: the specified input directory "
             << opts.indir << " does not exist." << endl;
        return -1;
    }

    if (!opts.outdir.empty())
    {
        if (!DirectoryExists(opts.outdir))
        {
            cerr << "\npreprocessor: the specified output directory "
                 << opts.outdir << " does not exist." << endl;
            return -1;
        }
    }

    // setup paths and filenames
    std::string inputdir  = EnsureTrailingPathSep(opts.indir);
    std::string infile = inputdir + std::string("matrix.mtx");
    std::string indict = inputdir + std::string("dictionary.txt");
    std::string indocs = inputdir + std::string("documents.txt");

    std::string outputdir, outfile, outfile_tf, outdict, outdocs;
    if (!opts.outdir.empty())
    {
        outputdir = EnsureTrailingPathSep(opts.outdir);
        outfile    = outputdir + std::string("reduced_matrix.mtx");
        outfile_tf = outputdir + std::string("reduced_matrix_tf.mtx");
        outdict    = outputdir + std::string("reduced_dictionary.txt");
        outdocs    = outputdir + std::string("reduced_documents.txt");
    }
    else
    {
        outfile    = std::string("reduced_matrix.mtx");
        outfile_tf = std::string("reduced_matrix_tf.mtx");
        outdict    = std::string("reduced_dictionary.txt");
        outdocs    = std::string("reduced_documents.txt");
    }

    //
    // load the input dictionary and documents
    //
    std::vector<std::string> dictionary, documents;

    if (!LoadStringsFromFile(indict, dictionary))
    {
        cerr << "\npreprocessor: could not open dictionary file " 
             << indict << endl;
        return -1;
    }
    
    unsigned int num_terms = dictionary.size();

    if (!LoadStringsFromFile(indocs, documents))
    {
        cerr << "\npreprocessor: could not open documents file "
             << indocs << endl;
        return -1;
    }

    unsigned int num_docs = documents.size();

    // print options to screen prior to run
    opts.indir = inputdir;
    if (outputdir.empty())
        opts.outdir = std::string("current directory");
    else
        opts.outdir = outputdir;
    PrintOpts(opts);

    bool boolean_mode = (0 != opts.boolean_mode);
    
    SparseMatrix<double> A;
    unsigned int height, width, nonzeros;

    //
    // load the input matrix
    //

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

    //
    // check num_terms and num_docs
    //

    if (num_terms < A.Height())
    {
        cerr << "\npreprocessor error: expected " << A.Height() 
             << " terms in the dictionary; found " << num_terms << "." << endl;
        return -1;
    }

    if (num_docs < A.Width())
    {
        cerr << "\npreprocessor error: expected " << A.Width()
             << " strings in the documents file; found " << num_docs
             << "." << endl;
        return -1;
    }

    //
    // do the preprocessing
    //

    timer.Start();

    //TermFrequencyMatrix  M(A, boolean_mode);
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
    std::vector<double> scores;
  
    bool ok = preprocess_tf(M, term_indices, doc_indices, scores,
                            opts.max_iter, opts.docs_per_term, opts.terms_per_doc);
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

    //
    // write the pruned term-frequency matrix to disk
    //
    // cout << "Writing pruned term-frequency matrix '" << outfile_tf << "'" << endl;
    // timer.Start();
    // if (!M.WriteMtxFile(outfile_tf))
    // {
    //     cerr << "\npreprocessor: could not write file "
    //          << outfile_tf << endl;
    //     return -1;
    // }
    // timer.Stop();
    // elapsed_s = static_cast<double>(timer.ReportMilliseconds() * 0.001);
    // cout << "Output term-frequency matrix write time: " << elapsed_s << "s." << endl;

    //
    // write the reduced dictionary and documents to disk
    //
    cout << "Writing dictionary file '" << outdict << "'" << endl;
    timer.Start();
    if (!WriteStringsToFile(outdict, dictionary, term_indices, M.Height()))
    {
        cerr << "\npreprocessor: could not write file "
             << outdict << endl;
    }
    timer.Stop();
    elapsed_s = static_cast<double>(timer.ReportMilliseconds() * 0.001);
    
    cout << "Writing documents file '" << outdocs << "'" << endl;
    timer.Start();
    if (!WriteStringsToFile(outdocs, documents, doc_indices, M.Width()))
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
bool WriteStringsToFile(const std::string& filepath,
                        std::vector<std::string>& strings,
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
        ostream << strings[index] << endl;
    }

    ostream.close();
    return true;
}
