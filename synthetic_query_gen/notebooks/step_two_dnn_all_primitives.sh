#!bin/bash

module load anaconda3/4.4.0 
source activate cs8803ice

## declare an array variable

##declare -a primitives=('is_acetaminophen','is_afib','is_chf','is_dm','is_docusate','is_female','is_furosemide','is_gerd','is_glucose','is_heparin','is_high_cholesterol', 'is_hypertension','is_magnesium_sulfate','is_male', 'is_metoprolol', 'is_pantoprazole', 'is_potassium', 'is_renal_failure','is_respiratory_failure','is_sodium_chloride','is_uti','white','black','asian')

#declare -a primitives=('is_acetaminophen' 'is_afib' 'is_chf' 'is_dm' 'is_docusate' 'is_female' 'is_furosemide' 'is_gerd')

#declare -a primitives=('is_glucose' 'is_heparin' 'is_high_cholesterol' 'is_hypertension' 'is_magnesium_sulfate' 'is_male'  'is_metoprolol' 'is_pantoprazole')

declare -a primitives=('is_potassium' 'is_renal_failure' 'is_respiratory_failure' 'is_sodium_chloride' 'is_uti' 'white' 'black' 'asian')



## now loop through the above array
for p in "${primitives[@]}";

do
   echo "$p"
   sbatch train_dnn_single_primitive.sh "$p"
   
done

    
