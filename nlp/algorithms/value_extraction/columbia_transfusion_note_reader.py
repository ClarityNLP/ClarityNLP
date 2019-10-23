#!/usr/bin/env python3
"""


OVERVIEW:


The code in this module parses and extracts vitals data from Columbia 
University Medical Center transfusion notes.


INPUT:


An ascii text file containing one or more transfusion notes.


OUTPUT:


The set of JSON fields in the output includes:

        transfusionStart        YYYY-MM-DD HH:MM:SS (ISO format)
        transfusionEnd          YYYY-MM-DD HH:MM:SS (ISO format)
        elapsedMinutes          integer
        reaction                yes or no
        bloodProductOrdered     character string

        vitals                     set of vitals records

            dateTime               YYYY-MM-DD HH:MM:SS (ISO format) at which
                                   these measurements were taken
            timeDeltaMinutes       elapsed time in minutes since transfusionStart
            dryWeightKg
            heightCm
            tempF                  
            tempC                  
            heartRate              units of beats/min
            respRateMachine        units of breaths/min
            respRatePatient        units of breaths/min
            nibpSystolic           
            nibpDiastolic          
            nibpMean               
            arterialSystolic
            arterialDiastolic
            arterialMean
            bloodGlucose           units of mg/dl
            cvp                    units mmHg
            spO2                   percentage
            oxygenFlow             units of Lpm
            endTidalCO2            units of mm Hg
            fiO2                   percentage

All JSON results will contain an identical number of fields, regardless of
whether or not all fields are actually valid. Fields that are not valid will
have a value of 'None' (the special Python built-in constant) and should be
ignored.

The field names listed above are available as strings in these lists:

        TRANSFUSION_NOTE_FIELDS
        VITALS_FIELDS

JSON results are written to stdout.


USAGE:


To process an input file and capture the JSON result:

        json_string = run(filepath)

To unpack the JSON result into a list of TransfusionNote namedtuples:

        json_data = json.loads(json_string)
        note_list = [TransfusionNote(**record) for record in json_data]

To log the valid fields in each note:

        for note in note_list:

            # for each field in the transfusion note
            for field in TRANSFUSION_NOTE_FIELDS:

                # get its value
                val = getattr(note, field)

                # if the field is valid
                if EMPTY_FIELD != val:
                    if 'vitals' != field:
                        log('{0}: {1}'.format(field, val))
                    else:
                        # extract vitals into a VitalsRecord namedtuple
                        v_record = VitalsRecord(**val)
                        for v_field in VITALS_FIELDS:
                            v_val = getattr(v_record, v_field)
                            if EMPTY_FIELD != v_val:
                                log('{0}: {1}'.format(v_field, v_val))

Each group of vitals for a given transfusion is returned as a separate
JSON record. All vitals records for a given transfusion share the fields
in the TRANSFUSION_NOTE_FIELDS list below.

A working example of this code can be found below at the end of this module.

Command-line help can be obtained by running this code with the -h option.

"""

import os
import re
import sys
import json
import errno
import optparse
from datetime import datetime, timedelta
from collections import namedtuple
from claritynlp_logging import log, ERROR, DEBUG

VERSION_MAJOR = 0
VERSION_MINOR = 4

# The output of this module is a JSON string containing a list of
# TransfusionNote namedtuples.  The 'vitals' field of each note is a
# list of VitalsRecord namedtuples.

EMPTY_FIELD = None
TRANSFUSION_NOTE_FIELDS = ['transfusionStart', 'transfusionEnd',
                           'elapsedMinutes', 'reaction',
                           'bloodProductOrdered', 'vitals']
TransfusionNote = namedtuple('TransfusionNote', TRANSFUSION_NOTE_FIELDS)

