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
    termSet |
    documentSet |
    cohort |
    population |
    define |
    context
    )
    SEMI
    ;

version:
    VERSION versionValue
    ;

versionValue:
    STRING
    ;

phenotypeName:
    PHENOTYPE_NAME STRING version?
    ;

description:
    DESCRIPTION STRING
    ;

dataModel:
    DATAMODEL (OMOP|STRING) version?
    ;

include:
    INCLUDE (CLARITY_CORE|OHDSI_HELPERS|STRING) version? CALLED IDENTIFIER
    ;

codeSystem:
    CODE_SYSTEM identifierPair
    ;

valueSet:
    VALUE_SET pairMethod
    ;

documentSet:
    DOCUMENT_SET pairMethod
    ;


termSet:
    TERM_SET pairArray
    ;

cohort:
    COHORT pairMethod
    ;

population:
    DEFAULT? POPULATION IDENTIFIER
    ;

context:
    CONTEXT (PATIENT|DOCUMENT)
    ;

define:
    DEFINE finalModifier? defineName COLON defineSubject
    ;

defineSubject:
    operation |
    dataEntity
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

expression
    : notOperator=(NOT | BANG) expression
    | expression logicalOperator expression
    | predicate IS NOT? BOOL
    | predicate
    ;

predicate:
    predicate NOT? IN L_PAREN (expression) R_PAREN
    | predicate IS nullNotnull
    | left=predicate comparisonOperator right=predicate
    | predicate NOT? BETWEEN predicate AND predicate
    | predicate NOT? LIKE predicate (STRING)?
    | expressionAtom
    ;

nullNotnull
    : NOT? (NULL)
    ;

expressionAtom
    : value
    | methodCall
    | unaryOperator expressionAtom
    | L_PAREN expression (COMMA expression)* R_PAREN
    ;

unaryOperator:
    NOT
    ;

logicalOperator:
    AND |
    OR
    ;

comparisonOperator:
    GT |
    LT |
    GTE |
    LTE |
    EQUAL |
    NOT_EQUAL
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
    qualifiedName L_PAREN value (COMMA value)* R_PAREN
    ;

qualifiedName:
    IDENTIFIER (DOT IDENTIFIER)*
    ;

    
pairMethod:
    IDENTIFIER COLON methodCall
    ;

pairArray:
    IDENTIFIER COLON (array|STRING)
;


modifiers:
    DEFAULT |
    FINAL
    ;

obj: L_CURLY pair (COMMA pair)* R_CURLY
   | L_CURLY R_CURLY
   ;

pair:
    (STRING | named) COLON value
   ;

identifierPair:
    (IDENTIFIER | OMOP) COLON value
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

value:
    STRING
   | DECIMAL
   | FLOAT
   | obj
   | array
   | BOOL
   | NULL
   | ALL
   | IDENTIFIER
   | qualifiedName
   | TIME
   ;

