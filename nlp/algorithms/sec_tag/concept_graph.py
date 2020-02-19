#!/usr/bin/env python3
"""
Concept graph derived from the SecTag hierarchy.
"""

import os
from copy import deepcopy
from claritynlp_logging import log, ERROR, DEBUG


class DuplicateNodeException(Exception):
    pass

class NodeNotFoundException(Exception):
    pass

class Node():
    """
    A node in the ConceptGraph.
    The 'cid' is the concept ID from the SecTag_Terminology database.
    """

    # cid = concept_id, level = level in the hierarchy [0-7]
    def __init__(self, cid, level, concept_name, treecode_string):
        self.cid   = cid;
        self.level = level;
        self.concept_name = concept_name;
        self.treecode_string = treecode_string;
        
        # decode the treecode_string to a list of ints
        int_strings = self.treecode_string.split('.')
        self.treecode_list = [int(s) for s in int_strings]
        
        # sets of parent and child node indices in the ConceptGraph
        self.parent_indices = set()
        self.child_indices = set()
        
    def add_parent(self, parent_index):
        self.parent_indices.add(parent_index)
        
    def add_child(self, child_index):
        self.child_indices.add(child_index)

    def get_parents(self):
        return deepcopy(self.parent_indices);

    def get_children(self):
        return deepcopy(self.child_indices);

    def dump(self):
        log("cid: {0}, level: {1}, name: {2}".format(self.cid, self.level, self.concept_name))
        log("\tchild indices: ")
        log("\t\t", end="")
        if len(self.child_indices) > 0:
            for c in self.child_indices:
                log("{0}, ".format(c), end="")
        else:
            log("None", end="")
        log("")
        log("\tparent indices: ")
        log("\t\t", end="")
        if len(self.parent_indices) > 0:
            for p in self.parent_indices:
                log("{0}, ".format(p), end="")
        else:
            log("None", end="")
        log("")
        