VITALS_FIELDS = ['dateTime', 'timeDeltaMinutes', 'dryWeightKg', 'heightCm',
                 'tempF', 'tempC', 'heartRate', 'respRateMachine',
                 'respRatePatient', 'nibpSystolic', 'nibpDiastolic',
                 'nibpMean', 'arterialSystolic', 'arterialDiastolic',
                 'arterialMean', 'bloodGlucose', 'cvp', 'spO2',
                 'oxygenFlow', 'endTidalCO2', 'fiO2']
VitalsRecord = namedtuple('VitalsRecord', VITALS_FIELDS)


# date-time
str_date_time = r'\b(?P<day>\d\d?)-(?P<month>[a-z]+)-(?P<year>\d\d\d\d)\s+'  +\
                r'(?P<hours>\d\d?):(?P<minutes>\d\d?)'
regex_date_time = re.compile(str_date_time, re.IGNORECASE)

# list of date-times
str_dt = r'\d\d?-[a-z]+-\d\d\d\d\s+\d\d?:\d\d?'
str_date_time_list = r'(' + str_dt + r'\s*)*' + str_dt

# list of numbers, either float or integer
str_num = r'\d+(\.\d+)?'
str_num_list = r'(' + str_num + r'\s*)*' + str_num
regex_num_list = re.compile(str_num_list)

# start of each note
str_note_start = r'\bTransfusion\s+Note:'
regex_note_start = re.compile(str_note_start, re.IGNORECASE)

# transfusion start date
str_start_date = r'\bTransfusion\s+Start\s+Date/Time:\s*'  +\
                 r'(?P<date_time>' + str_date_time + r')'
regex_start_date = re.compile(str_start_date, re.IGNORECASE)

# transfusion end date
str_end_date = r'\bTransfusion\s+End\s+Date/Time:\s*'  +\
                 r'(?P<date_time>' + str_date_time + r')'
regex_end_date = re.compile(str_end_date, re.IGNORECASE)

# transfusion reaction
str_reaction = r'\bTransfusion\s+Reaction\s+[^:]+:\s*' +\
               r'(?P<yes_no>(Yes|No))'
regex_reaction = re.compile(str_reaction, re.IGNORECASE)

# blood product ordered
str_blood_product = r'\bBlood\s+Product\s+Ordered:\s*' +\
                    r'(?P<blood_product>[^\n]+)\n'
regex_blood_product = re.compile(str_blood_product, re.IGNORECASE)

# start of vital signs flowsheet
str_vitals_flowsheet_start = r'\d+\)\s+Vital\s+Signs\s+Flowsheet'
regex_vitals_flowsheet_start = re.compile(str_vitals_flowsheet_start,
                                          re.IGNORECASE)

# vitals date/time line
str_vitals_date_time = r'\bDate/Time\s+' +\
                       r'(?P<date_time_list>' + str_date_time_list + r')'
regex_vitals_date_time = re.compile(str_vitals_date_time, re.IGNORECASE)

# vitals temp (F) line
str_vitals_temp_f = r'\bTemperature\s+\(F\)\s+degrees\s+F\s+' +\
                    r'(?P<list>' + str_num_list + r')'
regex_vitals_temp_f = re.compile(str_vitals_temp_f, re.IGNORECASE)

# vitals temp (C) line
str_vitals_temp_c = r'\bTemperature\s+\(C\)\s+degrees\s+C\s+' +\
                    r'(?P<list>' + str_num_list + r')'
regex_vitals_temp_c = re.compile(str_vitals_temp_c, re.IGNORECASE)

# vitals heart rate line
str_vitals_hr = r'\bHeart\s+Rate\b[^\d]+' +\
                r'(?P<list>' + str_num_list + r')'
regex_vitals_hr = re.compile(str_vitals_hr, re.IGNORECASE)

# vitals machine resp rate line
str_vitals_rr_machine = r'\bMachine\s+\(bpm\)\s+' +\
                        r'(?P<list>' + str_num_list + r')'
regex_vitals_rr_machine = re.compile(str_vitals_rr_machine, re.IGNORECASE)

