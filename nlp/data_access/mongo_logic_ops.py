#!/usr/bin/env python3
"""
Implementation via Mongo aggregation of n-ary logical AND, n-ary logical OR,
set difference (either 'A - B' or 'A not B', and set complement (NOT A).

This file is to be imported by the mongo evaluator.
"""

# Set this to True to join on (report_id|subject) && sentence && start.
# Otherwise join on report_id or subject only.
# Use the first for logical consistency for measurements or any chunks of
# text defined by a sentence and a start offset.
MEASUREMENT_CONTEXT=False

###############################################################################
def _append_logical_and(pipeline,             # pipeline to append to
                        field_to_join_on,
                        nlpql_feature_list):
    """
    Append the aggregation stages required to implement a logical AND on the
    provided nlpql features. This is an n-ary inner join on the common field
    encoded in the 'id_string'.

    The actual mathematical operation performed is
    'A AND B NOT (all other NLPQL features)'. This is for convenience, since
    users will not want to see or explicitly omit irrelevant NLPQL features
    in the result set.
    """

   #id_string = "${0}".format(field_to_join_on)
    
    str_filter_1 = field_to_join_on
    str_filter_2 = "${0}".format(field_to_join_on)
    
    n = len(nlpql_feature_list)
    feature_string = "feature_set.{0}".format(n-1)

    # set the join condition
    if MEASUREMENT_CONTEXT:
        # join on either (report_id or subject) AND sentence AND start offset
        join_obj = {
            str_filter_1 : str_filter_2,
            "sentence" : "$sentence",
            "start" : "$start"
        }
    else:
        # join only on either report_id or subject
        join_obj = {
            str_filter_1 : str_filter_2
        }
    
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
                "_id" : join_obj,
                "ntuple" : {"$push" : "$$ROOT"}, # grouped documents
                "count"  : {"$sum" : 1},         # count joined docs for each value of join var
                "feature_set" : {"$addToSet" : "$nlpql_feature"}
            }
        },

        # {'_id':..., 'ntuple':[records w/same value of join var], 'count':...}

        # keep only the results with at least as many entries as nlpql_features
        # (need n NLPQL features for an n-ary join)
        { "$match" : { "count" : { "$gte" : n }}},

        # keep only those records with n different nlpql_features
        # (check for the existence of an element at index n-1)
        { "$match" : { feature_string : { "$exists" : True }}},

        # project out the ntuple array
        {
            "$project" : {
                "_id"    : 0, # suppress _id field, not needed
                "ntuple" : 1  # keep ntuple array
            }
        },
        
        # the ntuple array contains each group of joined docs
    ]

    return pipeline.extend(stages)


###############################################################################
def _append_logical_or(pipeline,            # pipeline to append to
                       field_to_join_on,
                       nlpql_feature_list):
    """
    Compute the union of all records having the specified nlpql_features.
    """

    str_filter_1 = field_to_join_on
    str_filter_2 = "${0}".format(field_to_join_on)

    if MEASUREMENT_CONTEXT:
        join_obj = {
            str_filter_1 : str_filter_2,
            "sentence" : "$sentence",
            "start" : "$start"
        }
    else:
        join_obj = {
            str_filter_1 : str_filter_2
        }
    
    stages = [

        # find those records having the specified nlpql features
        {
            "$match" : {
                "nlpql_feature" : {"$in" : nlpql_feature_list}
            }
        },

        # group these records by the join variables
        {
            "$group" : {
                "_id" : join_obj,
                "ntuple" : {"$addToSet" : "$$ROOT"}  # grouped documents
            }
        },

        # project out the ntuple array
        {
            "$project" : {
                "_id"    : 0,  # suppress _id field, not needed
                "ntuple" : 1   # keep ntuple array
            }
        }
    ]

    return pipeline.extend(stages)



