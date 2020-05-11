"""
Resolve overlap among finder candidates.
"""

from collections import namedtuple
from claritynlp_logging import log, ERROR, DEBUG

CANDIDATE_FIELDS = ['start', 'end', 'match_text', 'regex', 'other']
Candidate = namedtuple('_Candidate', CANDIDATE_FIELDS)

# initialize all fields to None
Candidate.__new__.__defaults__ = (None,) * len(Candidate._fields)


###############################################################################

_VERSION_MAJOR = 0
_VERSION_MINOR = 3
_MODULE_NAME   = 'finder_overlap.py'


###############################################################################
def has_overlap(a1, b1, a2, b2):
    """
    Determine if intervals [a1, b1) and [a2, b2) overlap at all.
    """

    assert a1 <= b1
    assert a2 <= b2
    
    if b2 <= a1:
        return False
    elif a2 >= b1:
        return False
    else:
        return True


###############################################################################
def remove_overlap(candidates, debug=False):
    """
    Given a set of match candidates, resolve into nonoverlapping matches.
    Take the longest match at any given position.

    ASSUMES that the candidate list has been sorted by matching text length,
    from longest to shortest.
    """

    if debug:
        log('called _remove_overlap...')
    
    results = []
    overlaps = []
    indices = [i for i in range(len(candidates))]

    i = 0
    while i < len(indices):

        if debug:
            log('\tstarting indices: {0}'.format(indices))

        index_i = indices[i]
        start_i = candidates[index_i].start
        end_i   = candidates[index_i].end
        len_i   = end_i - start_i

        overlaps.append(i)
        candidate_index = index_i

        j = i+1
        while j < len(indices):
            index_j = indices[j]
            start_j = candidates[index_j].start
            end_j   = candidates[index_j].end
            len_j   = end_j - start_j
            

            # does candidate[j] overlap candidate[i] at all
            if has_overlap(start_i, end_i, start_j, end_j):
                if debug:
                    log('\t\t({0}, {1}), ({2}, {3})'.format(start_i, end_i, start_j, end_j))
                    log('\t\t"{0}" OVERLAPS "{1}", lengths {2}, {3}'.
                          format(candidates[index_i].match_text,
                                 candidates[index_j].match_text,
                                 len_i, len_j))
                overlaps.append(j)
                # keep the longest match at any overlap region
                if len_j > len_i:
                    start_i = start_j
                    end_i   = end_j
                    len_i   = len_j
                    candidate_index = index_j
            j += 1

        if debug:
            log('\t\t\twinner: "{0}"'.
                  format(candidates[candidate_index].match_text))
            log('\t\t\tappending "{0}" to results'.
                  format(candidates[candidate_index].match_text))
            
        results.append(candidates[candidate_index])

        if debug:
            log('\t\toverlaps: "{0}"'.format(overlaps))
        
        # remove all overlaps
        new_indices = []
        for k in range(len(indices)):
            if k not in overlaps:
                new_indices.append(indices[k])
        indices = new_indices

        if debug:
            log('\t\tindices after removing overlaps: {0}'.format(indices))
        
        if 0 == len(indices):
            break

        # start over
        i = 0
        overlaps = []

    return results


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)