# vitals patient resp rate line
str_vitals_rr_patient = r'\bPatient\s+\(bpm\)\s+' +\
                r'(?P<list>' + str_num_list + r')'
regex_vitals_rr_patient = re.compile(str_vitals_rr_patient, re.IGNORECASE)

# vitals non-invasive blood pressure, systolic
str_vitals_nibp_systolic = r'\bNIBP\s+Systolic\s+' +\
                           r'(?P<list>' + str_num_list + r')'
regex_vitals_nibp_systolic = re.compile(str_vitals_nibp_systolic, re.IGNORECASE)

# vitals non-invasive blood pressure, diastolic
str_vitals_nibp_diastolic = r'\bNIBP\s+Diastolic\s+' +\
                            r'(?P<list>' + str_num_list + r')'
regex_vitals_nibp_diastolic = re.compile(str_vitals_nibp_diastolic, re.IGNORECASE)

# vitals non-invasive blood pressure, mean
str_vitals_nibp_mean = r'\bNIBP\s+Mean\s+' +\
                       r'(?P<list>' + str_num_list + r')'
regex_vitals_nibp_mean = re.compile(str_vitals_nibp_mean, re.IGNORECASE)

# vitals arterial blood pressure, systolic
str_vitals_arterial_systolic = r'\bArterial\s+Systolic\s+' +\
                               r'(?P<list>' + str_num_list + r')'
regex_vitals_arterial_systolic = re.compile(str_vitals_arterial_systolic, re.IGNORECASE)

# vitals arterial blood pressure, diastolic
str_vitals_arterial_diastolic = r'\bArterial\s+Diastolic\s+' +\
                                r'(?P<list>' + str_num_list + r')'
regex_vitals_arterial_diastolic = re.compile(str_vitals_arterial_diastolic, re.IGNORECASE)

# vitals arterial blood pressure, mean
str_vitals_arterial_mean = r'\bArterial\s+Mean\s+' +\
                           r'(?P<list>' + str_num_list + r')'
regex_vitals_arterial_mean = re.compile(str_vitals_arterial_mean, re.IGNORECASE)

# blood glucose monitor
str_vitals_glucose = r'\bBlood\s+Glucose\s+Monitor\s+mg/dl\s+' +\
                     r'(?P<list>' + str_num_list + r')'
regex_vitals_glucose = re.compile(str_vitals_glucose, re.IGNORECASE)

# CVP
str_vitals_cvp = r'\bCVP\s+mmHg\s+' + r'(?P<list>' + str_num_list + r')'
regex_vitals_cvp = re.compile(str_vitals_cvp, re.IGNORECASE)

# SpO2
str_vitals_spo2 = r'\bSpO2\s+[^%]+%\)?\s+' +\
                  r'(?P<list>' + str_num_list + r')'
regex_vitals_spo2 = re.compile(str_vitals_spo2, re.IGNORECASE)

# oxygen flow
str_vitals_oxygen_flow = r'\bOxygen\s+Flow\b[^)]+\)\s+' +\
                         r'(?P<list>' + str_num_list + r')'
regex_vitals_oxygen_flow = re.compile(str_vitals_oxygen_flow, re.IGNORECASE)

# end tidal CO2 mm Hg
str_vitals_end_tidal_co2 = r'\s\(ETCO2\)\s+mm\s+Hg\s+' +\
                           r'(?P<list>' + str_num_list + r')'
regex_vitals_end_tidal_co2 = re.compile(str_vitals_end_tidal_co2, re.IGNORECASE)

# FiO2 %
str_vitals_fio2 = r'\bFiO2\s+\(%\)\s+' +\
                  r'(?P<list>' + str_num_list + r')'
regex_vitals_fio2 = re.compile(str_vitals_fio2, re.IGNORECASE)

# dry weight
str_vitals_dry_weight = r'\bDry\s+Weight\s+\(kg\)\s+' +\
                        r'(?P<list>' + str_num_list + r')'
