#!/usr/bin/env python3
"""
This module generates the MongoDB result documents that contain the output
from NLPQL expression evaluation.

For import only.
"""

import copy
import datetime
from collections import namedtuple

HISTORY_ELT_FIELDS = [
    'oid', 'pipeline_type', 'nlpql_feature', 'data', 'subject', 'report_id'
]
HistoryElt = namedtuple('HistoryElt', HISTORY_ELT_FIELDS)

PHENOTYPE_INFO_FIELDS = [
    'job_id', 'phenotype_id', 'owner', 'context_field', 'is_final'
]
PhenotypeInfo = namedtuple('PhenotypeInfo', PHENOTYPE_INFO_FIELDS)

HISTORY_FIELD = 'history'

# these fields are not copied from source doc to result doc
_NO_COPY_FIELDS = [
    '_id', 'job_id', 'phenotype_id', 'owner',
    'job_date', 'context_type', 'raw_definition_text',
    'nlpql_feature', 'phenotype_final', HISTORY_FIELD
]


###############################################################################
def flatten(l, ltypes=(list, tuple)):
    """
    Non-recursive list and tuple flattener from
    http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html,
    based on code from Mike Fletcher's BasicTypes library.
    """
    
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
        
    return ltype(l)


###############################################################################
def flatten_nested_lists(obj):
    """
    Remove nested lists in the given dict and return the flattened 
    equivalent. Does some special handling for empty lists or lists containing
    all identical entries, mainly to simplify the results when viewed in Excel.
    """

    for k,v in obj.items():
        # don't flatten the history field
        if HISTORY_FIELD == k:
            continue
        if type(v) == list:
            if 1 == len(v) and '' == v[0]:
                obj[k] = None
            else:
                flattened_list = flatten(v)

                all_none = True
                for item in flattened_list:
                    if item is not None:
                        all_none = False
                        break

                if all_none:
                    obj[k] = None
                else:
                    obj[k] = flattened_list


###############################################################################
def remove_arrays(obj):
    """
    Remove arrays in the result dict by creating numbered fields for
    the array elements.
    """
    to_insert = []
    to_remove = []
    
    for k,v in obj.items():
        if type(v) != list:
            continue

        elt_count = len(v)
        if 1 == elt_count:
            obj[k] = v[0]
        else:
            for i in range(elt_count):
                # use 1-based indexing
                field_name = '{0}_{1}'.format(k, i+1)
                to_insert.append( (field_name, copy.deepcopy(v), i) )
            to_remove.append(k)

    for k in to_remove:
        obj.pop(k, None)
    for k,v,i in to_insert:
        obj[k] = v[i]


###############################################################################
def extract_value(data):
    """
    If data is a single-element list, return element 0. If data is not a
    list, just return the data.
    """

    if isinstance(data, list):
        assert 1 == len(data)
        return data[0]
    else:
        return data


###############################################################################
def init_history(source_doc):
    """
    Initialize the history depending on the pipeline type. The history is a
    list of tuples of this form:

        (pipeline_type, str(_id), nlnpql_feature, values...)

    Returns a HistoryElt namedtuple for the given source document.

    """

    source_nlpql_feature = source_doc['nlpql_feature']
    
    if 'pipeline_type' in source_doc:
        pipeline_type = extract_value(source_doc['pipeline_type'])
        oid = str(source_doc['_id'])

        subject = source_doc['subject']
        report_id = source_doc['report_id']

        if 'ProviderAssertion' == pipeline_type:
            # return the term as the data
            data = extract_value(source_doc['term'])

        elif 'ValueExtractor' == pipeline_type:
            # return the extracted value as the data
            data = extract_value(source_doc['value'])

        elif 'MeasurementFinder' == pipeline_type:
            # return the measurement dimensions as the data
            x = extract_value(source_doc['dimension_X'])
            y = extract_value(source_doc['dimension_Y'])
            z = extract_value(source_doc['dimension_Z'])
            data = [x, y, z]

        else:
            # if a value field is present, use it as the data
            if 'value' in source_doc:
                data = extract_value(source_doc['value'])
            else:
                data = None

    history_elt = HistoryElt(
        oid           = oid,
        pipeline_type = pipeline_type,
        nlpql_feature = source_nlpql_feature,
        data          = data,
        subject       = subject,
        report_id     = report_id
    )

    return history_elt


###############################################################################
def get_default_result_display(ret):
    rd = dict()
    rd['date'] = ''
    rd['sentence'] = ''
    rd['result_content'] = ''

    dates = list()
    sentences = list()
    starts = list()
    ends = list()
    hl = list()
    for k, v in ret.items():
        if not v or (hasattr(v, '__len__') and len(v) == ''):
            continue
        if k.startswith('report_date'):
            dates.append(v)
        if k.startswith('sentence'):
            sentences.append(v)
        if k.startswith('term_'):
            hl.append(v)
        if k.startswith('value'):
            hl.append(v)
        if k.startswith('start_'):
            starts.append(v)
        if k.startswith('end_'):
            ends.append(v)

    # flatten any nested lists
    dates     = flatten(dates)
    sentences = flatten(sentences)
    starts    = flatten(starts)
    ends      = flatten(ends)
    hl        = flatten(hl)
    
    if len(dates) > 0:
        if all(x == dates[0] for x in dates):
            rd['date'] = dates[0]
    if len(sentences) > 0:
        if all(x == sentences[0] for x in sentences):
            rd['sentence'] = sentences[0]
        else:
            rd['sentence'] = ''
        rd['result_content'] = '\n'.join(sentences)

    rd['highlights'] = hl
    rd['start'] = starts
    rd['end'] = ends

    return rd


