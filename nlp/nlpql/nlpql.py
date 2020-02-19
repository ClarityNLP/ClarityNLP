import antlr4
import traceback
from data_access import PhenotypeModel, PhenotypeDefine, PhenotypeEntity, PhenotypeOperations
from claritynlp_logging import log, ERROR, DEBUG

if __name__ is not None and "." in __name__:
    from .nlpql_parserParser import *
    from .nlpql_lexer import *
else:
    from nlpql_parserParser import *
    from nlpql_lexer import *


def get_value_context(value_context: nlpql_parserParser.ValueContext):
    value = None

    children_count = value_context.getChildCount()

    if children_count == 0:
        value = value_context.getText()
    elif children_count == 1:
        child = value_context.getChild(0)
        txt = value_context.getText().strip('"')
        if type(child) == nlpql_parserParser.ArrayContext:
            value = get_array_context(child)
        elif type(child) == nlpql_parserParser.ObjContext:
            value = dict()
            for c in child.getChildren():
                if type(c) == nlpql_parserParser.PairContext:
                    pair = get_pair_context(c)
                    c_name = pair["name"]
                    c_value = pair["value"]
                    value[c_name] = c_value
        else:
            value = txt
    else:
        value = list()
        for c in value_context.getChildren():
            if type(c) == nlpql_parserParser.ArrayContext:
                value.append(get_value_context(c))
        # TODO still need to clean this up some.

    return value


def get_array_context(array_context: nlpql_parserParser.ArrayContext):
    ary = list()
    for c in array_context.getChildren():
        if type(c) == nlpql_parserParser.ValueContext:
            ary.append(get_value_context(c))

    return ary


def get_qualified_name(qualified_name: nlpql_parserParser.QualifiedNameContext):
    return qualified_name.getText()


def get_method_call(method_call: nlpql_parserParser.MethodCallContext):
    full_name = get_qualified_name(method_call.getChild(0)).split('.', 1)
    library = full_name[0]
    function_name = full_name[1]
    arguments = list()
    num__value_children = 0
    named_arguments = None
    last_value_type = None
    for c in method_call.getChildren():
        if type(c) == nlpql_parserParser.ValueContext:
            num__value_children += 1
            value = get_value_context(c)
            arguments.append(value)
            last_value_type = type(value)

    if num__value_children == 1 and last_value_type == dict:
        named_arguments = arguments[0]
        arguments = None

    return {
        "library": library,
        "funct": function_name,
        "arguments": arguments,
        "named_arguments": named_arguments
    }


def get_pair_context(pair_context: nlpql_parserParser.PairContext):
    c_name = pair_context.getChild(0).getText().strip('"')
    c_value = get_value_context(pair_context.getChild(2))

    if type(c_value) == str:
        l_val = c_value.lower()
        if l_val == "true":
            c_value = True
        elif l_val == "false":
            c_value = False
        elif l_val.isdigit():
            c_value = int(l_val)
        elif l_val.replace('.', '', 1).isdigit():
            c_value = float(l_val)
    return {
        "name": c_name,
        "value": c_value
    }


def get_pair_method(pair_context: nlpql_parserParser.PairMethodContext):
    name = pair_context.getChild(0).getText()
    method_info = get_method_call(pair_context.getChild(2))
    return {
        "name": name,
        "method": method_info
    }


def get_pair_array(pair_context: nlpql_parserParser.PairArrayContext):
    name = pair_context.getChild(0).getText()
    array = get_array_context(pair_context.getChild(2))
    return {
        "name": name,
        "array": array
    }


def get_identifier_pair(identifier: nlpql_parserParser.IdentifierPairContext):
    name = identifier.getChild(0).getText()
    value = get_value_context(identifier.getChild(2))

    return {
        'name': name,
        'value': value
    }


# by existing, this sets debug to True
def handle_debug(context, phenotype: PhenotypeModel):
    phenotype.debug = True


