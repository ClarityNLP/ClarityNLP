grammar nlpql_parser;

options { tokenVocab=nlpql_lexer; }

// TODO no strings on names

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
    termSet |
    documentSet |
    cohort |
    population |
    define |
    context
    )
    version?
    description?
    SEMI
    ;

version:
    VERSION STRING
    ;

phenotypeName:
    PHENOTYPE_NAME STRING
    ;

description:
    DESCRIPTION STRING
    ;

dataModel:
    DATAMODEL (OMOP|STRING) VERSION? STRING?
    ;

include:
    INCLUDE (CLARITY_CORE|OHDSI_HELPERS|STRING) VERSION? STRING? CALLED IDENTIFIER
    ;

codeSystem:
    CODE_SYSTEM pair
    ;

valueSet:
    VALUE_SET pairMethod
    ;

documentSet:
    DOCUMENT_SET pairMethod
    ;


termSet:
    TERM_SET pairStringArray
    ;

cohort:
    COHORT pairMethod
    ;

population:
    DEFAULT? POPULATION STRING
    ;

context:
    CONTEXT (PATIENT|DOCUMENT)
    ;

define:
    DEFINE finalModifier? defineName COLON (dataEntity | operation)
    ;

finalModifier:
    FINAL
    ;

defineName:
    IDENTIFIER
    ;

dataEntity:
     methodCall
    ;

operation:
    WHERE? expression
    ;

expression:
    operand |
    operand (binaryOperator operand)*
    ;

unaryOperator:
    NOT
    ;

comparisonOperator:
    GT |
    LT |
    GTE |
    LTE |
    EQUAL |
    NOT_EQUAL
;

binaryOperator:
    AND |
    OR |
    PLUS |
    MINUS |
    MULT |
    DIV |
    CARET |
    MOD
;

operand:
    value
    ;


methodCall:
    IDENTIFIER dotIdentifier L_PAREN value (COMMA value)* R_PAREN
    ;

dotIdentifier:
    DOT IDENTIFIER
    ;
    
pairMethod:
    STRING COLON methodCall
    ;

pairStringArray:
    STRING COLON (array|STRING)
;


modifiers:
    DEFAULT |
    FINAL
    ;

obj: L_CURLY pair (COMMA pair)* R_CURLY
   | L_CURLY R_CURLY
   ;

pair: (STRING | named) COLON value
   ;

named:
    CODE_SYSTEM |
    VALUE_SET |
    TERM_SET |
    DOCUMENT_SET |
    COHORT |
    POPULATION |
    DATAMODEL;

array: L_BRACKET value (COMMA value)* R_BRACKET
   | L_BRACKET R_BRACKET
   ;

value: STRING
   | DECIMAL
   | obj
   | array
   | BOOL
   | NULL
   | ALL
   | IDENTIFIER
   | IDENTIFIER dotIdentifier?
   ;

