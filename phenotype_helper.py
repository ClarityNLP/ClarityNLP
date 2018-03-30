from data_access import PhenotypeModel, PipelineConfig, PhenotypeEntity


def get_terms(model: PhenotypeModel):
    terms = dict()
    if model:
        if model.term_sets and len(model.term_sets) > 0:
            for t in model.term_sets:
                terms[t['name']] = t['values']
        # TODO expand concept_sets

    return terms


def get_terms_by_keys(term_dict, term_keys: list, concept_keys: list):
    terms = list()
    for k in term_keys:
        terms.extend(term_dict[k])
    for k in concept_keys:
        terms.extend(term_dict[k])

    return terms


def get_report_tags(model):
    types = dict()
    # TODO
    if model.document_sets:
        for d in model.document_sets:
            if d['library'] == "Clarity" and d['funct'] == "createReportTagList":
                types[d['name']] = d['arguments']
    return types


def get_report_tags_by_keys(report_tag_dict, keys: list):
    tags = list()
    for k in keys:
        tags.extend(report_tag_dict[k])
    return tags


def data_entities_to_pipelines(e: PhenotypeEntity, report_tags, all_terms, owner, debug):
    if e['named_arguments'] is None:
        e['named_arguments'] = dict()
    if 'value_sets' not in e['named_arguments']:
        e['named_arguments']['value_sets'] = []
    if 'termsets' not in e['named_arguments']:
        e['named_arguments']['termsets'] = []

    if e['library'] == "Clarity":
        # config_type, name, description, terms
        tags = get_report_tags_by_keys(report_tags, e['named_arguments']['documentsets'])
        if debug:
            limit = 100
        else:
            limit = 0
        pipeline = PipelineConfig(e['funct'], e['name'],
                                  get_terms_by_keys(all_terms, e['named_arguments']['termsets'],
                                                    e['named_arguments']['value_sets']
                                                    ),
                                  owner=owner,
                                  limit=limit,
                                  report_tags=tags)
        return pipeline
    else:
        raise ValueError("External pipelines not yet supported")


def get_pipelines_from_phenotype(model: PhenotypeModel):
    pipelines = list()
    if model and model.data_entities and len(model.data_entities) > 0:
        all_terms = get_terms(model)
        report_tags = get_report_tags(model)
        for e in model.data_entities:
            pipelines.append(data_entities_to_pipelines(e, report_tags, all_terms, model.owner, model.debug))
    return pipelines