def handle_limit(context, phenotype: PhenotypeModel):
    limit = context.getChild(1).getText()
    if len(limit) > 0:
        phenotype.limit = int(limit)


def handle_phenotype_name(context, phenotype: PhenotypeModel):
    # log('phenotype_name')
    previous = ''
    phenotype_def = None
    name = ''
    for c in context.getChildren():
        if previous == 'phenotype':
            desc = c.getText().replace('"', '').strip()
            phenotype_def = PhenotypeDefine(desc, previous)
            name = desc
        elif type(c) == nlpql_parserParser.VersionContext:
            version = c.getChild(1).getText().strip('"')
            phenotype_def['version'] = version

        previous = c.getText()
    phenotype.name = name
    phenotype.phenotype = phenotype_def


def handle_description(context, phenotype: PhenotypeModel):
    phenotype.description = context.getChild(1).getText()


def handle_data_model(context, phenotype: PhenotypeModel):
    # log('data model')
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
    # log('include')

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
    # log('code system')

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
    # log('value set')

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
    # log('term set')
    # termset RigorsTerms: ["Rigors",
    # "Rigoring",
    # "Rigours",
    # "Rigouring",
    # "Chill",
    # "Chills",
    # "Shivers",
    # "Shivering",
    # "Teeth chattering"];
    # Sepsis = PhenotypeDefine("Sepsis", "termset", values=['Sepsis', 'Systemic infection'])
    ts = get_pair_array(context.getChild(1))
    pd = PhenotypeDefine(ts["name"], "termset", values=ts["array"])

    if not phenotype.term_sets:
        phenotype.term_sets = list()
    phenotype.term_sets.append(pd)


def handle_document_set(context, phenotype: PhenotypeModel):
    # log('document set')
    # documentset ProviderNotes: Clarity.createDocumentList("'Physician' OR 'Nurse' OR 'Note' OR 'Discharge Summary'");

    call = get_pair_method(context.getChild(1))
    name = call["name"]
    library = call["method"]["library"]
    funct = call["method"]["funct"]
    arguments = call["method"]["arguments"]
    named_arguments = call["method"]["named_arguments"]

    phenotype_def = PhenotypeDefine(name, 'documentset', library=library,
                                    funct=funct, arguments=arguments, named_arguments=named_arguments)

    if not phenotype.document_sets:
        phenotype.document_sets = list()
    phenotype.document_sets.append(phenotype_def)


def handle_cohort(context, phenotype: PhenotypeModel):
    log('cohort')
    call = get_pair_method(context.getChild(1))
    name = call["name"]
    library = call["method"]["library"]
    funct = call["method"]["funct"]
    arguments = call["method"]["arguments"]
    named_arguments = call["method"]["named_arguments"]

    phenotype_def = PhenotypeDefine(name, 'cohort', library=library,
                                    funct=funct, arguments=arguments,
                                    named_arguments=named_arguments)

    if not phenotype.cohorts:
        phenotype.cohorts = list()
    phenotype.cohorts.append(phenotype_def)


def handle_context(context, phenotype: PhenotypeModel):
    phenotype.context = context.getChild(1).getText()


def handle_define(context, phenotype: PhenotypeModel):
    log('define')
    final = False
    define_name = ''
    children = context.getChildren()
    for child in children:
        if not child == antlr4.tree.Tree.TerminalNodeImpl:
            if type(child) == nlpql_parserParser.FinalModifierContext:
                final = True
            elif type(child) == nlpql_parserParser.DefineNameContext:
                define_name = child.getText()
            elif type(child) == nlpql_parserParser.DefineSubjectContext:
                handle_define_subject(child, phenotype, define_name, final)


def handle_define_subject(context, phenotype: PhenotypeModel,  define_name, final):
    children = context.getChildren()
    for child in children:
        if type(child) == nlpql_parserParser.OperationContext:
            handle_operation(child, phenotype, define_name, final)
        elif type(child) == nlpql_parserParser.DataEntityContext:
            handle_data_entity(child, phenotype,  define_name, final)


