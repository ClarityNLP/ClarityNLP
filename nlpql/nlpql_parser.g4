grammar nlpql_parser;

options { tokenVocab=nlpql_lexer; }

validExpression:
    statement*
    EOF
    ;

statement:
    (phenotypeName |
    description |
    dataModel |
    include |
    codeSystem |
    valueSet |
    termSet
    )
    SEMI
    ;

phenotypeName:
    PHENOTYPE_NAME STRING VERSION? STRING?
    ;

description:
    DESCRIPTION STRING VERSION? STRING?
    ;

dataModel:
    DATAMODEL (OMOP|STRING) VERSION? STRING?
    ;

include:
    INCLUDE (CLARITY_CORE|OHDSI_HELPERS|STRING) VERSION? STRING? CALLED IDENTIFIER
    ;

codeSystem:
    CODE_SYSTEM STRING COLON value
    ;

valueSet:
    VALUE_SET STRING COLON methodCall
    ;

methodCall:
    IDENTIFIER DOT IDENTIFIER L_PAREN value R_PAREN
    ;

termSet:
    TERM_SET STRING COLON (array|STRING)
    ;

obj: L_CURLY pair (COMMA pair)* R_CURLY
   | L_CURLY R_CURLY
   ;

pair: STRING COLON value
   ;

array: L_BRACKET value (COMMA value)* R_BRACKET
   | L_BRACKET R_BRACKET
   ;

value: STRING
   | DECIMAL
   | obj
   | array
   | BOOL
   | NULL
   ;