class ConceptGraph():
    """
       Graph of primary concepts in a modified adjacency list representation.
       Each node contains separate parent and child links. All links are
       bidirectional.
    """
    
    def __init__(self):
        self.nodes = []
        self.cid_to_index_map = {}

        # node cid => set of all ancestor CIDs of this node
        self.all_ancestors_map = {}

        # node cid => set of all descendant CIDs of this node
        self.all_descendants_map = {}

    def size(self):
        return len(self.nodes)

    def dump_node(self, node_index):
        """log node info for the node at the given node index."""
        self.nodes[node_index].dump()
        
    def dump_cid(self, cid):
        """log node info for the node with the given cid."""
        if not cid in self.cid_to_index_map:
            raise NodeNotFoundException
        node_index = self.cid_to_index_map[cid]
        self.dump_node(node_index)
        
    def add_node(self, node):
        if node.cid in self.cid_to_index_map:
            raise DuplicateNodeException(node.cid)
        self.nodes.append(node)
        self.cid_to_index_map[node.cid] = len(self.nodes) - 1

    def node_index(self, cid):
        if not cid in self.cid_to_index_map:
            raise NodeNotFoundException(cid)
        return self.cid_to_index_map[cid]

    def link_nodes_by_index(self, child_node_index, parent_node_index):
        self.nodes[child_node_index].add_parent(parent_node_index)
        self.nodes[parent_node_index].add_child(child_node_index)
    
    def link_nodes(self, child_cid, parent_cid):
        if not child_cid in self.cid_to_index_map:
            raise NodeNotFoundException(child_cid)
        if not parent_cid in self.cid_to_index_map:
            raise NodeNotFoundException(parent_cid)
        child_node_index = self.cid_to_index_map[child_cid]
        parent_node_index = self.cid_to_index_map[parent_cid]
        self.link_nodes_by_index(child_node_index, parent_node_index)
        # debug
        # log("Linked these nodes: ")
        # self.nodes[child_node_index].dump()
        # self.nodes[parent_node_index].dump()

    def indices_to_cids(self, index_set):
        """Convert a set of node indices to a set of cids for those nodes."""
        cid_set = set()
        for index in index_set:
            cid = self.nodes[index].cid
            cid_set.add(cid)
        return cid_set

    def parent_indices(self, cid):
        """Return the set of parent node indices for this node."""
        if not cid in self.cid_to_index_map:
            raise NodeNotFoundException(cid)
        node_index = self.cid_to_index_map[cid]
        parent_indices = self.nodes[node_index].get_parents()
        return parent_indices

    def child_indices(self, cid):
        """Return the set of child node indices for this node."""
        if not cid in self.cid_to_index_map:
            raise NodeNotFoundException(cid)
        node_index = self.cid_to_index_map[cid]
        child_indices = self.nodes[node_index].get_children()
        return child_indices
    
    def parent_cids(self, cid):
        """Return the set of parent cids for this node."""
        parent_indices = self.parent_indices(cid)
        return self.indices_to_cids(parent_indices)

    def child_cids(self, cid):
        """Return the set of child cids for this node."""
        child_indices = self.child_indices(cid)
        return self.indices_to_cids(child_indices)

    def nearest_common_ancestor(self, cid1, cid2):
        """Return the most recent common ancestor of the two nodes."""
        if not cid1 in self.cid_to_index_map:
            raise NodeNotFoundException(cid1)
        if not cid2 in self.cid_to_index_map:
            raise NodeNotFoundException(cid2)

        # get the indices of each node
        node_index_1 = self.cid_to_index_map[cid1]
        node_index_2 = self.cid_to_index_map[cid2]

        treecode_list_1 = self.nodes[node_index_1].treecode_list
        treecode_list_2 = self.nodes[node_index_2].treecode_list

        n = min( len(treecode_list_1), len(treecode_list_2) )
        
        ancestor_treecode_list = []
        for i in range(0, n):
            if treecode_list_1[i] != treecode_list_2[i]:
                break
            else:
                ancestor_treecode_list.append(treecode_list_1[i])

        return ancestor_treecode_list

    def treecode_list(self, cid):
        """Return the treecode list of the given node."""
        if not cid in self.cid_to_index_map:
            raise NodeNotFoundException(cid)

        node_index = self.cid_to_index_map[cid]
        return deepcopy(self.nodes[node_index].treecode_list)

    def all_ancestors_of_node(self, node_index):
        """Return the set of all ancestor node indices for the given node."""

        ancestors = set()

        ancestor_pool = self.nodes[node_index].get_parents()
        while len(ancestor_pool) > 0:
            p = ancestor_pool.pop()
            ancestors.add(p)
            indices = self.nodes[p].get_parents()
            if len(indices) > 0:
                for j in indices:
                    ancestor_pool.add(j)
            
        return ancestors

    def all_descendants_of_node(self, node_index):
        """Return the set of all descendant node indices for the given node."""

        descendants = set()

        descendant_pool = self.nodes[node_index].get_children()
        while len(descendant_pool) > 0:
            d = descendant_pool.pop()
            descendants.add(d)
            indices = self.nodes[d].get_children()
            if len(indices) > 0:
                for j in indices:
                    descendant_pool.add(j)

        return descendants
    
    def all_ancestors_of_cid(self, cid):
        """Return the set of all ancestor node indices for the node with the given cid."""
        if not cid in self.cid_to_index_map:
            raise NodeNotFoundException(cid)
        node_index = self.cid_to_index_map[cid]
        return self.all_ancestors_of_node(node_index)

    def all_descendants_of_cid(self, cid):
        """Return the set of all descendant node indices for the node with the given cid."""
        if not cid in self.cid_to_index_map:
            raise NodeNotFoundException(cid)
        node_index = self.cid_to_index_map[cid]
        return self.all_descendants_of_node(node_index)
    
    def dump_to_file(self, filename):
        """Dump to file in this format:
           
              node_count,link_count
              node[0].cid, node[0].level, node[0].concept_name, node[0].treecode_string
              node[1].cid, node[1].level, node[1].concept_name, node[1].treecode_string
              ...
              noce[node_count-1].cid, node[node_count-1].level, node[node_count-1].concept_name, ...
              link_0_child_cid,link_0_parent_cid
              link_1_child_cid,link_1_parent_cid
              ...
              link_n_child_cid,link_n_parent_cid
        """

        outfile = open(filename, "wt")
        
        # build a set of 2-tuples for all links
        link_set = set()

        node_index = 0
        for n in self.nodes:
            parents = n.get_parents()
            for p in parents:
                link_set.add( (node_index, p) )
            children = n.get_children()
            for c in children:
                link_set.add( (c, node_index) )

            node_index += 1

        outfile.write("{0},{1}\n".format(len(self.nodes), len(link_set)))
        for i in range(0, len(self.nodes)):
            outfile.write("{0},{1},{2},{3}\n".format(self.nodes[i].cid,
                                                     self.nodes[i].level,
                                                     self.nodes[i].concept_name,
                                                     self.nodes[i].treecode_string))
        for l in link_set:
            outfile.write("{0},{1}\n".format(self.nodes[l[0]].cid,
                                             self.nodes[l[1]].cid))
        outfile.close()

    def load_from_file(self, filename, db_extra=None):
        """
        Load the data written by self.dump_to_file() and validate the result.
        The parameter 'db_extra' is explained in the docstring for self.validate.
        """

        if db_extra is None:
            db_extra = {}
        infile = open(filename, "rt")
        line = infile.readline().rstrip()
        node_count, link_count = line.split(',')
        node_count = int(node_count)
        link_count = int(link_count)

        # load the nodes
        for i in range(0, node_count):
            line = infile.readline().rstrip()
            (cid, level, name, treecode_string) = line.split(',')
            node = Node(int(cid), int(level), name, treecode_string)
            self.add_node(node)

        # load the links
        for i in range(0, link_count):
            line = infile.readline().rstrip()
            child_cid, parent_cid = line.split(',')
            self.link_nodes(int(child_cid), int(parent_cid))
        
        infile.close()
        self.validate(db_extra)

        self.compute_ancestor_sets()
        self.compute_descendant_sets()

    def compute_ancestor_sets(self):
        """
        For each node cid, compute all ancestor cids of that node.
        """
        self.all_ancestors_map = {}
        for n in range(0, len(self.nodes)):
            cid = self.nodes[n].cid
            ancestor_indices = self.all_ancestors_of_node(n)
            ancestor_cids = set([self.nodes[i].cid for i in ancestor_indices])
            self.all_ancestors_map[cid] = ancestor_cids

    def compute_descendant_sets(self):
        """
        For each node cid, compute all descendant cids of that node.
        """
        self.all_descendants_map = {}
        for n in range(0, len(self.nodes)):
            cid = self.nodes[n].cid
            descendant_indices = self.all_descendants_of_node(n)
            descendant_cids = set([self.nodes[i].cid for i in descendant_indices])
            self.all_descendants_map[cid] = descendant_cids
        
    def dump_ancestor_cids_to_file(self, filename):
        """For each node, write all of its ancestor nodes to the given file.
           Output is the cid of each node, followed by the cids of its
           ancestors, in CSV format.
         """

        outfile = open(filename, "wt")
        for n in range(0, len(self.nodes)):
            ancestors = self.all_ancestors_of_node(n)
            outfile.write("{0}".format(self.nodes[n].cid))
            if len(ancestors) > 0:
                outfile.write(",")

                ancestor_count = len(ancestors)

                i=0
                for a in ancestors:
                    outfile.write("{0}".format(self.nodes[a].cid))
                    i += 1
                    if i < ancestor_count:
                        outfile.write(",")
            outfile.write("\n")
        outfile.close()

    def load_ancestor_cids_from_file(self, filename):
        """
        Load the data written by dump_ancestor_cids_to_file().
        """
        ancestor_cid_map = {}
        infile = open(filename, "rt")
        for line in infile:
            data = line.rstrip().split(',')
            cid = int(data[0])
            ancestor_cid_map[cid] = [int(d) for d in data[1:]]

        infile.close()

        # verify results
        for cid in ancestor_cid_map.keys():
            ancestor_indices = self.all_ancestors_of_cid(cid)
            ancestor_cids = [self.nodes[a].cid for a in ancestor_indices]
            for a in ancestor_cids:
                if not a in ancestor_cid_map[cid]:
                    log("Ancestor {0} for cid {1} is missing.".format(a, cid))

        return ancestor_cid_map
                
        
    def dump_descendant_cids_to_file(self, filename):
        """For each node, write all of its descendant nodes to the given file.
           Output is the cid of the node, followed by the cids of its 
           descendants, in CSV format.
        """

        outfile = open(filename, "wt")
        for n in range(0, len(self.nodes)):
            descendants = self.all_descendants_of_node(n)
            outfile.write("{0}".format(self.nodes[n].cid))
            if len(descendants) > 0:
                outfile.write(",")

                descendant_count = len(descendants)

                i = 0
                for d in descendants:
                    outfile.write("{0}".format(self.nodes[d].cid))
                    i += 1
                    if i < descendant_count:
                        outfile.write(",")
            outfile.write("\n")
        outfile.close()

    def validate(self, db_extra=None):
        """
        Check that the graph was constructed properly. Find the number of
        descendants of each node at level 0 and compare with results of
        running SQL queries on the SecTag_Terminology database.

        The number of descendants of a top-level node is equal to the number
        of concepts_tbl entries that begin with n.*, where n is in [1, 27],
        (the top-level concept tree codes begin with 1).

        This query will return the desired result set, for n in the above range:

            SELECT * from concepts_tbl 
            WHERE concepttype = 'ATOMIC' and tree LIKE 'n.*' AND level <= 7;

        The 'db_extra' argument is used for validation if additional entries
        are added programmatically (i.e., not by altering the database
        creation SQL code). The key is the level-0 cid, the value is the
        number of additional entries for this level-0 cid.

        """
        if db_extra is None:
            db_extra = dict()

        # cid's of top-level atomic concepts; inital level value is index+1
        LEVEL_0_CIDS = [    1,    4,   18,   60,   63,  544,  961,
                          962,  966,  968,  969,  972,  973, 1066,
                         1072, 1079, 1080, 1081, 1083, 1084, 1086,
                         1089, 1090, 1091, 1092, 1093, 2747]

        # number of descendant concepts for the corresponding cid
        EXPECTED_RESULTS = [2, 13, 41,  2, 477, 415,  0,
                            3,  1,  0,  2,   0,  92,  5,
                            6,  0,  0,  1,   0,   1,  2,
                            0,  0,  0,  0,   0,   0]

        for i in range(0, 27):
            cid = LEVEL_0_CIDS[i]
            descendants = self.all_descendants_of_cid(cid)
            num = len(descendants)
            expected_num = EXPECTED_RESULTS[i]
            if cid in db_extra:
                expected_num += int(db_extra[cid])

            if num != expected_num:
                log("ConceptGraph::validate: cid {0}, tree {1}.* has {2} descendants, expected {3}."
                      .format(cid, i+1, num, expected_num))

        #log ("Graph validation checks passed.")