def handle_data_entity(context, phenotype: PhenotypeModel, define_name, final):
    log('data entity')
    pe = PhenotypeEntity(define_name, 'define', final=final)
    call = get_method_call(context.getChild(0))
    # hasSepsis = PhenotypeEntity('hasSepsis', 'define',
    #                             library='ClarityNLP',
    #                             funct='ProviderAssertion',
    #                             named_arguments={
    #                                 "termsets": ['Sepsis'],
    #                                 "documentsets": [
    #                                     'ProviderNotes',
    #                                     "Radiology"
    #                                 ]
    #                             })
    pe["funct"] = call["funct"]
    pe["library"] = call["library"]
    named_args = call["named_arguments"]
    args = call["arguments"]
    if named_args:
        pe["named_arguments"] = named_args
    if args and len(args) > 0:
        pe["arguments"] = args
    if not phenotype.data_entities:
        phenotype.data_entities = list()

    phenotype.data_entities.append(pe)


def is_operator(c):
    return type(c) == nlpql_parserParser.ComparisonOperatorContext or type(c) == nlpql_parserParser.LogicalOperatorContext or type(c) == nlpql_parserParser.UnaryOperatorContext


def get_atomic_expression(context: nlpql_parserParser.ExpressionAtomContext):
    atomic = None
    #     : value
    # | methodCall
    # | unaryOperator expressionAtom
    # | L_PAREN expression (COMMA expression)* R_PAREN
    num_childen = len(context.children)
    first = context.getChild(0)
    main_type = type(first)
    if num_childen == 1:
        if type(first) == nlpql_parserParser.ValueContext:
            atomic = get_value_context(first)
        elif type(first) == nlpql_parserParser.MethodCallContext:
            atomic = get_method_call(first)
    else:
        for c in context.getChildren():
            log('TODO')
            log(c)
    return {
        "atomic_value": atomic,
        "main_type": main_type

    }


def get_predicate_context(context: nlpql_parserParser.PredicateContext):

    #     left=predicate comparisonOperator right=predicate
    # | expressionAtom
    predicates = list()
    for c in context.getChildren():
        txt = c.getText()
        log(txt)

        if type(c) == nlpql_parserParser.ExpressionAtomContext:
            expression_atom = get_atomic_expression(c)
            atom_value = expression_atom["atomic_value"]
            if atom_value:
                if type(atom_value) == list:
                    predicates.extend(atom_value)
                else:
                    predicates.append(atom_value)
        # TODO

    return predicates


def get_generic_expression(expression: nlpql_parserParser.ExpressionContext, entities: list(), operator: list()):
    txt = expression.getText()
    if expression.getChildCount() == 1:
        child = expression.getChild(0)
        if type(child) == nlpql_parserParser.LogicalOperatorContext:
            operator.append(txt)
        else:
            entities.append(txt)
    else:
        for exp in expression.getChildren():
            txt = exp.getText()
            if type(exp) == nlpql_parserParser.LogicalOperatorContext:
                operator.append(txt)
            else:
                get_generic_expression(exp, entities, operator)

    return entities, operator


def get_pretty_text(expression):

    if expression.getChildCount() == 1:
        expression_text = expression.getText()
    else:
        expression_text = ''
        for c in expression.getChildren():
            if type(c) == nlpql_parserParser.LogicalOperatorContext or type(c) == nlpql_parserParser.ComparisonOperatorContext:
                expression_text += ' %s ' % c.getText()
            else:
                if c.getChildCount() == 0:
                    expression_text += c.getText()
                else:
                    expression_text += (get_pretty_text(c))
    
    return expression_text


def get_not_expression(expression: nlpql_parserParser.ExpressionContext, define_name, final):
    log(expression)
    entities = list()
    operator = ""

    op = PhenotypeOperations(define_name, operator, entities, final=final, raw_text=get_pretty_text(expression))
    return op


