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
#include <algorithm>
#include <cstdint>
#include <vector>
#include <string>
#include <cassert>
#include "preprocess_common.hpp"
#include "sparse_matrix_decl.hpp"
#include "sparse_matrix_impl.hpp"
#include "term_frequency_matrix.hpp"
#include "spooky_v2.hpp"
#include "term_occurrence_histogram.hpp"

using std::cout;
using std::cerr;
using std::endl;

void PruneRows(TermFrequencyMatrix& M, 
               std::vector<unsigned int>& mask,
               std::vector<unsigned int>& histogram,
               std::vector<unsigned int>& histogram_nz,
               std::vector<unsigned int>& term_indices,
               std::vector<unsigned int>& renumbered_term_indices,
               const unsigned int min_docs_per_term);

bool PrunableCols(TermFrequencyMatrix& M, 
                  std::vector<unsigned int>& mask,
                  unsigned int& new_width,
                  unsigned int& new_nz,
                  const unsigned int min_terms_per_doc);

void PruneCols(TermFrequencyMatrix& M, 
               std::vector<unsigned int>& mask,
               std::vector<unsigned int>& doc_indices,
               const unsigned int new_width,
               const unsigned int new_nz);

void UniqueCols(TermFrequencyMatrix& M, 
                std::vector<unsigned int>& mask,
                std::vector<IndexedData>& hash,
                unsigned int& new_width,
                unsigned int& new_nz);

void ResolveFalsePositives(const unsigned int width,
                           const unsigned int* cols,
                           const TFData* tf_data,
                           std::vector<IndexedData>& hash,
                           std::vector<unsigned int>& unique_indices,
                           const unsigned int c1, const unsigned int c2);

void ResolveFalsePositives2(const unsigned int width,
                            const unsigned int* cols,
                            const TFData* tf_data,
                            std::vector<IndexedData>& hash,
                            std::vector<unsigned int>& unique_indices,
                            const unsigned int c1);

//-----------------------------------------------------------------------------
bool preprocess_tf(TermFrequencyMatrix& M,
                   std::vector<unsigned int>& term_indices,
                   std::vector<unsigned int>& doc_indices,
                   const unsigned int MAX_ITER,
                   const unsigned int MIN_DOCS_PER_TERM,
                   const unsigned int MIN_TERMS_PER_DOC)
{
    const unsigned int m = M.Height();
    const unsigned int n = M.Width();
    const unsigned int s = std::max(m, n);
    unsigned width, new_width, new_nz;

     // setup the term and doc index vectors
    if (term_indices.size() < m)
        term_indices.resize(m);
    if (doc_indices.size() < n)
        term_indices.resize(n);
    
    for (unsigned int r=0; r != m; ++r)
        term_indices[r] = r;
    for (unsigned int c=0; c != n; ++c)
        doc_indices[c] = c;

    // boolean mask
    std::vector<unsigned int> mask(s);

    // auxiliary arrays
    std::vector<IndexedData> hash(n);
    std::vector<unsigned int> histogram(s);
    std::vector<unsigned int> histogram_nz(s);
    std::vector<unsigned int> renumbered_term_indices(m);

    // Sort the matrix row indices prior to start, since UniqueCols() 
    // treats the row indices as byte strings for hashing.  The order
    // of the nonzero row indices in any column must be identical for
    // the hash function to return equal hash values (in the absence
    // of collisions, which are also checked for).
    M.SortRows();

    //
    // main loop
    // 
    cout << "\nStarting iterations..." << endl;
    unsigned int iter=0;
    while (iter < MAX_ITER)
    {
        // Prune any rows satisfying the row pruning criteria.  The mask
        // is not returned, since this function removes the pruned rows.
        PruneRows(M, mask, histogram, histogram_nz, term_indices, renumbered_term_indices, MIN_DOCS_PER_TERM);
        width = M.Width();

        // Evaluate the column pruning criteria and create a binary mask for
        // all cols.  The mask contains TT for columns that survive, FF for
        // cols that are prunable.  The new_width variable contains the number
        // of surviving columns (the sum of all mask values equal to TT).
        if (!PrunableCols(M, mask, new_width, new_nz, MIN_TERMS_PER_DOC))
        {
            // No prunable columns were found.  Determine whether all columns
            // are unique.  Unique cols will be identified by a TT value in
            // the returned mask.
            assert(width == new_width);
            UniqueCols(M, mask, hash, new_width, new_nz);

            // finished if all columns are unique
            if (width == new_width)
                break;
        }
        else
        {
            if (0 == new_width)
            {
                cerr << "Preprocessor: all columns were pruned." << endl;
                return false;
            }

            // Prune all cols c with mask[c] == FF.
            PruneCols(M, mask, doc_indices, new_width, new_nz);

            // Check to see if all cols are unique; the returned mask will
            // indicate unique cols with TT at the column index.
            width = M.Width();
            assert(width == new_width);
            UniqueCols(M, mask, hash, new_width, new_nz);
        }

        if (width != new_width)
            PruneCols(M, mask, doc_indices, new_width, new_nz);
           
        cout << "\t[" << (iter+1) << "] height: " << M.Height() << ", width: " 
             << M.Width() << ", nonzeros: " << M.Size() << endl;
        ++iter;
    }

    return true;
}

