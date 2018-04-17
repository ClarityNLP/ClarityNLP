/** References from https://github.com/antlr/grammars-v4 */
lexer grammar nlpql_lexer;

// modifiers
DEFAULT: 'default';
FINAL: 'final';

// declares
PHENOTYPE_NAME: 'phenotype';
VERSION: 'version';
DESCRIPTION: 'description';
DATAMODEL: 'datamodel';
INCLUDE: 'include';
CALLED: 'called';
CODE_SYSTEM: 'codesystem';
VALUE_SET: 'valueset';
TERM_SET: 'termset';
DOCUMENT_SET: 'documentset';
COHORT: 'cohort';
POPULATION: 'population';
DEFINE: 'define';
CONTEXT: 'context';


// Custom Clarity Features
OMOP: 'OMOP';
CLARITY_CORE: 'ClarityCore';
OHDSI_HELPERS: 'OHDSIHelpers';
ALL: 'All';
PATIENT: 'Patient';
DOCUMENT: 'Document';

//  Operators
WHERE: 'WHERE';
AND: 'AND';
OR: 'OR';
NOT: 'NOT';
GT: '>';
LT: '<';
LTE:    '<=';
GTE: '>=';
EQUAL: '==';
NOT_EQUAL: '!=';
PLUS:   '+';
MINUS: '-';
MULT: '*';
DIV: '/';
CARET: '^';
MOD: '%';

// Data types
SEMI:               ';';
COLON:              ':';
DOT:                '.';
COMMA:              ',';
L_PAREN:            '(';
R_PAREN:            ')';
L_BRACKET:          '[';
R_BRACKET:          ']';
L_CURLY:            '{';
R_CURLY:            '}';
DECIMAL:    ('0' | [1-9] (Digits? | '_'+ Digits)) [lL]?;
HEX:        '0' [xX] [0-9a-fA-F] ([0-9a-fA-F_]* [0-9a-fA-F])? [lL]?;
OCT:        '0' '_'* [0-7] ([0-7_]* [0-7])? [lL]?;
BINARY:     '0' [bB] [01] ([01_]* [01])? [lL]?;
FLOAT:      (Digits '.' Digits? | '.' Digits) ExponentPart? [fFdD]?
             |       Digits (ExponentPart [fFdD]? | [fFdD])
             ;
HEX_FLOAT:  '0' [xX] (HexDigits '.'? | HexDigits? '.' HexDigits) [pP] [+-]? Digits [fFdD]?;
BOOL:       'true'
            |       'false'
            ;
NULL:       'null';
CHAR:       '\'' (~['\\\r\n] | EscapeSequence) '\'';
STRING:     '"' (~["\\\r\n] | EscapeSequence)* '"';

WS:                 [ \t\r\n\u000C]+ -> channel(HIDDEN);
COMMENT:            '/*' .*? '*/'    -> channel(HIDDEN);
LINE_COMMENT:       '//' ~[\r\n]*    -> channel(HIDDEN);
IDENTIFIER:         LetterOrDigit LetterOrDigit*;

fragment ExponentPart
    : [eE] [+-]? Digits
    ;

fragment EscapeSequence
    : '\\' [btnfr"'\\]
    | '\\' ([0-3]? [0-7])? [0-7]
    | '\\' 'u'+ HexDigit HexDigit HexDigit HexDigit
    ;
fragment HexDigits
    : HexDigit ((HexDigit | '_')* HexDigit)?
    ;
fragment HexDigit
    : [0-9a-fA-F]
    ;
fragment Digits
    : [0-9] ([0-9_]* [0-9])?
    ;
fragment LetterOrDigit
    : Letter
    | [0-9]
    ;
fragment Letter
    : [A-Za-z$_]
    ;