#!/usr/bin/env python3
"""
    sec_tag_db_extract.py

    Extract section tags and related data from the SecTag_Terminology MySQL database.

        Usage: python3 sec_tag_db_extract.py

    To create the SecTag_Terminology database, download the sec_tag.zip file from
    Josh Denny's site at Vanderbilt:

        https://www.vumc.org/cpm/sectag-tagging-clinical-note-section-headers

    Unzip and find the SecTag_Terminology.sql file.

    Use the following commands to create a new SecTag_Terminology database:

        mysql -p -u root
        <enter MySQL root password>

        CREATE USER 'sectag'@'localhost' IDENTIFIED BY 'sectag';
        CREATE DATABASE SecTag_Terminology;
        GRANT ALL ON SecTag_Terminology.* TO 'sectag'@'localhost';
        GRANT FILE ON *.* TO 'sectag'@'localhost';

    If you change either the user name or password, make identical changes in the 
    pymysql.connect command at the bottom of this file.

    After running these commands, log out as the MySQL root user and populate 
    the database as the sectag user:

        mysql -p -u sectag SecTag_Terminology < SecTag_Terminology.sql

"""

import os
import sys
import pymysql
import pymysql.cursors

# add current dir to PYTHONPATH to import: export PYTHONPATH=.:$PYTHONPATH
from concept_graph import DuplicateNodeException
from concept_graph import NodeNotFoundException
from concept_graph import ConceptGraph
from concept_graph import Node
from claritynlp_logging import log, ERROR, DEBUG

# name of file mapping concept names to synonyms
CS_FILENAME = os.path.join(os.getcwd(), 'data', 'concepts_and_synonyms.txt')

# name of the file containing the concept graph
GRAPH_FILENAME = os.path.join(os.getcwd(), 'data', 'graph.txt')

# ancestor and descendant node files
ANCESTOR_FILENAME   = os.path.join(os.getcwd(), 'data', 'ancestors.txt')
DESCENDANT_FILENAME = os.path.join(os.getcwd(), 'data', 'descendants.txt')

# ids of some problem concepts
CID_PRINCIPAL_DIAGNOSIS    = 127
CID_SLEEP_HABITS           = 308
CID_LEVEL_OF_CONSCIOUSNESS = 695
CID_APPEARANCE             = 745

