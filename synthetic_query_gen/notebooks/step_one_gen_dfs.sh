#!bin/bash

module load anaconda3/4.4.0 
source activate cs8803ice

python3 generate_label_and_notes_dfs.py "~/../../gv1/users/cherlihy3-gtri/mimic_all_report_ids.csv" "~/../../gv1/users/cherlihy3-gtri/primitive_query_results_all_patients.csv"