regex_vitals_dry_weight = re.compile(str_vitals_dry_weight, re.IGNORECASE)

# height
str_vitals_height = r'\bHeight\s+\(cm\)\s+' +\
                    r'(?P<list>' + str_num_list + r')'
regex_vitals_height = re.compile(str_vitals_height, re.IGNORECASE)

# NOTE: changes to these strings will affect processing below!

regexes = {
    regex_start_date:'transfusionStart',
    regex_vitals_flowsheet_start:'vitalsFlowsheetStart',
    regex_end_date:'transfusionEnd',
    regex_reaction:'reaction',
    regex_blood_product:'bloodProductOrdered',
}

vitals_regexes = {
    regex_vitals_date_time:'dateTime',
    regex_vitals_dry_weight:'dryWeightKg',
    regex_vitals_height:'heightCm',
    regex_vitals_temp_f:'tempF',
    regex_vitals_temp_c:'tempC',
    regex_vitals_hr:'heartRate',
    regex_vitals_rr_machine:'respRateMachine',
    regex_vitals_rr_patient:'respRatePatient',
    regex_vitals_nibp_systolic:'nibpSystolic',
    regex_vitals_nibp_diastolic:'nibpDiastolic',
    regex_vitals_nibp_mean:'nibpMean',
    regex_vitals_arterial_systolic:'arterialSystolic',
    regex_vitals_arterial_diastolic:'arterialDiastolic',
    regex_vitals_arterial_mean:'arterialMean',
    regex_vitals_glucose:'bloodGlucose',
    regex_vitals_cvp:'cvp',
    regex_vitals_spo2:'spO2',
    regex_vitals_oxygen_flow:'oxygenFlow',
    regex_vitals_end_tidal_co2:'endTidalCO2',
    regex_vitals_fio2:'fiO2',
}

month_dict = {
    'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6,
    'jul':7, 'aug':8, 'sep':9, 'sept':9, 'oct':10, 'nov':11, 'dec':12
}

TRANSFUSION_TIME_FIELDS = ['transfusionStartDay', 'transfusionStartMonth',
                           'transfusionStartYear','transfusionStartHours',
                           'transfusionStartMinutes', 'transfusionEndDay',
                           'transfusionEndMonth', 'transfusionEndYear',
                           'transfusionEndHours', 'transfusionEndMinutes']

MODULE_NAME = 'columbia_transfusion_note_reader.py'

EMPTY_JSON = '{}'

# number of space characters between adjacent measurements on the same line
COL_SPACING = 8

###############################################################################
def to_datetime(year, month, day, hours, minutes):
    """
    Convert time components to a python datetime object.
    """

    if EMPTY_FIELD != year and EMPTY_FIELD != month and EMPTY_FIELD != day \
       and EMPTY_FIELD != hours and EMPTY_FIELD != minutes:

        return datetime(year, month, day, hours, minutes)
    else:
        return EMPTY_FIELD

###############################################################################
def to_iso(datetime_val):
    """
    Convert a datetime value to YYYY-MM-DD HH:MM:SS format.
    """

    return datetime_val.isoformat(sep=' ')

###############################################################################
def elapsed_min(t_start, t_end):
    """
    Return the elapsed time for the transfusion, in minutes.
    """

    if EMPTY_FIELD == t_start or EMPTY_FIELD == t_end:
        return EMPTY_FIELD
    
    # subtract to get a timedelta obj representing the elapsed time
    t_elapsed = t_end - t_start

    # convert to elapsed time to minutes
    return int( t_elapsed.total_seconds() / 60)
    