//-----------------------------------------------------------------------------
void PruneRows(TermFrequencyMatrix& M, 
               std::vector<unsigned int>& mask,
               std::vector<unsigned int>& histogram,
               std::vector<unsigned int>& histogram_nz,
               std::vector<unsigned int>& term_indices,
               std::vector<unsigned int>& renumbered_term_indices,
               const unsigned int min_docs_per_term)
{
    // For a term-frequency matrix, 'size' and 'nonzero_count' are two 
    // different things.  These are identical for a boolean matrix.

    const unsigned int width   = M.Width();
    unsigned int source_nz     = M.Size();
    unsigned int source_height = M.Height();
    unsigned int* source_cols  = M.ColBuffer();
    TFData* source_tf = M.TFDataBuffer();

    // Sum across the rows of the matrix to get term occurrence counts.
    // Note that this is different from the number of occupied elements.
    TermOccurrenceHistogram(source_tf, source_nz, &histogram[0], &histogram_nz[0], source_height);

    // create a binary mask for each row according to pruning conditions
    unsigned int new_height=0, new_nz=0;
    for (unsigned int r=0; r != source_height; ++r)
    {
        // histogram[r] == sum of occurrence counts for the rth term
        // histogram_nz[r] == number of documents in which the rth term occurs
        bool condition_1 = (histogram[r] >= min_docs_per_term);
        bool condition_2 = (histogram_nz[r] < width);
        mask[r] = (condition_1 && condition_2) ? TT : FF;

        // update the new height and nonzero count without branching
        new_height += (mask[r] & 0x01);
        new_nz += (mask[r] & histogram_nz[r]);
    }

    assert(new_height <= source_height);
    if (new_height == source_height)
        return;

    assert(new_nz <= source_nz);

    // The row indices need to be renumbered since some rows have been pruned.
    // Construct a mapping from old row indices to new row indices.
    unsigned int count=0;
    for (unsigned int r=0; r != source_height; ++r)
    {
        if (TT == mask[r])
        {
            // save the surviving term index value at the new index
            term_indices[count] = term_indices[r];
            renumbered_term_indices[r] = count++;
        }
    }

    assert(count == new_height);

    // build the pruned matrix in place, compacting the existing data
    unsigned int nz_count2 = 0;
    for (unsigned int c=0; c != width; ++c)
    {
        // column c in the unpruned matrix begins and ends at these offsets
        // in the source_rows array
        unsigned int start = source_cols[c];
        unsigned int end   = source_cols[c+1];

        // column c in the pruned matrix begins here
        source_cols[c] = nz_count2;

        for (unsigned int offset=start; offset != end; ++offset)
        {
            unsigned int r = source_tf[offset].row;
            if (TT == mask[r])
            {
                // copy this row in place with a renumbered row index
                assert(nz_count2 < new_nz);
                source_tf[nz_count2].row = renumbered_term_indices[r];
                source_tf[nz_count2].count = source_tf[offset].count;
                ++nz_count2;
            }
        }
    }

    source_cols[width] = nz_count2;
    assert(new_nz == nz_count2);

    M.SetHeight(new_height);
    M.SetSize(nz_count2);
}

//-----------------------------------------------------------------------------
bool PrunableCols(TermFrequencyMatrix& M, 
                  std::vector<unsigned int>& mask,
                  unsigned int& new_width,
                  unsigned int& new_nz,
                  const unsigned int min_terms_per_doc)
{
    unsigned int source_nz     = M.Size();
    unsigned int source_width  = M.Width();
    unsigned int* source_cols  = M.ColBuffer();

    // Count the number of terms for each doc; also construct a binary mask
    // for each doc according to the pruning condition.
    new_width = 0;
    new_nz = 0;
    for (unsigned int c=0; c != source_width; ++c)
    {
        unsigned int num_terms = source_cols[c+1] - source_cols[c];
        mask[c] = (num_terms >= min_terms_per_doc) ? TT : FF;

        // update width and nonzero count
        new_width += (mask[c] & 0x01);
        new_nz += (mask[c] & num_terms);
    }

    assert(new_width <= source_width);
    if (new_width == source_width)
        return false;

    assert(new_nz <= source_nz);
    return true;
}