###############################################################################
def to_math_result_docs(eval_result, phenotype_info, cursor):
    """
    Generate the MongoDB documents that contain the results from evaluation
    of a pure NLPQL mathematical expression.
    """

    output_docs = []

    is_final      = phenotype_info.is_final
    context_field = phenotype_info.context_field

    for doc in cursor:

        # output doc
        ret = {}

        # add doc fields to the output doc as lists
        field_map = {}
        fields = doc.keys()
        fields_to_copy = [f for f in fields if f not in _NO_COPY_FIELDS]
        for f in fields_to_copy:
            if f not in field_map:
                field_map[f] = [doc[f]]
            else:
                field_map[f].append(doc[f])

        for k,v in field_map.items():
            ret[k] = copy.deepcopy(v)

        # set the context field explicitly
        ret[context_field] = doc[context_field]

        ret['job_id']              = phenotype_info.job_id
        ret['phenotype_id']        = phenotype_info.phenotype_id
        ret['owner']               = phenotype_info.owner
        ret['job_date']            = datetime.datetime.now()
        ret['context_type']        = context_field
        ret['raw_definition_text'] = eval_result.expr_text
        ret['nlpql_feature']       = eval_result.nlpql_feature
        ret['phenotype_final']     = is_final

        # use the pipeline_type field to record the type of expression
        ret['pipeline_type'] = 'EvalMathExpr'
        ret["result_display"] = get_default_result_display(ret)

        # documents for math operations are generated from
        # ValueExtractor and other tasks, hence no history field
        assert HISTORY_FIELD not in doc

        # add source _id and nlpql_feature
        if is_final:
            # really need to construct the output doc from the history
            ret['_ids_1'] = str(doc['_id'])
            ret['nlpql_features_1'] = doc['nlpql_feature']
        else:
            history_entry = init_history(doc)
            ret[HISTORY_FIELD] = [history_entry]

        flatten_nested_lists(ret)

        if is_final:
            remove_arrays(ret)

        output_docs.append(ret)

    
    return output_docs


###############################################################################
def to_logic_result_docs(eval_result,
                         phenotype_info,
                         doc_map,
                         oid_list_of_lists):
    """
    Generate the MongoDB documents that contain the results from evaluation
    of a pure NLPQL logical expression.
    """

    output_docs = []

    is_final      = phenotype_info.is_final
    context_field = phenotype_info.context_field
    
    # an 'ntuple' is a list of _id values
    for ntuples in oid_list_of_lists:
        for ntuple in ntuples:
            assert isinstance(ntuple, list)
            if 0 == len(ntuple):
                continue

            # each ntuple supplies the data for a result doc
            ret = {}
            history = []

            # get the shared context field value for this ntuple
            oid = ntuple[0]
            doc = doc_map[oid]
            context_field_value = doc[context_field]

            # include the present ntuple in the history
            for oid in ntuple:
                # get the doc associated with this _id
                doc = doc_map[oid]

                # carry forward the history for this doc, if any
                if HISTORY_FIELD in doc:
                    # mongo converts tuples to lists, so convert to namedtuple
                    for elt in doc[HISTORY_FIELD]:
                        assert isinstance(elt, list)
                        tup = HistoryElt(elt[0], elt[1], elt[2],
                                         elt[3], elt[4], elt[5])
                        history.append(tup)

                # include the present doc in the history
                history_entry = init_history(doc)
                history.append(history_entry)

                assert context_field_value == doc[context_field]

            # add ntuple doc fields to the output doc as lists
            field_map = {}
            for oid in ntuple:
                doc = doc_map[oid]
                fields = doc.keys()
                fields_to_copy = [f for f in fields if f not in _NO_COPY_FIELDS]
                for f in fields_to_copy:
                    if f not in field_map:
                        field_map[f] = [doc[f]]
                    else:
                        field_map[f].append(doc[f])

            for k,v in field_map.items():
                ret[k] = copy.deepcopy(v)

            # set the context field value; same value for all ntuple entries
            ret[context_field] = context_field_value

            # update fields common to AND/OR
            ret['job_id']              = phenotype_info.job_id
            ret['phenotype_id']        = phenotype_info.phenotype_id
            ret['owner']               = phenotype_info.owner
            ret['job_date']            = datetime.datetime.now()
            ret['context_type']        = context_field
            ret['raw_definition_text'] = eval_result.expr_text
            ret['nlpql_feature']       = eval_result.nlpql_feature
            ret['phenotype_final']     = is_final

            # use the pipeline_type field to record the type of expression
            ret['pipeline_type'] = 'EvalLogicExpr'
            ret["result_display"] = get_default_result_display(ret)

            # add source _ids and nlpql_features (1-based indexing)
            if is_final:
                # really need to construct the output doc from the history
                for i in range(len(history)):
                    history_elt = history[i]
                    assert isinstance(history_elt, tuple)
                    field_name = '_ids_{0}'.format(i+1)
                    ret[field_name] = history_elt.oid
                    field_name = 'nlpql_features_{0}'.format(i+1)
                    ret[field_name] = history_elt.nlpql_feature
            else:
                # udpate the history
                ret[HISTORY_FIELD] = copy.deepcopy(history)

            flatten_nested_lists(ret)

            if is_final:
                remove_arrays(ret)

            output_docs.append(ret)

    
    return output_docs
