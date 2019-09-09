.. _datefinderalgo:

Finding Date Expressions
************************

Overview
========

ClarityNLP includes a module that locates date expressions in clinical text.
By 'date expression' we mean a string such as ``July 20, 1969``, ``7.20.69``,
or something similar. The ``DateFinder`` module scans sentences for date
expressions, extracts them, and generates output in JSON format.

Source Code
===========

The source code for the date finder module is located in
``nlp/algorithms/finder/date_finder.py``.

Inputs
------

A single string, the sentence to be scanned for date expressions.

Outputs
-------

A JSON array containing these fields for each date expression found:

===========  ==============================================================
Field Name   Explanation
===========  ==============================================================
text         string, text of the complete date expression
start        integer, offset of the first character in the matching text
end          integer, offset of the final character in the matching text plus 1
year         integer year
month        integer month (Jan=1, Feb=2, ..., Dec=12)
day          integer day of the month [1, 31]
===========  ==============================================================

All JSON results contain an identical number of fields. Any fields that are
not valid for a given date expression will have a value of EMPTY_FIELD and
should be ignored.

Algorithm
=========

ClarityNLP uses a set of regular expressions to recognize date expressions.
The date_finder module scans a sentence with each date-finding regex and
keeps track of any matches. If any matches overlap, an overlap resolution
process is used to select a winniner. Each winning match is converted to a
``DateValue`` namedtuple. This object is defined at the top of the source code
module and can be imported by other Python code. Each namedtuple is appended
to a list as the sentence is scanned. After scanning completes, the list of
``DateValue`` namedtuples is converted to JSON and returned to the caller.

Date Expression Formats
-----------------------

Using notation similar to that used by the 
`PHP date reference <https://www.php.net/manual/en/datetime.formats.date.php>`_,
we define the following quantities:

=========  ===============================================================================
Shorthand  Meaning
=========  ===============================================================================
dd         one or two-digit day of the month with optional suffix (7th, 22nd, etc.)
DD         two-digit day of the month
m          textual name of the month
M          textual month abbreviation
mm         one or two-digit numerical month
MM         two-digit month
y          two or four-digit year
yy         two-digit year
YYYY       four-digit year
?          optional
=========  ===============================================================================

With these definitions, the date expression formats that ClarityNLP recognizes are
(using the date of the first Moon landing for illustration):

======================================  ======================================================
Date Expression Format                  Examples
======================================  ======================================================
YYYYMMDD                                19690720
[-+]?YYYY-MM-DD                         +1969-07-20
YYYY/MM/DD                              1969/07/20
YY-MM-DD                                69-07-20
YYYY-MM-DDTHH:MM:SS(.ffffff)?
(here MM:SS means minutes and seconds)
mm/dd/YYYY                              07/20/1969
YYYY/mm/dd                              1969/7/20, 1969/07/20
dd-mm-YYYY, dd.mm.YYYY                  20-07-1969, 20.7.1969
y-mm-dd                                 1969-7-20, 1969-07-20, 69-7-20
dd.mm.yy                                20.7.69, 20.07.69
dd-m-y, ddmy, dd m y                    20-JULY-69, 20JULY69, 20 July 1969
m-dd-y, m.dd.y, mddy, m dd, y           20-July 1969, 20JULY1969, 20 July, 1969
M-DD-y                                  Jul-20-1969, Jul-20-69
y-M-DD                                  69-Jul-20, 1969-Jul-20
mm/dd                                   7/20, 07/20
m-dd, m.dd, m dd                        July 20, July 20th, July-20
dd-m, dd.m, dd m                        20-July, 20.July, 20 July
YYYY-mm                                 1969-07, 1969-7
m-YYYY, m.YYYY, m YYYY                  July-1969, July.1969, July 1969
YYYY-m, YYYY.m, YYYY m                  1969-July, 1969.July, 1969 July
YYYY                                    1969
m                                       July
======================================  ======================================================

