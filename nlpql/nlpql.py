import antlr4

from data_access import PhenotypeModel, PhenotypeDefine

if __name__ is not None and "." in __name__:
    from .nlpql_parserParser import *
    from .nlpql_lexer import *
else:
    from nlpql_parserParser import *
    from nlpql_lexer import *


def get_value_context(value_context: nlpql_parserParser.ValueContext):
    value = None

    if len(value_context.children) == 1:
        value = value_context.getText().strip('"')
    # TODO other data types...

    return value


def get_qualified_name(qualified_name: nlpql_parserParser.QualifiedNameContext):
    return qualified_name.getText()


def get_method_call(method_call: nlpql_parserParser.MethodCallContext):
    full_name = get_qualified_name(method_call.getChild(0)).split('.', 1)
    library = full_name[0]
    function_name = full_name[1]
    arguments = list()
    for c in method_call.getChildren():
        if type(c) == nlpql_parserParser.ValueContext:
            arguments.append(get_value_context(c))

    return {
        "library": library,
        "funct": function_name,
        "arguments": arguments
    }


def get_pair_method(pair_context: nlpql_parserParser.PairMethodContext):
    name = pair_context.getChild(0).getText()
    method_info = get_method_call(pair_context.getChild(2))
    return {
        "name": name,
        "method": method_info
    }


def get_identifier_pair(identifier: nlpql_parserParser.IdentifierPairContext):
    name = identifier.getChild(0).getText()
    value = get_value_context(identifier.getChild(2))

    return {
        'name': name,
        'value': value
    }


def handle_phenotype_name(context, phenotype: PhenotypeModel):
    print('phenotype_name')
    previous = ''
    phenotype_def = None
    for c in context.getChildren():
        if previous == 'phenotype':
            desc = c.getText()
            phenotype_def = PhenotypeDefine(desc, previous)
        elif type(c) == nlpql_parserParser.VersionContext:
            version = c.getChild(1).getText().strip('"')
            phenotype_def['version'] = version

        previous = c.getText()
    phenotype.phenotype = phenotype_def


def handle_description(context, phenotype: PhenotypeModel):
    phenotype.description = context.getChild(1).getText()


def handle_data_model(context, phenotype: PhenotypeModel):
    print('data model')
    previous = ''
    phenotype_def = None
    for c in context.getChildren():
        if previous == 'datamodel':
            desc = c.getText()
            phenotype_def = PhenotypeDefine(desc, previous)
        elif type(c) == nlpql_parserParser.VersionContext:
            version = c.getChild(1).getText().strip('"')
            phenotype_def['version'] = version

        previous = c.getText()
    if not phenotype.data_models:
        phenotype.data_models = list()

    phenotype.data_models.append(phenotype_def)


def handle_include(context, phenotype: PhenotypeModel):
    print('include')

    # ohdsi_helpers = PhenotypeDefine('OHDSIHelpers', 'include', version='1.0', alias='OHDSI')
    # include OHDSIHelpers version "1.0" called OHDSI;

    phenotype_def = None
    previous = ''
    for c in context.getChildren():
        if previous == 'include':
            desc = c.getText()
            phenotype_def = PhenotypeDefine(desc, previous)
        elif previous == 'called':
            alias = c.getText()
            phenotype_def['alias'] = alias
        elif type(c) == nlpql_parserParser.VersionContext:
            version = c.getChild(1).getText().strip('"')
            phenotype_def['version'] = version

        previous = c.getText()

    if not phenotype.includes:
        phenotype.includes = list()

    phenotype.includes.append(phenotype_def)


def handle_code_system(context, phenotype: PhenotypeModel):
    print('code system')

    # codesystem OMOP: "http://omop.org";
    # omop = PhenotypeDefine('OMOP', 'codesystem', values=['http://omop.org'])

    identifier = context.getChild(1)
    kv = get_identifier_pair(identifier)

    if type(kv['value']) == list:
        phenotype_def = PhenotypeDefine(kv['name'], 'codesystem', values=kv['value'])
    else:
        vals = list()
        vals.append(kv['value'])
        phenotype_def = PhenotypeDefine(kv['name'], 'codesystem', values=vals)

    if not phenotype.code_systems:
        phenotype.code_systems = list()

    phenotype.code_systems.append(phenotype_def)