###############################################################################
def to_json(transfusion_note_list):
    """
    Serialize the transfusion notes to JSON. Make each different vitals
    measurement for a given note an independent JSON object.
    """

    dict_list = []
    for note in transfusion_note_list:
        
        note_dict = {}

        for f in TRANSFUSION_NOTE_FIELDS:
            if f in note:
                note_dict[f] = note[f]
            else:
                note_dict[f] = EMPTY_FIELD

        # get the transfusion start and end times as datetime objects
        t_start = to_datetime(note['transfusionStartYear'],
                              note['transfusionStartMonth'],
                              note['transfusionStartDay'],
                              note['transfusionStartHours'],
                              note['transfusionStartMinutes'])

        t_end = to_datetime(note['transfusionEndYear'],
                            note['transfusionEndMonth'],
                            note['transfusionEndDay'],
                            note['transfusionEndHours'],
                            note['transfusionEndMinutes'])

        # write to JSON output in ISO format
        note_dict['transfusionStart'] = to_iso(t_start)
        note_dict['transfusionEnd']   = to_iso(t_end)
        
        # compute transaction elapsed time in minutes
        note_dict['elapsedMinutes'] = elapsed_min(t_start, t_end)
                
        # convert vitals from struct of arrays to array of structs

        flowsheet_count = len(note['vitalsFlowsheets'])
        for flowsheet in note['vitalsFlowsheets']:
            
            # first find max len of all the vitals arrays for this flowsheet
            max_len = 0
            for array_name in vitals_regexes.values():
                if array_name in flowsheet:
                    array = flowsheet[array_name]
                    if len(array) > max_len:
                        max_len = len(array)

            # now extract values at identical indices across all arrays
            for i in range(max_len):
                vitals_dict = {}
                for array_name in vitals_regexes.values():
                    
                    vitals_dict[array_name] = EMPTY_FIELD
                    
                    # set values for this particular set of measurements
                    if array_name in flowsheet:
                        array = flowsheet[array_name]
                        if i < len(array):
                            vitals_dict[array_name] = array[i]
                        else:
                            # sometimes values are missing
                            vitals_dict[array_name] = EMPTY_FIELD

                # compute time delta from transfusion start for these vitals
                if EMPTY_FIELD != vitals_dict['dateTime']:
                    t_end = to_datetime(vitals_dict['dateTime']['year'],
                                        vitals_dict['dateTime']['month'],
                                        vitals_dict['dateTime']['day'],
                                        vitals_dict['dateTime']['hours'],
                                        vitals_dict['dateTime']['minutes'])

                    vitals_dict['timeDeltaMinutes'] = elapsed_min(t_start, t_end)
                    vitals_dict['dateTime'] = to_iso(t_end)
                else:
                    vitals_dict['timeDeltaMinutes'] = EMPTY_FIELD
                    vitals_dict['dateTime'] = EMPTY_FIELD
                            
                # append these vitals as a new measurement set
                result_dict = {}
                for f in TRANSFUSION_NOTE_FIELDS:
                    if 'vitals' == f:
                        result_dict[f] = vitals_dict
                    else:
                        result_dict[f] = note_dict[f]
                dict_list.append(result_dict)
        
    return json.dumps(dict_list, indent=4)


###############################################################################
def extract_date_time(matchobj, regex_name, transfusion_note):
    """
    Extract all components of a date/time string and convert to intgers.
    """

    found_date_time = False

    try:
        if matchobj.group('date_time') is not None:
            text_dt = matchobj.group('date_time')
            match_dt = regex_date_time.match(text_dt)
            assert match_dt
            
            day     = match_dt.group('day')
            month   = match_dt.group('month')
            year    = match_dt.group('year')
            hours   = match_dt.group('hours')
            minutes = match_dt.group('minutes')
            
            transfusion_note[regex_name + 'Day']   = int(day)
            transfusion_note[regex_name + 'Month'] = month_dict[month.lower()]
            transfusion_note[regex_name + 'Year']  = int(year)
            transfusion_note[regex_name + 'Hours'] = int(hours)
            transfusion_note[regex_name + 'Minutes'] = int(minutes)
            found_date_time = True
    except IndexError:
        pass

    #log('found date time: {0}'.format(found_date_time))
    return found_date_time               