//-----------------------------------------------------------------------------
void PruneCols(TermFrequencyMatrix& M, 
               std::vector<unsigned int>& mask,
               std::vector<unsigned int>& doc_indices,
               const unsigned int new_width,
               const unsigned int new_nz)
{
    unsigned int source_width  = M.Width();
    unsigned int* source_cols  = M.ColBuffer();
    TFData* source_tf = M.TFDataBuffer();

    // compact the source_cols and source_rows arrays
    unsigned int new_c = 0, nz_count = 0;
    for (unsigned int c=0; c != source_width; ++c)
    {
        if (TT == mask[c])  // keep this col
        {
            unsigned int start = source_cols[c];
            unsigned int end   = source_cols[c+1];

            // move offsets to row data for column c
            source_cols[new_c] = nz_count;
            
            // update the document indices
            doc_indices[new_c] = doc_indices[c];
            ++new_c;

            // move nonzero row indices for column c
            for (unsigned int offset=start; offset != end; ++offset)
            {
                source_tf[nz_count] = source_tf[offset];
                ++nz_count;
            }
        }
    }

    assert(new_width == new_c);
    assert(nz_count == new_nz);
    source_cols[new_width] = new_nz;
    M.SetWidth(new_width);
    M.SetSize(new_nz);
}

//-----------------------------------------------------------------------------
void HashColsSpooky(const unsigned int width,
                    const unsigned int* cols,
                    const unsigned int* rows,
                    std::vector<IndexedData>& hash)
{
    // This is SpookyHash from Bob Jenkins, 64-bit variant.

    SpookyHash spooky;
    const uint64_t SPOOKY_HASH_SEED = 42u;

    for (unsigned int c=0; c != width; ++c)
    {
        unsigned int start = cols[c];
        unsigned int end   = cols[c+1];

        uint64_t hashval = spooky.Hash64(&rows[start], 
                                         (end-start)*sizeof(unsigned int),
                                         SPOOKY_HASH_SEED);

        hash[c].value = hashval;
        hash[c].index = c;
    }
}

//-----------------------------------------------------------------------------
void HashColsSpooky(const unsigned int width,
                    const unsigned int* cols,
                    const TFData* tf_data,
                    std::vector<IndexedData>& hash)
{
    // This is SpookyHash from Bob Jenkins, 64-bit variant.

    SpookyHash spooky;
    const uint64_t SPOOKY_HASH_SEED = 42u;

    for (unsigned int c=0; c != width; ++c)
    {
        unsigned int start = cols[c];
        unsigned int end   = cols[c+1];

        uint64_t hashval = spooky.Hash64(&tf_data[start], 
                                         (end-start)*sizeof(TFData), //unsigned int),
                                         SPOOKY_HASH_SEED);

        hash[c].value = hashval;
        hash[c].index = c;
    }
}

//-----------------------------------------------------------------------------
void ResolveFalsePositives2(const unsigned int width,
                            const unsigned int* cols,
                            const TFData* tf_data,
                            std::vector<IndexedData>& hash,
                            std::vector<unsigned int>& unique_indices,
                            const unsigned int c1)
{
    // special case for two equal hashes - do a direct comparison
    unique_indices.clear();

    // get the original source columns
    unsigned int k1 = hash[c1].index;
    unsigned int k2 = hash[c1+1].index;

    // TFData indices for k1
    unsigned int start1 = cols[k1];
    unsigned int end1   = cols[k1+1];
    unsigned int num1 = end1 - start1;

    // TFData indices for k2
    unsigned int start2 = cols[k2];
    unsigned int end2   = cols[k2+1];
    unsigned int num2 = end2 - start2;

    // order cols from high to low - will choose the col at the largest
    // index as the survivor if both cols are identical
    if (k1 < k2)
        std::swap(k1, k2);
    
    if (num1 != num2)
    {
        // cols are unequal if different number of nonzeros
        unique_indices.push_back(k1);
        unique_indices.push_back(k2);
        return;
    }

    bool equal = true;
    unsigned int offset1 = start1;
    unsigned int offset2 = start2;
    while (offset1 < end1)
    {
        TFData d1 = tf_data[offset1++];
        TFData d2 = tf_data[offset2++];
        if (d1 != d2)
        {
            equal = false;
            break;
        }
    }

    unique_indices.push_back(k1);
    if (!equal)
        unique_indices.push_back(k2);
}

