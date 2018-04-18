import antlr4
import json
from data_access import PhenotypeModel, PhenotypeEntity, PhenotypeDefine, PhenotypeOperations
if __name__ is not None and "." in __name__:
    from .nlpql_parserParser import *
    from .nlpql_lexer import *
else:
    from nlpql_parserParser import *
    from nlpql_lexer import *


def handle_phenotype_name(context, phenotype: PhenotypeModel):
    print('phenotype_name')
    previous = ''
    phenotype_def = None
    desc = ''
    for c in context.getChildren():
        if previous == 'phenotype':
            desc = c.getText()
            phenotype_def = PhenotypeDefine(desc, previous)


        previous = c.getText()
    phenotype.phenotype = phenotype_def


def handle_version(context, phenotype: PhenotypeModel):
    print('version')
    return {}


def handle_description(context, phenotype: PhenotypeModel):
    print('description')
    return {}


def handle_data_model(context, phenotype: PhenotypeModel):
    print('data model')
    return {}


def handle_include(context, phenotype: PhenotypeModel):
    print('include')
    return {}


def handle_code_system(context, phenotype: PhenotypeModel):
    print('code system')
    return {}


def handle_value_set(context, phenotype: PhenotypeModel):
    print('value set')
    return {}


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
    children = context.getChildren()
    for child in children:
        if not child == antlr4.tree.Tree.TerminalNodeImpl:
            if type(child) == nlpql_parserParser.FinalModifierContext:
                final = True
            elif type(child) == nlpql_parserParser.DefineNameContext:
                define_name = child.getText()
            elif type(child) == nlpql_parserParser.DefineSubjectContext:
                handle_define_subject(child, phenotype)
    return phenotype


def handle_define_subject(context, phenotype: PhenotypeModel):
    children = context.getChildren()
    for child in children:
        if not child == antlr4.tree.Tree.TerminalNodeImpl:
            if type(child) == nlpql_parserParser.OperationContext:
                handle_operation(child, phenotype)
            elif type(child) == nlpql_parserParser.DataEntityContext:
                handle_data_entity(child, phenotype)


def handle_data_entity(context, phenotype: PhenotypeModel):
    print('data entity')
    print(context)
    return {}


def handle_operation(context, phenotype: PhenotypeModel):
    print(context)
    print('operation')
    return {}


handlers = {
    nlpql_parserParser.PhenotypeNameContext:handle_phenotype_name,
    nlpql_parserParser.VersionContext:handle_version,
    nlpql_parserParser.DataModelContext:handle_data_model,
    nlpql_parserParser.IncludeContext:handle_include,
    nlpql_parserParser.CodeSystemContext:handle_code_system,
    nlpql_parserParser.ValueSetContext:handle_context,
    nlpql_parserParser.TermSetContext:handle_term_set,
    nlpql_parserParser.DocumentSetContext:handle_document_set,
    nlpql_parserParser.DefineContext:handle_define,
    nlpql_parserParser.ContextContext:handle_context,
    nlpql_parserParser.CohortContext:handle_cohort,
    nlpql_parserParser.DescriptionContext:handle_description
}


def handle_expression(expr):
    has_errors = False
    has_warnings = False
    errors = []
    unknown = []
    phenotype = PhenotypeModel()
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
                        obj = handlers[stmt_type](stmt, phenotype)
                    else:
                        has_warnings = True
                        unknown.append(child)
                        print('UNKNOWN: ' + child.getText())

    return {
        "has_warnings": has_warnings,
        "has_errors": has_errors,
        "errors": errors,
        "warnings": unknown,
        "phenotype": phenotype
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


if __name__ == '__main__':
    with open('../samples/simple.nlpql') as f:
        nlpql_txt = f.read()
        run_parser(nlpql_txt)
