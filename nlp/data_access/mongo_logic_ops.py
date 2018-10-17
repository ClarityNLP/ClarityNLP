#!/usr/bin/env python3
"""
"""

###############################################################################
def append_logical_and(pipeline,
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
def append_logical_or(pipeline, nlpql_feature_list):
    """
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
def logical_and(pipeline, field_to_join_on, nlpql_feature_list):

    id_string = "${0}".format(field_to_join_on)
    feature_count = len(nlpql_feature_list)
    
    append_logical_and(pipeline,
                       id_string,
                       feature_count,
                       nlpql_feature_list)
    return pipeline


###############################################################################
def logical_or(pipeline, nlpql_feature_list):

    append_logical_or(pipeline, nlpql_feature_list)
    return pipeline


###############################################################################
def logic_expr(pipeline, operator, field_to_join_on, nlpql_feature_list):
    """
    """

    if 'or' == operator:
        return logical_or(pipeline, nlpql_feature_list)
    elif 'and' == operator:
        return logical_and(pipeline, field_to_join_on, nlpql_feature_list)
    else:
        print('mongo_logic_expr: unknown operator: {0}'.format(operator))
        return []