###############################################################################
def extract_date_time_list(matchobj, regex_name, item_list):
    """
    Extract each date/time in a date/time list.
    """

    found_date_time_list = False

    try:
        if matchobj.group('date_time_list') is not None:
            text_dt_list = matchobj.group('date_time_list')
            found_date_time_list = True

            count = 0
            iterator = regex_date_time.finditer(text_dt_list)
            for match_dt in iterator:
                item_dict = {}
                day     = match_dt.group('day')
                month   = match_dt.group('month')
                year    = match_dt.group('year')
                hours   = match_dt.group('hours')
                minutes = match_dt.group('minutes')

                item_dict['day']   = int(day)
                item_dict['month'] = month_dict[month.lower()]
                item_dict['year']  = int(year)
                item_dict['hours'] = int(hours)
                item_dict['minutes'] = int(minutes)
                item_list.append(item_dict)
    except IndexError:
        pass

    return found_date_time_list


###############################################################################
def extract_vitals(vitals_text, list_text, num_readings):
    """
    Extract numeric values from a line of vitals data. Whitespace is 
    significant. Numeric values have 'COL_SPACING' space characters from
    one column to the next. Whitespace gaps between numeric values must be
    a multiple of COL_SPACING.
    """

    CHAR_SPACE = ' '
    results = [EMPTY_FIELD] * num_readings

    # extract list of numeric values
    source_index = 0
    numeric_values = [float(v.strip()) for v in list_text.split()]

    # find the position of the first measurement
    end = vitals_text.find(list_text)

    # scan backwards to find the first non-space character
    start = None
    for i in range(end-1, 0, -1):
        if CHAR_SPACE != vitals_text[i]:
            start = i+1
            break

    assert start is not None

    # the difference must be a multiple of the column spacing
    assert 0 == (end - start) % COL_SPACING
    meas_index = (end - start) // COL_SPACING
    # use 0-based indexing
    results[meas_index - 1] = numeric_values[source_index]
    source_index += 1

    # scan the string, count spaces between numbers, and assign the
    # remaining values to their proper offset in the results array

    i = end+1
    counting_spaces = False
    while i < len(vitals_text):
        if CHAR_SPACE != vitals_text[i]:
            if counting_spaces:
                # found the first char of the next measurement
                counting_spaces = False
                end = i
                assert 0 == (end - start) % COL_SPACING
                # delta == no. of cols between current and prev values
                delta = (end - start) // COL_SPACING
                results[meas_index - 1 + delta] = numeric_values[source_index]
                source_index += 1
                meas_index += delta
        else:
            if not counting_spaces:
                # found the first space char of a new whitespace gap
                counting_spaces = True
                start = i
        i += 1

    return results
    

###############################################################################
def process_note(note_text, results):
    """
    Extract vitals data from a single transfusion note.
    """

    transfusion_note = {}

    flowsheets = []
    num_readings = None
    for regex, regex_name in regexes.items():
        match = regex.search(note_text)
        if match:
            # extract any date/time components
            if extract_date_time(match, regex_name, transfusion_note):
                continue
            elif 'reaction' == regex_name:
                transfusion_note[regex_name] = match.group('yes_no').lower()
            elif 'bloodProductOrdered' == regex_name:
                transfusion_note[regex_name] = match.group('blood_product').lower().strip()
            elif 'vitalsFlowsheetStart' == regex_name:
                start = match.end()
                vitals_text = note_text[start:]
                vitals_dict = {}
                for vr, vr_name in vitals_regexes.items():
                    match_vr = vr.search(vitals_text)
                    if match_vr:
                        date_time_list = []
                        if extract_date_time_list(match_vr, vr_name, date_time_list):
                            vitals_dict[vr_name] = date_time_list
                            num_readings = len(date_time_list)
                            continue
                        else:
                            # found numeric list
                            assert num_readings is not None
                            list_text = match_vr.group('list')
                            if list_text is not None:
                                # get numeric values
                                values = extract_vitals(match_vr.group(),
                                                        list_text,
                                                        num_readings)
                                vitals_dict[vr_name] = values

                flowsheets.append(vitals_dict)

    transfusion_note['vitalsFlowsheets'] = flowsheets
    results.append(transfusion_note)