###############################################################################
def _append_logical_a_not_b(pipeline,         # pipeline to append to
                            field_to_join_on, # formatted "$join_field"
                            nlpql_feature_a,
                            nlpql_feature_b):
    """
    Find all elements common to A and B, then remove them from A. Whether an
    element belongs to both sets is determined by the join condition.
    """

    str_filter_1 = field_to_join_on
    str_filter_2 = "${0}".format(field_to_join_on)
    
    # set the join condition
    if MEASUREMENT_CONTEXT:
        # join on either (report_id or subject) AND sentence AND start offset
        join_obj = {
            str_filter_1 : str_filter_2,
            "sentence" : "$sentence",
            "start" : "$start"
        }
    else:
        # join only on either report_id or subject
        join_obj = {
            str_filter_1 : str_filter_2
        }
    
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
                "_id"    : join_obj,
                "ntuple" : {"$push" : "$$ROOT"}, # grouped documents
                "count"  : { "$sum" : 1}         # count joined docs for
                                                 # each value of join var
            }
        },

        # {'_id':..., 'ntuple':[records w/same value of join var], 'count':...}

        # of these, keep only the docs having nlpql_feature_a
        { "$match" : { "ntuple.nlpql_feature" : { "$nin" : [nlpql_feature_b]}}},

        # project out the ntuple array
        {
            "$project" : {
                "_id"    : 0,        # suppress _id field, not needed
                "ntuple" : "$ntuple" # keep ntuple array
            }
        }
    ]

    return pipeline.extend(stages)


###############################################################################
def _append_logical_not_a(pipeline,
                          field_to_join_on,
                          nlpql_feature):
    """
    Find all records that do NOT have the given nlpql feature. Group them by
    the join condition to conform to the other operations in this module.
    """

    str_filter_1 = field_to_join_on
    str_filter_2 = "${0}".format(field_to_join_on)
    
    # set the join condition
    if MEASUREMENT_CONTEXT:
        # join on either (report_id or subject) AND sentence AND start offset
        join_obj = {
            str_filter_1 : str_filter_2,
            "sentence" : "$sentence",
            "start" : "$start"
        }
    else:
        # join only on either report_id or subject
        join_obj = {
            str_filter_1 : str_filter_2
        }
    
    stages = [

        {
            "$match" : {
                "nlpql_feature" : {"$nin" : [nlpql_feature]}
            }
        },

        # group by value of the nlpql_feature
        {
            "$group" : {
                "_id"    : join_obj,            # field to group on
                "ntuple" : {"$push" : "$$ROOT"} # grouped documents
            }
        },

        # project out the ntuple array
        {
            "$project" : {
                "_id"    : 0, # suppress _id field, not needed
                "ntuple" : 1  # keep ntuple array
            }
        }
    ]

    pipeline.extend(stages)
    return pipeline


###############################################################################
def _logical_a_and_b(pipeline, field_to_join_on, nlpql_feature_list):

    _append_logical_and(pipeline,
                        field_to_join_on,
                        nlpql_feature_list)
    return pipeline


###############################################################################
def _logical_a_or_b(pipeline, field_to_join_on, nlpql_feature_list):

    _append_logical_or(pipeline,
                       field_to_join_on,
                       nlpql_feature_list)
    return pipeline


###############################################################################
def _logical_a_not_b(pipeline,
                     field_to_join_on,
                     nlpql_feature_a,
                     nlpql_feature_b):

    _append_logical_a_not_b(pipeline,
                            field_to_join_on,
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
        pipeline = _logical_a_or_b(pipeline,
                                   field_to_join_on,
                                   nlpql_feature_list)

    elif 'and' == operator:
        pipeline = _logical_a_and_b(pipeline,
                                    field_to_join_on,
                                    nlpql_feature_list)

    elif 'not' == operator:
        pipeline = _logical_a_not_b(pipeline,
                                    field_to_join_on,
                                    nlpql_feature_list[0],
                                    nlpql_feature_list[1])

    else:
        print('mongo_logic_expr: unknown operator: {0}'.format(operator))
        pipeline = []

    return pipeline


###############################################################################
def logic_expr_not_a(pipeline, field_to_join_on, nlpql_feature):
    """
    Build a MongoDB aggregation pipeline to compute the expression 'not A',
    where A is a set of MongoDB documents. The 'not' operator is applied to
    the nlpql_feature field of each document.
    """

    pipeline = _append_logical_not_a(pipeline, field_to_join_on, nlpql_feature)
    return pipeline
