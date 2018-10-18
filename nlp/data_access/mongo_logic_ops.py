#!/usr/bin/env python3
"""
Implementations of logical AND, OR, and NOT using Mongo aggregation.

This file is to be imported by the mongo evaluator.
"""

###############################################################################
def _append_logical_a_and_b(pipeline,
                            id_string,
                            feature_count,
                            nlpql_feature_list):
    """
    Append the aggregation stages required to implement a logical AND on the
    provided nlpql features. This is essentially an inner join on the common
    field encoded in the 'id_string'.
    """

    stages = [

        # find those records having the specified nlpql features
        {
            "$match" : {
                "nlpql_feature" : {"$in" : nlpql_feature_list}
            }
        },
        
        # group these records by value of the join variable
        {
            "$group" : {
                "_id" : id_string,               # field to group on
                "docs" : { "$push" : "$$ROOT" }, # put pairs in docs array
                "count" : { "$sum" : 1}          # count the number of docs for
                                                 # each value of the join var
            }
        },

        # {'_id':..., 'docs':[records w/same value of join var], 'count':...}

        # keep only the results with at least as many entries as nlpql_features
        { "$match" : { "count" : { "$gte" : feature_count }}},

        # serialize the entries, using one element from docs at a time;
        # creates new 'docs' field for each matching record
        { "$unwind" : "$docs" },

        # results after joining on subject: have _id, docs, and count fields

        # only emit the docs entries into the result set
        { "$replaceRoot" : { "newRoot" : "$docs" }}
    ]

    return pipeline.extend(stages)


###############################################################################
def _append_logical_a_not_b(pipeline,
                            id_string,
                            nlpql_feature_a,
                            nlpql_feature_b):
    """
    Join on the id_string and return all docs from A that are not in B.
    """

    stages = [

        # find those records having the specified nlpql features
        {
            "$match" : {
                "nlpql_feature" : {"$in" : [nlpql_feature_a, nlpql_feature_b]}
            }
        },

        # group these records by value of the join variable
        {
            "$group" : {
                "_id" : id_string,               # field to group on
                "docs" : { "$push" : "$$ROOT" }, # put pairs in docs array
                "count" : { "$sum" : 1}          # count the number of docs for
                                                 # each value of the join var
            }
        },

        # {'_id':..., 'docs':[records w/same value of join var], 'count':...}

        # keep only the results with at least as many entries as nlpql_features
        { "$match" : { "count" : { "$eq" : 1 }}},

        # keep only the docs having nlpql_feature_a
        { "$match" : { "docs.nlpql_feature" : { "$in" : [nlpql_feature_a]}}},

        # serialize the entries, using one element from docs at a time;
        # creates new 'docs' field for each matching record
        { "$unwind" : "$docs" },

        # results after joining on subject: have _id, docs, and count fields

        # only emit the docs entries into the result set
        { "$replaceRoot" : { "newRoot" : "$docs" }}
    ]

    return pipeline.extend(stages)


###############################################################################
def _append_logical_a_or_b(pipeline, nlpql_feature_list):
    """
    Compute the union of all records having the given nlpql features.
    """

    stages = [

        # find those records having the specified nlpql features
        {
            "$match" : {
                "nlpql_feature" : {"$in" : nlpql_feature_list}
            }
        }
    ]

    return pipeline.extend(stages)


###############################################################################
def _append_logical_not_a(pipeline, nlpql_feature):
    """
    Find all records that do NOT have the given nlpql feature.
    """

    stages = [

        {
            "$match" : {
                "nlpql_feature" : {"$nin" : [nlpql_feature]}
            }
        }
    ]

    pipeline.extend(stages)
    return pipeline


###############################################################################
def _logical_a_and_b(pipeline, field_to_join_on, nlpql_feature_list):

    id_string = "${0}".format(field_to_join_on)
    feature_count = len(nlpql_feature_list)
    
    _append_logical_a_and_b(pipeline,
                            id_string,
                            feature_count,
                            nlpql_feature_list)
    return pipeline


###############################################################################
def _logical_a_or_b(pipeline, nlpql_feature_list):

    _append_logical_a_or_b(pipeline, nlpql_feature_list)
    return pipeline


###############################################################################
def _logical_a_not_b(pipeline,
                     field_to_join_on,
                     nlpql_feature_a,
                     nlpql_feature_b):

    id_string = "${0}".format(field_to_join_on)
    _append_logical_a_not_b(pipeline,
                            id_string,
                            nlpql_feature_a,
                            nlpql_feature_b)
    return pipeline


###############################################################################
def logic_expr_a_b(pipeline, operator, field_to_join_on, nlpql_feature_list):
    """
    Build a MongoDB aggregation pipeline to evaluate a logic expression
    involving two sets of documents (i.e. two groups of rows in the
    intermediate results file).
    """

    if 'or' == operator:
        return _logical_a_or_b(pipeline,
                               nlpql_feature_list)
    elif 'and' == operator:
        return _logical_a_and_b(pipeline,
                                field_to_join_on,
                                nlpql_feature_list)
    elif 'not' == operator:
        return _logical_a_not_b(pipeline,
                                field_to_join_on,
                                nlpql_feature_list[0],
                                nlpql_feature_list[1])
    else:
        print('mongo_logic_expr: unknown operator: {0}'.format(operator))
        return []


###############################################################################
def logic_expr_not_a(pipeline, nlpql_feature):
    """
    Build a MongoDB aggregation pipeline to compute the expression 'not A',
    where A is a set of MongoDB documents. The 'not' operator is applied to
    the nlpql_feature field of each document.
    """

    return _append_logical_not_a(pipeline, nlpql_feature)