def get_logical_expression(expression: nlpql_parserParser.ExpressionContext, define_name, final):
    log(expression)
    entities = list()
    operator = list()

    for c in expression.getChildren():
        if type(c) == nlpql_parserParser.ExpressionContext:
            get_generic_expression(c, entities, operator)

        elif type(c) == nlpql_parserParser.LogicalOperatorContext:
            operator.append(c.getText())

    op = PhenotypeOperations(define_name, operator[0], entities, final=final, raw_text=get_pretty_text(expression))
    return op


def get_predicate_expression(expression: nlpql_parserParser.PredicateContext, define_name, final):
    log(expression)
    entities = list()
    operator = ""
    for c in expression.getChildren():
        if is_operator(c):
            operator = c.getText().strip('"')
        elif type(c) == nlpql_parserParser.PredicateContext:
            pc = get_predicate_context(c)
            if pc:
                if type(pc) == list:
                    entities.extend(pc)
                else:
                    entities.append(pc)

    op = PhenotypeOperations(define_name, operator, entities, final=final, raw_text=get_pretty_text(expression))
    return op


def get_predicate_boolean(expression: nlpql_parserParser.PredicateBooleanContext, define_name, final):
    log(expression)
    operator = ""
    entities = list()

    op = PhenotypeOperations(define_name, operator, entities, final=final, raw_text=get_pretty_text(expression))
    return op


def handle_operation(context, phenotype: PhenotypeModel, define_name, final):
    log('operation')

    # SepsisState = PhenotypeOperations('SepsisState', 'OR', ['onVentilator', 'hasSepsis'], final=True)

    # : notOperator=(NOT | BANG) expression
    # | expression logicalOperator expression
    # | predicate IS NOT? BOOL
    expression_context = context.getChild(1)
    first = expression_context.getChild(0)

    res = None
    if type(first) == nlpql_parserParser.NotOperatorContext:
        res = get_not_expression(expression_context, define_name, final)
    elif type(first) == nlpql_parserParser.ExpressionContext:
        res = get_logical_expression(expression_context, define_name, final)
    elif type(first) == nlpql_parserParser.PredicateBooleanContext:
        res = get_predicate_boolean(expression_context, define_name, final)
    elif type(first) == nlpql_parserParser.PredicateContext:
        res = get_predicate_expression(expression_context.getChild(0), define_name, final)

    if not phenotype.operations:
        phenotype.operations = list()

    if res:
        phenotype.operations.append(res)


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
    nlpql_parserParser.DescriptionContext: handle_description,
    nlpql_parserParser.DebuggerContext: handle_debug,
    nlpql_parserParser.LimitContext: handle_limit
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
                            log(ex, ERROR)
                            traceback.print_exc(file=sys.stderr)
                            error = ''.join(traceback.format_stack())
                            errors.append(error)
                    else:
                        has_warnings = True
                        unknown.append(child)
                        log('UNKNOWN child: ' + child.getText())

    return {
        "has_warnings": has_warnings,
        "has_errors": has_errors,
        "errors": errors,
        "warnings": unknown,
        "phenotype": p,
        "valid": not has_errors and not has_warnings
    }


def run_nlpql_parser(nlpql_txt: str):
    lexer = nlpql_lexer(antlr4.InputStream(nlpql_txt))
    stream = antlr4.CommonTokenStream(lexer)
    parser = nlpql_parserParser(stream)
    tree = parser.validExpression()
    res = handle_expression(tree)
    return res


if __name__ == '__main__':
    # with open('samples/sample2.nlpql') as f:
    #     nlpql_txt = f.read()
    #     results = run_nlpql_parser(nlpql_txt)
    #     if results['has_errors'] or results['has_warnings']:
    #         log(results)
    #     else:
    #         log('NLPQL parsed successfully')
    #         log(results['phenotype'].to_json())
    log("init nlpql parsing...", DEBUG)