def handle_value_set(context, phenotype: PhenotypeModel):
    print('value set')

    # Sepsis = PhenotypeDefine('Sepsis', 'valueset', library='OHDSI',
    #                          funct='getConceptSet',
    #                          arguments=['assets/Sepsis.json'])
    # valueset RigorsConcepts:OHDSI.getConceptSet("assets/RigorsConcepts.json");
    call = get_pair_method(context.getChild(1))
    name = call["name"]
    library = call["method"]["library"]
    funct = call["method"]["funct"]
    arguments = call["method"]["arguments"]

    phenotype_def = PhenotypeDefine(name, 'valueset', library=library,
                                    funct=funct, arguments=arguments)

    if not phenotype.value_sets:
        phenotype.value_sets = list()
    phenotype.value_sets.append(phenotype_def)


def handle_term_set(context, phenotype: PhenotypeModel):
    print('term set')
    return {}


def handle_document_set(context, phenotype: PhenotypeModel):
    print('document set')
    return {}


def handle_cohort(context, phenotype: PhenotypeModel):
    print('cohort')
    return {}


def handle_context(context, phenotype: PhenotypeModel):
    print('context')
    return {}


def handle_define(context, phenotype: PhenotypeModel):
    print('define')
    final = False
    define_name = ''
    found = list()
    children = context.getChildren()
    for child in children:
        if not child == antlr4.tree.Tree.TerminalNodeImpl:
            if type(child) == nlpql_parserParser.FinalModifierContext:
                final = True
            elif type(child) == nlpql_parserParser.DefineNameContext:
                define_name = child.getText()
            elif type(child) == nlpql_parserParser.DefineSubjectContext:
                found.extend(handle_define_subject(child, phenotype))


def handle_define_subject(context, phenotype: PhenotypeModel):
    children = context.getChildren()
    matches = list()
    for child in children:
        if not child == antlr4.tree.Tree.TerminalNodeImpl:
            if type(child) == nlpql_parserParser.OperationContext:
                matches.append(handle_operation(child, phenotype))
            elif type(child) == nlpql_parserParser.DataEntityContext:
                matches.append(handle_data_entity(child, phenotype))
    return matches


def handle_data_entity(context, phenotype: PhenotypeModel):
    print('data entity')
    print(context)
    return {}


def handle_operation(context, phenotype: PhenotypeModel):
    print(context)
    print('operation')
    return {}


handlers = {
    nlpql_parserParser.PhenotypeNameContext: handle_phenotype_name,
    nlpql_parserParser.DataModelContext: handle_data_model,
    nlpql_parserParser.IncludeContext: handle_include,
    nlpql_parserParser.CodeSystemContext: handle_code_system,
    nlpql_parserParser.ValueSetContext: handle_value_set,
    nlpql_parserParser.TermSetContext: handle_term_set,
    nlpql_parserParser.DocumentSetContext: handle_document_set,
    nlpql_parserParser.DefineContext: handle_define,
    nlpql_parserParser.ContextContext: handle_context,
    nlpql_parserParser.CohortContext: handle_cohort,
    nlpql_parserParser.DescriptionContext: handle_description
}


def handle_expression(expr):
    has_errors = False
    has_warnings = False
    errors = []
    unknown = []
    p = PhenotypeModel()
    for child in expr.getChildren():
        if type(child) == nlpql_parserParser.StatementContext:
            statement_members = child.getChildren()
            for stmt in statement_members:
                stmt_type = type(stmt)
                if not stmt_type == antlr4.tree.Tree.TerminalNodeImpl:
                    if stmt_type == antlr4.tree.Tree.ErrorNodeImpl:
                        has_errors = True
                        errors.append(stmt)
                    elif stmt_type in handlers:
                        try:
                            handlers[stmt_type](stmt, p)
                        except Exception as ex:
                            has_errors = True
                            errors.append(ex)
                    else:
                        has_warnings = True
                        unknown.append(child)
                        print('UNKNOWN: ' + child.getText())

    return {
        "has_warnings": has_warnings,
        "has_errors": has_errors,
        "errors": errors,
        "warnings": unknown,
        "phenotype": p
    }


def run_parser(nlpql_txt: str):
    lexer = nlpql_lexer(antlr4.InputStream(nlpql_txt))
    stream = antlr4.CommonTokenStream(lexer)
    parser = nlpql_parserParser(stream)
    tree = parser.validExpression()
    results = handle_expression(tree)
    if results['has_errors'] or results['has_warnings']:
        print(results)
    else:
        print('NLPQL parsed successfully')
        print(results['phenotype'].to_json())


if __name__ == '__main__':
    with open('samples/simple.nlpql') as f:
        nlpql_txt = f.read()
        run_parser(nlpql_txt)
