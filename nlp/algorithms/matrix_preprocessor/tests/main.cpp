// test driver for the sparse matrix preprocessor

#include <iostream>
#include <string>
#include "tests.hpp"
#include "utils.hpp"
#include "sparse_matrix.hpp"

using std::cout;
using std::cerr;
using std::endl;

bool TestSparseMatrixGet();

//-----------------------------------------------------------------------------
int main(int argc, char* argv[])
{
    bool all_ok = true;

    if (1 == argc)
    {
        cerr << "Usage: " << argv[0] << "  <path_to_data_dir>" << endl;
        return -1;
    }

    std::string data_dir = EnsureTrailingPathSep(std::string(argv[1]));

    if (!TestSparseMatrixGet())
    {
        all_ok = false;
        cerr << "TestSparseMatrixGet failed" << endl;
    }

    if (!TestPreprocessor(data_dir))
    {
        all_ok = false;
        cerr << "TestPreprocessor failed" << endl;
    }
    
    if (all_ok)
        cout << "all tests passed" << endl;

    return 0;
}

//-----------------------------------------------------------------------------
bool TestSparseMatrixGet()
{
    SparseMatrix<double> M(3, 4, 5);

    M.BeginLoad();
    M.Load(1, 0, 1.0);
    M.Load(1, 1, 2.0);
    M.Load(2, 0, 3.0);
    M.Load(2, 1, 4.0);
    M.Load(2, 3, 5.0);
    M.EndLoad();

    double m00 = M.Get(0, 0);
    double m01 = M.Get(0, 1);
    double m02 = M.Get(0, 2);
    double m03 = M.Get(0, 3);
    double m10 = M.Get(1, 0);
    double m11 = M.Get(1, 1);
    double m12 = M.Get(1, 2);
    double m13 = M.Get(1, 3);
    double m20 = M.Get(2, 0);
    double m21 = M.Get(2, 1);
    double m22 = M.Get(2, 2);
    double m23 = M.Get(2, 3);

    if ( (0.0 != m00) || (0.0 != m01) || (0.0 != m02) || (0.0 != m03) ||
         (1.0 != m10) || (2.0 != m11) || (0.0 != m12) || (0.0 != m13) ||
         (3.0 != m20) || (4.0 != m21) || (0.0 != m22) || (5.0 != m23))
    {
        return false;
    }

    // // 1,3,2,4,5
    // unsigned int size = M.Size();
    // cout << "data: " << endl;
    // const double* data = M.LockedDataBuffer();
    // for (int i=0; i<size-1; ++i)
    //     cout << data[i] << ",";
    // cout << data[size-1] << endl;

    // // 1,2,1,2,2
    // cout << "indices: " << endl;
    // const unsigned int* indices = M.LockedRowBuffer();
    // for (int i=0; i<size-1; ++i)
    //     cout << indices[i] << ",";
    // cout << indices[size-1] << endl;

    // // 0,2,4,4,5
    // cout << "col offsets: " << endl;
    // const unsigned int* col_offsets = M.LockedColBuffer();
    // for (int i=0; i<size-1; ++i)
    //     cout << col_offsets[i] << ",";
    // cout << col_offsets[size-1] << endl;

    return true;
}