###############################################################################
def run(filepath):
    """
    Perform the main work of this module.
    """

    if not filepath:
        raise ValueError('input file not specified')
    
    # make sure the input file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)

    # load the file contents into a string

    try:
        infile = open(filepath, 'r')
    except (OSError, IOError) as e:
        return EMPTY_JSON
    except Exception as e:
        return EMPTY_JSON

    with infile:
        try:
            text = infile.read()
        except UnicodeDecodeError as e:
            return EMPTY_JSON
        except (OSError, IOError) as e:
            return EMPTY_JSON
        except Exception as e:
            return EMPTY_JSON

    if 0 == len(text):
        return EMPTY_JSON
        
    return run_on_text(text)


def run_on_text(text):
    results = []
    boundaries = []

    # scan the data and process the notes one by one
    iterator = regex_note_start.finditer(text)
    for match in iterator:
        boundaries.append(match.start())
        if len(boundaries) > 1:
            note_text = text[boundaries[-2]:boundaries[-1]]
            process_note(note_text, results)

    # final note, extends to end of the text string
    if len(boundaries) > 0:
        note_text = text[boundaries[-1]:]
        process_note(note_text, results)

    return to_json(results)
    
###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(MODULE_NAME, VERSION_MAJOR, VERSION_MINOR)
        
###############################################################################
def show_help():
    log(get_version())
    log("""
    USAGE: python3 ./{0} -f <filename>  [-hv]

    OPTIONS:

        -f, --file <quoted string>  Path to file containing transfusion notes.

    FLAGS:

        -h, --help           log this information and exit.
        -v, --version        log version information and exit.

    """.format(MODULE_NAME))
                    
###############################################################################
if __name__ == '__main__':

    optparser = optparse.OptionParser(add_help_option=False)
    optparser.add_option('-f', '--file', action='store',
                         dest='filepath')
    optparser.add_option('-v', '--version',  action='store_true',
                         dest='get_version')
    optparser.add_option('-h', '--help',     action='store_true',
                         dest='show_help', default=False)

    opts, other = optparser.parse_args(sys.argv)

    # show help if no command line arguments
    if opts.show_help or 1 == len(sys.argv):
        show_help()
        sys.exit(0)

    if opts.get_version:
        log(get_version())
        sys.exit(0)

    # process the file
    json_string = run(opts.filepath)

    # log formatted output
    
    # parse the JSON result
    json_data = json.loads(json_string)

    # unpack to a list of TransfusionNote namedtuples
    note_list = [TransfusionNote(**record) for record in json_data]

    # find the max length of all the transfusion note field names
    maxlen_t = len(max(TRANSFUSION_NOTE_FIELDS, key=len))

    # find the max length of all the vitals field names
    maxlen_v = len(max(VITALS_FIELDS, key=len))

    maxlen = max(maxlen_t, maxlen_v)
    
    # log all valid fields in each note
    for note in note_list:
        for field in TRANSFUSION_NOTE_FIELDS:
            val = getattr(note, field)
            if EMPTY_FIELD != val:
                if 'vitals' != field:
                    indent = ' '*(maxlen - len(field))
                    log('{0}{1}: {2}'.format(indent, field, val))
                else:
                    # extract vitals into a VitalsRecord namedtuple
                    v_record = VitalsRecord(**val)
                    for v_field in VITALS_FIELDS:
                        v_val = getattr(v_record, v_field)
                        if EMPTY_FIELD != v_val:
                            indent = ' '*(maxlen - len(v_field))
                            log('{0}{1}: {2}'.format(indent, v_field, v_val))
        log()