###############################################################################
def extract_synonyms(conn):

    cursor = conn.cursor()
    
    # get concepts and associated synonyms
    query = \
    "SELECT c.cid, c.kmname as 'Concept Name', l.sid, s.str AS 'Synonym', s.str_type AS 'Synonym Type' \
    FROM (sidcidnew_lnk AS l LEFT JOIN strings_tbl AS s ON l.sid = s.sid) \
    INNER JOIN concepts_tbl AS c ON l.cid = c.cid \
    WHERE c.concepttype = 'ATOMIC' \
    ORDER BY c.cid ASC, s.sid ASC;"
    
    try:
        cursor.execute(query)
    except Exception as ex:
        log("extract_synonyms: could not execute query...", ERROR)
        log(ex, ERROR)
        cursor.close()
        conn.close()
        sys.exit(-1)
        
    results = []
        
    while True:
        row = cursor.fetchone()
        if not row:
            break
        
        # concept_id, concept_name, synonym_id, synonym_name, synonym_type
        result = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(row[0], row[1], row[2], row[3], row[4])

        # correct spelling errors for some concepts:

        cid = int(row[0])
        if CID_PRINCIPAL_DIAGNOSIS == cid:
            # change 'principle_diagnosis' to 'principal_diagnosis'
            result = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(row[0], 'principal_diagnosis', row[2], row[3], row[4])
        elif CID_SLEEP_HABITS == cid:
            # Correct an error for concept 308, which has "sleep_habits,_sleep"
            # as the concept name (kmname database column). Use "sleep_habits"
            # as the concept name.
            result = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(row[0], 'sleep_habits', row[2], row[3], row[4])
        elif CID_LEVEL_OF_CONSCIOUSNESS == cid:
            # change 'cousciousness' to 'consciousness' in all synonyms
            new_row3 = row[3].replace('cousciousness', 'consciousness')
            result = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(row[0], 'level_of_consciousness', row[2], new_row3, row[4])
        elif CID_APPEARANCE == cid:
            # The 'appearance' concept has an invalid treecode and is the only concept at level 10.
            # It has two synonyms: 'appearance' (PT) and 'appearance' (KM). Remove these synonyms.
            # With these removed, the synonym 'general appearance' is associated with the concepts
            # 'general_review' and 'general_exam'. The synonym 'appearance' is associated with
            # concept 'general_exam'.
            continue

        results.append(result)
            
    log("extract_synonyms: query returned {0} rows.".format(cursor.rowcount))

    # write to output file
    outfile = open(CS_FILENAME, 'wt')
    outfile.write("cid,concept_name,synonym_id,synonym_name,synonym_type\n")
    for r in results:
        outfile.write(r)

    # additions - start synonym ids at 6000, greater than any existing synonym id

    # map 'discharge exam' to 'discharge_condition'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(125, 'discharge_condition', 6000, 'discharge exam', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(125, 'discharge_condition', 6001, 'discharge_exam', 'KM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(125, 'discharge_condition', 6002, 'exam discharge', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(125, 'discharge_condition', 6003, 'exam_discharge', 'KM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(125, 'discharge_condition', 6004, 'on discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(125, 'discharge_condition', 6005, 'at discharge', 'PT'))

    # map 'discharge VS' to 'vital_signs'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(547, 'vital_signs', 6010, 'discharge vital signs', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(547, 'vital_signs', 6011, 'discharge_vital_signs', 'KM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(547, 'vital_signs', 6012, 'discharge VS', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(547, 'vital_signs', 6013, 'discharge vs', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(547, 'vital_signs', 6014, 'discharge vitals', 'NORM'))
    
    # add synonyms for 'labs discharge'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6020, 'discharge labs', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6021, 'discharge lab', 'NORM'))

    # add synonyms for 'labs studies pending at time of discharge'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6040,
                                                     'labs studies pending at time of discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6041,
                                                     'studies pending at time of discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6042,
                                                     'lab study pending time discharge', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6043,
                                                     'pending at time of discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6044,
                                                     'pending time discharge', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6045,
                                                     'labs on day of discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6046,
                                                     'lab day discharge', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6047,
                                                     'lab discharge', 'NORM'))

    # add synonyms for 'issues requiring follow-up'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(967, 'discharge_followup', 6050,
                                                     'issues requiring follow-up', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(967, 'discharge_followup', 6051,
                                                     'issues requiring follow_up', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(967, 'discharge_followup', 6052,
                                                     'issues requiring follow up', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(967, 'discharge_followup', 6053,
                                                     'issues requiring followup', 'PT'))


    # add synonyms for 'discharge instructions'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(963, 'discharge_instructions', 6060,
                                                     'instructions on discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(963, 'discharge_instructions', 6061,
                                                     'instruction discharge', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(963, 'discharge_instructions', 6062,
                                                     'discharge instructions followup', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(963, 'discharge_instructions', 6063,
                                                     'discharge instruction followup', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(963, 'discharge_instructions', 6064,
                                                     'discharge instructions follow up', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(963, 'discharge_instructions', 6065,
                                                     'discharge instruction follow up', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(963, 'discharge_instructions', 6066,
                                                     'discharge instructions follow-up', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(963, 'discharge_instructions', 6067,
                                                     'discharge instruction follow-up', 'NORM'))
    
    
    # add synonyms for 'discharge_medications'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(438, 'discharge_medications', 6070,
                                                     'medications on discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(438, 'discharge_medications', 6071,
                                                     'medication discharge', 'NORM'))

    # add synonyms for 'discharge_diagnosis'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(133, 'discharge_diagnosis', 6080,
                                                     'diagnoses on discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(133, 'discharge_diagnosis', 6081,
                                                     'diagnosis on discharge', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(133, 'discharge_diagnosis', 6082,
                                                     'diagnoses discharge', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(133, 'discharge_diagnosis', 6083,
                                                     'diagnosis discharge', 'NORM_COMP'))

    # add synonyms for 'report approved date'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(107, 'report_date', 6090,
                                                     'report approved date', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(107, 'report_date', 6091,
                                                     'date report approved', 'PT'))
    
    # add synonyms for 'laboratory_data' (admission labs)
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6100,
                                                     'admission labs', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6101,
                                                     'admission lab', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6102,
                                                     'laboratories and studies', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(790, 'laboratory_data', 6103,
                                                     'lab and studies', 'PT'))
    
    # add synonyms for 'chest_xray'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6110,
                                                     'pa and lateral radiographs of the chest', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6111,
                                                     'pa lateral radiograph chest', 'NORM_COMP'))

    # add synonyms for 'thoracic_angiography' (CTA = computed tomography angiography)
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(881, 'thoracic_angiography', 6120,
                                                     'cta of the chest', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(881, 'thoracic_angiography', 6121,
                                                     'cta chest', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(881, 'thoracic_angiography', 6121,
                                                     'chest cta', 'NORM_COMP'))

    # add synonyms for 'nasal cavity'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(464, 'nose_review', 6130,
                                                     'nasal cavity', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(464, 'nose_review', 6131,
                                                     'nasal_cavity', 'PT'))
    
    # synonyms for 'history_present_illness'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(158, 'history_present_illness', 6150,
                                                     'history of presenting illness', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(158, 'history_present_illness', 6151,
                                                     'history presenting illness', 'NORM'))
    

    # synonyms for 'surgical_procedures'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(149, 'surgical_procedures', 6160,
                                                     'major surgical or invasive procedure', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(149, 'surgical_procedures', 6161,
                                                     'major surgical invasive procedure', 'NORM_COMP'))

    # synonyms for 'laboratory_and_radiology_data'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(788, 'laboratory_and_radiology_data', 6170,
                                                     'pertinent results', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(788, 'laboratory_and_radiology_data', 6171,
                                                     'pertinent result', 'NORM'))

    # synonyms for 'chest_xray'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6180, 'chest x-ray', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6181, 'x-ray chest', 'PT'))
    
    # synonyms for 'echocardiogram'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(819, 'echocardiogram', 6190, 'doppler', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(819, 'echocardiogram', 6191, 'tte', 'PT'))

    # synonyms for 'type_of_procedure'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(1075, 'type_of_procedure', 6200, 'test type', 'PT'))
        
    # synonyms for 'icd_code'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(62, 'icd_code', 6210, 'icd-9 codes', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(62, 'icd_code', 6211, 'icd-9 code', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(62, 'icd_code', 6212, 'icd-10 codes', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(62, 'icd_code', 6213, 'icd-10 code', 'NORM'))

    # synonyms for 'physician'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(20, 'physician', 6220, 'interpret md', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(20, 'physician', 6221, 'interpreting md', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(20, 'physician', 6222, 'interpreting physician', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(20, 'physician', 6222, 'interpret physician', 'PT'))
    
    # synonyms for tomography
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5000, 'computed_tomography', 6398, 'ct scan', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5000, 'computed_tomography', 6399, 'ct', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5001, 'cerebral_ct', 6400, 'head ct', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5001, 'cerebral_ct', 6401, 'ct head', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5001, 'cerebral_ct', 6402, 'ct of the head', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5002, 'thoracic_ct', 6403, 'chest ct', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5002, 'thoracic_ct', 6404, 'ct chest', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5002, 'thoracic_ct', 6405, 'ct of the chest', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5002, 'thoracic_ct', 6406, 'torso ct', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5002, 'thoracic_ct', 6407, 'ct torso', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5002, 'thoracic_ct', 6408, 'ct of the torso', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6409, 'abdominal ct', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6410, 'ct abdominal', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6411, 'ct abdomen', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6412, 'ct of the abdomen', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6413, 'ct abd', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6414, 'abd ct', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6415, 'ct of the pelvis', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6416, 'ct pelvis', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6417, 'pelvis ct', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6419, 'ct abd pelvis', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6420, 'ct pelvis abd', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6421, 'abd pelvis ct', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5003, 'abdominal_ct', 6422, 'pelvis abd ct', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5004, 'renal_and_adrenal_ct', 6430,
                                                     'renal and adrenal ct', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5004, 'renal_and_adrenal_ct', 6431,
                                                     'adrenal and renal ct', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5004, 'renal_and_adrenal_ct', 6432,
                                                     'renal adrenal ct', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5004, 'renal_and_adrenal_ct', 6433,
                                                     'adrenal renal ct', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5005, 'extremities_ct', 6440,
                                                     'extremities ct', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5005, 'extremities_ct', 6441,
                                                     'ct extremities', 'NORM'))

    # synonyms for CTA
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(880, 'cerebral_angiography', 6500, 'cta of the head', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(880, 'cerebral_angiography', 6500, 'cta head', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(880, 'cerebral_angiography', 6501, 'head cta', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(880, 'cerebral_angiography', 6503, 'cta of the neck', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(880, 'cerebral_angiography', 6504, 'cta neck', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(880, 'cerebral_angiography', 6505, 'neck cta', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(881, 'thoracic_angiography', 6510, 'cta of the torso', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(881, 'thoracic_angiography', 6511, 'cta torso', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(881, 'thoracic_angiography', 6512, 'torso cta', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6520,
                                                     'cta of the abdomen', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6521,
                                                     'cta abdomen', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6522,
                                                     'cta abd', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6523,
                                                     'abd cta', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6524,
                                                     'cta of the pelvis', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6525,
                                                     'cta pelvis', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6526,
                                                     'pelvis cta', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6527,
                                                     'cta abd pelvis', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6528,
                                                     'cta pelvis abd', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6529,
                                                     'abd pelvis cta', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(882, 'abdominal_angiography', 6530,
                                                     'pelvis abd cta', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(883, 'renal_and_adrenal_angiography', 6540,
                                                     'renal and adrenal cta', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(883, 'renal_and_adrenal_angiography', 6541,
                                                     'renal adrenal cta', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(883, 'renal_and_adrenal_angiography', 6542,
                                                     'adrenal renal cta', 'NORM_COMP'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(883, 'extremities_angiography', 6550,
                                                      'cta of the extremities', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(883, 'extremities_angiography', 6551,
                                                     'cta extremities', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(883, 'extremities_angiography', 6552,
                                                      'extremities cta', 'PT'))

    # synonyms for MRI
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5013, 'magnetic_resonance_imaging', 6600,
                                                      'magnetic resonance imaging', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5013, 'magnetic_resonance_imaging', 6601,
                                                      'mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5014, 'cerebral_mri', 6602, 'head mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5014, 'cerebral_mri', 6603, 'mri head', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5014, 'cerebral_mri', 6604, 'mri of the head', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5014, 'cerebral_mri', 6605, 'mri of the brain', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5014, 'cerebral_mri', 6606, 'mri brain', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5014, 'cerebral_mri', 6607, 'brain mri', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5014, 'cerebral_mri', 6608, 'mr head', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5015, 'thoracic_mri', 6610, 'chest mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5015, 'thoracic_mri', 6611, 'mri chest', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5015, 'thoracic_mri', 6612, 'mri of the chest', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5015, 'thoracic_mri', 6613, 'torso mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5015, 'thoracic_mri', 6614, 'mri torso', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5015, 'thoracic_mri', 6615, 'mri of the torso', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6620, 'abdominal mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6621, 'mri abdominal', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6622, 'mri abdomen', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6623, 'mri of the abdomen', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6624, 'mri abd', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6625, 'abd mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6626, 'mri of the pelvis', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6627, 'mri pelvis', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6628, 'pelvis mri', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6629, 'mri abd pelvis', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6630, 'mri pelvis abd', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6631, 'abd pelvis mri', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5016, 'abdominal_mri', 6632, 'pelvis abd mri', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5017, 'renal_and_adrenal_mri', 6650,
                                                     'renal and adrenal mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5017, 'renal_and_adrenal_mri', 6651,
                                                     'adrenal and renal mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5017, 'renal_and_adrenal_mri', 6652,
                                                     'renal adrenal mri', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5017, 'renal_and_adrenal_mri', 6653,
                                                     'adrenal renal mri', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5018, 'extremities_mri', 6654,
                                                     'extremities mri', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5018, 'extremities_mri', 6655,
                                                     'mri extremities', 'NORM'))

    # synonyms for MRA
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5019, 'magnetic_resonance_angiography', 6700,
                                                      'magnetic resonance angiography', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5019, 'magnetic_resonance_angiography', 6701,
                                                      'mri', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5020, 'cerebral_mra', 6702, 'head mra', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5020, 'cerebral_mra', 6703, 'mra head', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5020, 'cerebral_mra', 6704, 'mra of the head', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5020, 'cerebral_mra', 6705, 'mra of the brain', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5020, 'cerebral_mra', 6706, 'mra brain', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5020, 'cerebral_mra', 6707, 'brain mra', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5021, 'thoracic_mra', 6710, 'chest mra', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5021, 'thoracic_mra', 6711, 'mra chest', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5021, 'thoracic_mra', 6712, 'mra of the chest', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5021, 'thoracic_mra', 6713, 'torso mra', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5021, 'thoracic_mra', 6714, 'mra torso', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5021, 'thoracic_mra', 6715, 'mra of the torso', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6720, 'abdominal mra', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6721, 'mra abdominal', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6722, 'mra abdomen', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6723, 'mra of the abdomen', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6724, 'mra abd', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6725, 'abd mra', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6726, 'mra of the pelvis', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6727, 'mra pelvis', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6728, 'pelvis mra', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6729, 'mra abd pelvis', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6730, 'mra pelvis abd', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6731, 'abd pelvis mra', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5022, 'abdominal_mra', 6732, 'pelvis abd mra', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5023, 'renal_and_adrenal_mra', 6750,
                                                     'renal and adrenal mra', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5023, 'renal_and_adrenal_mra', 6751,
                                                     'adrenal and renal mra', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5023, 'renal_and_adrenal_mra', 6752,
                                                     'renal adrenal mra', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5023, 'renal_and_adrenal_mra', 6753,
                                                     'adrenal renal mra', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5024, 'extremities_mra', 6754,
                                                     'extremities mra', 'NORM'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5024, 'extremities_mra', 6755,
                                                     'mra extremities', 'NORM'))

    
    # synonyms for 'hospital_course_by_system'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(194, 'hospital_course_by_system', 6800,
                                                     'hospitalization by systems', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(194, 'hospital_course_by_system', 6801,
                                                     'hospitalization by system', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(194, 'hospital_course_by_system', 6802,
                                                     'hospitalization system', 'NORM_COMP'))

    # synonyms for 'renal_course'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5025, 'renal_course', 6810, 'renal course', 'PT'))
    
    # synonyms for 'xray_ankle'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5026, 'xray_ankle', 6820, 'xray ankle', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5026, 'xray_ankle', 6821, 'x-ray ankle', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5026, 'xray_ankle', 6822, 'ankle xray', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(5026, 'xray_ankle', 6823, 'ankle x-ray', 'PT'))
    
    # synonys for 'hematology_course'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(210, 'hematology_course', 6830, 'hematology', 'PT'))

    # synonyms for 'nasopharynx_exam'
    cid = 5027
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(cid, 'nasopharynx_exam', 6840, 'nasopharynx exam', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(cid, 'nasopharynx_exam', 6844, 'nasopharynx', 'PT'))

    # synonyms for 'hypopharynx_exam'
    cid = 5028
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(cid, 'hypopharynx_exam', 6850, 'hypopharynx exam', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(cid, 'hypopharynx_exam', 6851, 'hypopharynx', 'PT'))    
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(cid, 'hypopharynx_exam', 6852, 'laryngopharynx exam', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(cid, 'hypopharynx_exam', 6853, 'laryngopharynx', 'PT'))
    
    # synonyms for 'ultrasonography_abdomen'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6860, 'ruq u/s', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6861, 'ruq u s', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6862, 'ruq us', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6863, 'u/s ruq', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6864, 'u s ruq', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6865, 'us ruq', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6866, 'ruq ultrasound', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6867, 'ultrasound ruq', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6868,
                                                     'ultrasound right upper quadrant', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(857, 'ultrasonography_abdomen', 6869,
                                                     'right upper quadrant ultrasound', 'PT'))

    # synonyms for 'ultrasound'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6900, 'u/s', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6901, 'rue u/s', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6902, 'rue u s', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6903, 'rue us', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6904, 'u/s rue', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6905, 'u s rue', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6906, 'us rue', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6907, 'right upper extremity u s', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6908,
                                                     'right upper extremity ultrasound', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6909,
                                                     'ultrasound right upper extremity', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(856, 'ultrasound', 6910,
                                                     'ultrasound rue', 'PT'))

    # synonyms for 'oncology_family_history'
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(372, 'oncology_family_history', 6920, 'oncology hx', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(372, 'oncology_family_history', 6921, 'onc hx', 'PT'))

    # synonyms for chest_xray
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6930, 'chest pa and lateral', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6931, 'chest pa, and lateral', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6932, 'chest pa and lateral', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6933, 'chest pa lateral', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(839, 'chest_xray', 6934, 'pa and lateral', 'PT'))

    # synonyms for sleep habits
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(308, 'sleep_habits', 6940, 'sleep habits', 'PT'))
    outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(308, 'sleep_habits', 6941, 'sleep_habits', 'KM'))
    
    outfile.close()
    cursor.close()

###############################################################################
def extract_tree(conn):

    cursor = conn.cursor()
    
    # one empty dict for levels 0..7 inclusive
    maps = [{}, {}, {}, {}, {}, {}, {}, {}]

    db_extra = {}
    
    # extract all concepts starting from level 7 (deepest) to level 0 (top)

    for level in reversed(range(0, 8)):
        
        query = \
                "SELECT cid, kmname, tree \
                FROM concepts_tbl         \
                WHERE level = {0} AND concepttype = 'ATOMIC'".format(level)
        
        try:
            cursor.execute(query)
        except:
            log("extract_tree: could not execute query...")
            cursor.close()
            conn.close()
            sys.exit(-1)

        while True:
            row = cursor.fetchone()
            if row == None:
                break

            cid = row[0]
            concept_name = row[1]
            tree_code = row[2]

            # Correct an error for concept 308, which has "sleep_habits,_sleep"
            # as the concept name (kmname database column). Use "sleep_habits"
            # as the concept name.
            if CID_SLEEP_HABITS == cid:
                if "sleep_habits,_sleep" == concept_name:
                    concept_name = "sleep_habits"

            # Correct the spelling error for concept 695, level_of_consciousness
            elif CID_LEVEL_OF_CONSCIOUSNESS == cid:
                if 'level_of_cousciousness' == concept_name:
                    concept_name = 'level_of_consciousness'
                    
            # Concept 745 'appearance' is at level 10 with an invalid treecode,
            # so skip it. This is the only level 10 concept, by the way. Other
            # synonyms for 'appearance' and 'general appearance' map to existing
            # concepts of 'general_exam' and 'general_review'.
            elif 745 == cid:
                continue

            # skip any other concepts with empty tree codes
            if len(tree_code) > 0:
                maps[level][tree_code] = (cid, concept_name)

        log("extract_tree: query for level {0} returned {1} rows.".format(level, cursor.rowcount))

        # Concept 2921 'preoperative_medications' is missing a treecode, but
        # the concept 441 'postoperative_medications' has treecode 5.37.106.127
        # and no further children. This resolves to:
        #
        #     patient_history:            5
        #     medications:                5.37
        #     medications_by_situation:   5.37.106
        #
        # Assign treecode 5.37.106.500 to preoperative_medications.
        maps[3]['5.37.106.500'] = (2921, 'preoperative_medications')
        
        # add additional concepts for computed tomography
        maps[5]['6.41.149.234.162.500']   = (5000, 'computed_tomography')
        maps[6]['6.41.149.234.162.500.1'] = (5001, 'cerebral_ct')
        maps[6]['6.41.149.234.162.500.2'] = (5002, 'thoracic_ct')
        maps[6]['6.41.149.234.162.500.3'] = (5003, 'abdominal_ct')
        maps[6]['6.41.149.234.162.500.4'] = (5004, 'renal_and_adrenal_ct')
        maps[6]['6.41.149.234.162.500.5'] = (5005, 'extremities_ct')

        # add additional concepts for magnetic resonance imaging
        maps[2]['6.41.500']         = (5010, 'nonradiographic_studies')
        maps[3]['6.41.500.1']       = (5011, 'types_of_nonradiographic_studies')
        maps[4]['6.41.500.1.1']     = (5012, 'nonradiographic_contrast_studies')
        maps[5]['6.41.500.1.1.1']   = (5013, 'magnetic_resonance_imaging')
        maps[6]['6.41.500.1.1.1.1'] = (5014, 'cerebral_mri')
        maps[6]['6.41.500.1.1.1.2'] = (5015, 'thoracic_mri')
        maps[6]['6.41.500.1.1.1.3'] = (5016, 'abdominal_mri')
        maps[6]['6.41.500.1.1.1.4'] = (5017, 'renal_and_adrenal_mri')
        maps[6]['6.41.500.1.1.1.5'] = (5018, 'extremities_mri')

        #add additional concepts for magnetic resonance angiography
        maps[5]['6.41.500.1.1.2']   = (5019, 'magnetic_resonance_angiography')
        maps[6]['6.41.500.1.1.2.1'] = (5020, 'cerebral_mra')
        maps[6]['6.41.500.1.1.2.2'] = (5021, 'thoracic_mra')
        maps[6]['6.41.500.1.1.2.3'] = (5022, 'abdominal_mra')
        maps[6]['6.41.500.1.1.2.4'] = (5023, 'renal_and_adrenal_mra')
        maps[6]['6.41.500.1.1.2.5'] = (5024, 'extremities_mra')
        
        # add concept for 'renal_course'
        maps[5]['5.32.77.79.18.500'] = (5025, 'renal_course')
        
        # add concept for 'xray_ankle'
        maps[7]['6.41.149.234.160.167.92.500']  = (5026, 'xray_ankle')

        # add concepts for nasopharynx_exam and hypopharynx_exam
        maps[5]['6.40.139.191.120.500'] = (5027, 'nasopharynx_exam')
        maps[5]['6.40.139.191.120.501'] = (5028, 'hypopharynx_exam')

        # update the 'extra' additions to the database for each level-0 concept
        
        # level-0 treecode 5 is concept id 63, 'patient_history'
        # level-0 treecode 6 is concept id 544, 'objective_data'
        db_extra[ 63] = 2
        db_extra[544] = 24
        #db_extra[544] = 22 - 7 + 9
        
    cursor.close()

    # # log the concept hierarchies
    # # level in [7, 6, ..., 1, 0]
    # for level in reversed(range(0, 8)):

    #     log("CURRENT LEVEL: {0}".format(level))
        
    #     # for each entry in the map at this level
    #     for key in maps[level].keys():

    #         l = level
    #         tree_code = key
    #         while l >= 0:
    #             concept_name = maps[l][tree_code]
    #             indent = '    ' * (7 - l)
    #             log("{0}{1}".format(indent, concept_name))

    #             # up one level for the next iteration
    #             l -= 1

    #             # remove final '.' and following digits
    #             tree_code = tree_code[0:tree_code.rfind('.')]

    #             # concept 2945 is missing a tree entry
    #             if 0 == len(tree_code):
    #                 break

    #     break

    # build the concept hierarchy graph
    # Stage 1: add nodes to graph without linking to children or parents
    # Stage 2: link children and parents

    graph = ConceptGraph()

    # stage 1: create the node list, build cid-to-index map
    for level in reversed(range(0, 8)):
        for key in maps[level].keys():
            cid = maps[level][key][0]
            concept_name = maps[level][key][1]
            treecode = key
            node = Node(cid, level, concept_name, treecode)
            graph.add_node(node)

    log("Concept graph node count: {0}".format(graph.size()))

    # stage 2: add child => parent and child <= parent links, work bottom-up
    for level in reversed(range(1, 8)): # [7, 6, 5, 4, 3, 2, 1] NOT 0
        for key in maps[level].keys():
            child_tree_code  = key
            child_cid        = maps[level][child_tree_code][0]
            parent_tree_code = child_tree_code[0:child_tree_code.rfind('.')]
            parent_cid       = maps[level-1][parent_tree_code][0]
            graph.link_nodes(child_cid, parent_cid)

    # verify the graph construction
    graph.validate(db_extra)
            
    # ancestor_node_indices = graph.all_ancestors(846)
    # log("ancestor cids of node(cid == 846): ")
    # for a in ancestor_node_indices:
    #     log("{0}, ".format(graph.nodes[a].cid), end="")
    # log()

    # descendant_node_indices = graph.all_descendants(63)
    # log("descendant cids of node(cid == 63): count: {0}".format(len(descendant_node_indices)))
    # for d in descendant_node_indices:
    #     log("{0}, ".format(graph.nodes[d].cid), end="")
    # log()

    # for i in range(1, 28):
    #     cid = maps[0][str(i)][0]
    #     descendants = graph.all_descendants(cid)
    #     log("{0}.* has {1} descendants.".format(i, len(descendants)))
    
    graph.dump_to_file(GRAPH_FILENAME)
    graph.dump_ancestor_cids_to_file(ANCESTOR_FILENAME)
    graph.dump_descendant_cids_to_file(DESCENDANT_FILENAME)

    graph2 = ConceptGraph()
    graph2.load_from_file(GRAPH_FILENAME, db_extra)
    graph2.load_ancestor_cids_from_file(ANCESTOR_FILENAME)
    
###############################################################################
try:
    conn = pymysql.connect(db = 'SecTag_Terminology',
                           host = 'localhost',
                           user = 'sectag',
                           passwd = 'sectag')
    
    log("Connected to SecTag_Terminology database.")
    
except:
    log("Cannot connect to MySQL server...")
    sys.exit(-1)

extract_synonyms(conn)
extract_tree(conn)

conn.close()
log("Disconnected")