//-----------------------------------------------------------------------------
void ResolveFalsePositives(const unsigned int width,
                           const unsigned int* cols,
                           const TFData* tf_data,
                           std::vector<IndexedData>& hash,
                           std::vector<unsigned int>& unique_indices,
                           const unsigned int c1, const unsigned int c2)
{
    const unsigned int BUFSIZE = 2048;
    std::string key;
    std::vector<char> key_buf(BUFSIZE, '\0');
    std::multimap<std::string, unsigned int> MM;

    unique_indices.clear();
    for (unsigned int c=c1; c != c2; ++c)
    {
        // k is the original column
        unsigned int k = hash[c].index;
        
        unsigned int start = cols[k];
        unsigned int end   = cols[k+1];

        // count the number of nonzeros in this column and convert to bytes
        unsigned int source_bytes = (end - start)*sizeof(TFData);
        if (source_bytes + 1 >= BUFSIZE)
            key_buf.resize( 2*(source_bytes + 1));

        // copy the TFData into the buf as ASCII
        const unsigned char* source = reinterpret_cast<const unsigned char*>(&tf_data[start]);
        for (unsigned int i=0; i != source_bytes; ++i)
            key_buf[i] = source[i] + '0';
        key_buf[source_bytes] = '\0';

        key = std::string(&key_buf[0]);
        MM.insert(std::make_pair(key, k));
    }

    // save the max index at each *unique* key, to match Matlab's current behavior
    // (note - Matlab's legacy behavior is different; see Matlab's help
    // for the 'unique' function)
    for (auto it=MM.begin(), end=MM.end(); it != end; it=MM.upper_bound(it->first))
    {
        std::string key = it->first;

        unsigned int max_index = 0;
        for (auto pos=MM.lower_bound(key); pos != MM.upper_bound(key); ++pos)
        {
            unsigned int index = pos->second;
            if (index > max_index)
                max_index = index;
        }

        unique_indices.push_back(max_index);
    }
}

//-----------------------------------------------------------------------------
void UniqueCols(TermFrequencyMatrix& M, 
                std::vector<unsigned int>& mask,
                std::vector<IndexedData>& hash,
                unsigned int& new_width,
                unsigned int& new_nz)
{
    std::vector<unsigned int> unique_indices;
    const unsigned int width = M.Width();
    const unsigned int* cols = M.LockedColBuffer();
    const TFData* tf_data = M.TFDataBuffer();

    HashColsSpooky(width, cols, tf_data, hash);

    // find groups of identical hashes by sorting the hash values
    std::sort(hash.begin(), hash.begin() + width, 
              [](const IndexedData& d1, 
                 const IndexedData& d2) 
              {
                  return d1.value < d2.value;
              });

    // walk the array and find the equal hash groups
    // smallest index is the unique representative of any group
    uint32_t c1=0, c2;
    uint64_t hashval = hash[0].value;
    while ( c1 < (width-1))
    {
        c2 = c1 + 1;

        // if not equal, get the next hash value and continue
        if (hash[c2].value != hashval)
        {
            // hash[c1].index is a unique column
            mask[hash[c1].index] = TT;
            hashval = hash[c2].value;
        }
        else
        {
            // continue searching until an unequal hash is found
            while (c2 < width)
            {
                if (hash[c2].value == hashval)
                    ++c2;
                else
                {
                    // found it, at index c2
                    hashval = hash[c2].value;
                    break;
                }
            }

            // The group of equal hashes spans the range [c1, c2) in the
            // hash array.  These should all be true duplicate columns, but
            // there is a chance that the hash function could have produced
            // a collision between unequal columns.  So all cols with equal
            // hash values need to be checked further for uniqueness.
            
            unsigned int equal_count = c2-c1;
            if (2 == equal_count)
                ResolveFalsePositives2(width, cols, tf_data, hash, unique_indices, c1);
            else
                ResolveFalsePositives(width, cols, tf_data, hash, unique_indices, c1, c2);

            // mask off all cols in the range [c1, c2), then set the unique indices            
            for (uint32_t k=c1; k<c2; ++k)
            {
                uint32_t index = hash[k].index;
                mask[index] = FF;
            }

            for (auto it=unique_indices.begin(); it != unique_indices.end(); ++it)
                mask[*it] = TT;
        }

        c1 = c2;

        // if c2 is the only remaining element, it is unique
        if (c2 == (width-1))
            mask[hash[c2].index] = TT;
    }

    // update new_width and new_nz
    new_width = 0, new_nz = 0;
    for (unsigned int c=0; c != width; ++c)
    {
        if (TT == mask[c])
        {
            ++new_width;
            new_nz += (cols[c+1] - cols[c]);
        }
    }
}
