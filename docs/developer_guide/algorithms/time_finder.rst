.. _timefinderalgo:

Finding Time Expressions
************************

Overview
========

ClarityNLP includes a module that locates time expressions in clinical text.
By 'time expression' we mean a string such as ``9:41 AM``, ``05:12:24.12345``,
or something similar. The ``TimeFinder`` module scans sentences for time
expressions, extracts them, and generates output in JSON format.

Source Code
===========

The source code for the time finder module is located in
``nlp/algorithms/finder/time_finder.py``.

Inputs
------

A single string, the sentence to be scanned for time expressions.

Outputs
-------

A JSON array containing these fields for each time expression found:

==================  ==============================================================
Field Name          Explanation
==================  ==============================================================
text                string, text of the complete time expression
start               integer, offset of the first character in the matching text
end                 integer, offset of the final character in the matching text plus 1
hours               integer hours
minutes             integer minutes
seconds             integer seconds
fractional_seconds  string, contains digits after decimal point, including any leading zeros
am_pm               string, either STR_AM or STR_PM (see values below)
timezone            string, timezone code
gmt_delta_sign      sign of the UTC offset, either '+' or '-'
gmt_delta_hours     integer, UTC hour offset
gmt_delta_minutes   integer, UTC minute offset
==================  ==============================================================

All JSON results contain an identical number of fields. Any fields that are
not valid for a given time expression will have a value of EMPTY_FIELD and
should be ignored.

Algorithm
=========

ClarityNLP uses a set of regular expressions to recognize time expressions.
The time_finder module scans a sentence with each time-finding regex and
keeps track of any matches. If any matches overlap, an overlap resolution
process is used to select a winniner. Each winning match is converted to a
``TimeValue`` namedtuple. This object is defined at the top of the source code
module and can be imported by other Python code. Each namedtuple is appended
to a list as the sentence is scanned. After scanning completes, the list of
``TimeValue`` namedtuples is converted to JSON and returned to the caller.

Time Expression Formats
-----------------------

Using notation similar to that used by the 
`PHP time reference <https://www.php.net/manual/en/datetime.formats.time.php>`_,
as well as the Wikipedia article on
`ISO 8601 formats <https://en.wikipedia.org/wiki/ISO_8601>`_, we define the
following quantities:

==========  =============================================================================================
Shorthand   Meaning
==========  =============================================================================================
h           hour digit, 0-9
h12         12 hr. clock, hours only,   0-9
h24         24 hr. clock, hours only, zero-padded, 00-24
m           minutes digit, 0-9
mm          minutes, zero-padded, 00-59
ss          seconds, zero-padded 00-60 (60 means leap second)
am_pm       am or pm designator, can be ``am`` or ``pm``, either lower or upper case, with each
            letter optionally followed by a ``.`` symbol
t           either ``t`` or ``T``
f           fractional seconds digit
?           optional
utc_time    ``hh``, ``hh:mm``, ``hhmm``, ``hh:mm:ss``, ``hhmmss``, ``hh:mm:ss.ffffff``, ``hhmmss.ffffff``
==========  =============================================================================================

With these definitions, the time expression formats that ClarityNLP recognizes are:

======================================  ======================================================
Time Expression Format                  Examples
======================================  ======================================================
utc-timeZ                               10:14:03Z
utc_time+-hh:mm                         10:14:03+01:30, 10:14:03-01:30
utc_time+-hhmm                          10:14:03+0130,  10:14:03-0130
utc_time+-hh                            10:14:03+01,    10:14:03-01
YYYY-MM-DDTHH:MM:SS(.ffffff)?           1969-07-20T10:14:03.123456
(here MM:SS means minutes and seconds)
h12 am_pm                               4 am, 5PM, 10a.m., 9 pm.
h12m am_pm                              5:09 am, 9:41 P.M., 10:02 AM.
h12ms am_pm                             06:10:37 am, 10:19:36P.M., 1:02:03AM
h12msf                                  7:11:39:012345 am, 11:41:22.22334 p.m.
h12m                                    4:08, 10:14, and 11:59
t?h24m                                  14:12, 01:27, 10:27, T23:43
t?h24ms                                 01:03:24, T14:15:16
t?h24msf                                04:08:37.81412, 19:20:21.532453, 08:11:40:123456
t?hhmm                                  0613, t0613
t?hhmmss                                232120, 120000
t?h24ms with timezone abbreviation      040837CEST, 112345 PST, T093000 Z
t?h24ms with GMT offset                 T192021-0700, 14:45:15+03:30
======================================  ======================================================

A list of world time zone abbreviations can be found
`here <https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations>`_. ClarityNLP supports
this list as well as ``Z``, meaning "Zulu" or UTC time.
