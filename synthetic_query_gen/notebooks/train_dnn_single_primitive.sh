#!/bin/bash
#SBATCH --job-name="cs8803"
#SBATCH -t 0-08:00
#SBATCH --mem-per-cpu=16G

module load anaconda3/4.4.0 
source activate cs8803ice

p=$1

echo "$p"
python3 ./train_ddn_for_query_results.py "$p" "./data/note_id_df_sample20k.p" "./data/notes_with_truth_labels_for_query_primitives_20k.csv" "./data/dl_results_sample20K.csv"


    
