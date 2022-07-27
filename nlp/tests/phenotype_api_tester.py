try:
    from .data_access import *
    from .apis import *
    from .results import *
except Exception:
    from apis import *
    from data_access import *
    from results import *

import time


if __name__ == "__main__":
    # Mongo, Postgres and Luigi should be running
    ptype = PhenotypeDefine('Sepsis', 'phenotype', version='1')
    using_omop = PhenotypeDefine('OMOP', 'datamodel', version='5.3')
    clarity_core = PhenotypeDefine('ClarityCore', 'include', version='1.0', alias='ClarityNLP')

    Sepsis = PhenotypeDefine("Sepsis", "termset", values=['Sepsis', 'Systemic infection'])
    Ventilator = PhenotypeDefine("Ventilator", "termset", values=['ventilator', 'vent', 'ventilation'])

    onVentilator = PhenotypeEntity('onVentilator', 'define',
                                   library='ClarityNLP',
                                   funct='TermFinder',
                                   named_arguments={
                                       "termsets": ['Ventilator'],
                                   })

    hasSepsis = PhenotypeEntity('hasSepsis', 'define',
                                library='Clarity',
                                funct='ProviderAssertion',
                                named_arguments={
                                    "termsets": ['Sepsis'],
                                })
    #

    #SepsisState = PhenotypeOperations('SepsisState', 'OR', ['onVentilator', 'hasSepsis'], final=True)

    report1 = Report(
        report_type='Example Doc',
        _id='0',
        report_id='0',
        source='Super Test Document Set',
        report_date="2022-06-24T15:02:43.378272Z",
        subject='TEST_SUBJECT_1234',
        report_text="septic shock and on vent"
        #report_text="REASON FOR CONSULTATION: ICU management.\n\nHISTORY OF PRESENT ILLNESS: The patient is a 43-year-old gentleman who presented from an outside hospital with complaints of right upper quadrant pain in the abdomen, which revealed possible portal vein and superior mesenteric vein thrombus leading to mesenteric ischemia. The patient was transferred to the ABCD Hospital where he had a weeklong course with progressive improvement in his status after aggressive care including intubation, fluid resuscitation, and watchful waiting. The patient clinically improved; however, his white count remained elevated with the intermittent fevers prompting a CT scan. Repeat CT scan showed a loculated area of ischemic bowel with perforation in the left upper abdomen. The patient was taken emergently to the operating room last night by the General Surgery Service where proximal half of the jejunum was noted to be liquified with 3 perforations. This section of small bowel was resected, and a wound VAC placed for damage control. Plan was to return the patient to the Operating Room tomorrow for further exploration and possible re-anastomosis of the bowel. The patient is currently intubated, sedated, and on pressors for septic shock and in the down ICU.\n\nPAST MEDICAL HISTORY: Prior to coming into the hospital for this current episode, the patient had hypertension, diabetes, and GERD.\n\nPAST SURGICAL HISTORY: Included a cardiac cath with no interventions taken.\n\nHOME MEDICATIONS: Include Lantus insulin as well as oral hypoglycemics.\n\nCURRENT MEDS: Include Levophed, Ativan, fentanyl drips, cefepime, Flagyl, fluconazole, and vancomycin. Nexium, Synthroid, hydrocortisone, and Angiomax, which is currently on hold.\n\nREVIEW OF SYSTEMS: Unable to be obtained secondary to the patient\\'s intubated and sedated status.\n\nALLERGIES: None.\n\nFAMILY HISTORY: Includes diabetes on his father side of the family. No other information is provided.\n\nSOCIAL HISTORY: Includes tobacco use as well as alcohol use.\n\nPHYSICAL EXAMINATION:\nGENERAL: The patient is currently intubated and sedated on Levophed drip.\nVITAL SIGNS: Temperature is 100.6, systolic is 110/60 with MAP of 80, and heart rate is 120, sinus rhythm.\nNEUROLOGIC: Neurologically, he is sedated, on Ativan with fentanyl drip as well. He does arouse with suctioning, but is unable to open his eyes to commands.\nHEAD AND NECK EXAMINATION: His pupils are equal, round, reactive, and constricted. He has no scleral icterus. His mucous membranes are pink, but dry. He has an EG tube, which is currently 24-cm at the lip. He has a left-sided subclavian vein catheter, triple lumen.\nNECK: His neck is without masses or lymphadenopathy or JVD.\nCHEST: Chest has diminished breath sounds bilaterally.\nABDOMEN: Abdomen is soft, but distended with a wound VAC in place. Groins demonstrate a left-sided femoral outline.\nEXTREMITIES: His bilateral upper extremities are edematous as well as his bilateral lower extremities; however, his right is more than it is in the left. His toes are cool, and pulses are not palpable.\n\nLABORATORY EXAMINATION: Laboratory examination reveals an ABG of 7.34, CO2 of 30, O2 of 108, base excess of -8, bicarb of 16.1, sodium of 144, potassium of 6.5, chloride of 122, CO2 18, BUN 43, creatinine 2.0, glucose 172, calcium 6.6, phosphorus 1.1, mag 1.8, albumin is 1.6, cortisone level random is 22. After stimulation with cosyntropin, they were still 22 and then 21 at 30 and 60 minutes respectively. LFTs are all normal. Amylase and lipase are normal. Triglycerides are 73, INR is 2.2, PTT is 48.3, white count 20.7, hemoglobin 9.6, and platelets of 211. UA was done, which also shows a specific gravity of 1.047, 1+ protein, trace glucose, large amount of blood, and many bacteria. Chest x-rays performed and show the tip of the EG tube at level of the carina with some right upper lobe congestion, but otherwise clear costophrenic angles. Tip of the left subclavian vein catheter is appropriate, and there is no pneumothorax noted.\n\nASSESSMENT AND PLAN: This is a 43-year-old gentleman who is acutely ill, in critical condition with mesenteric ischemia secondary to visceral venous occlusion. He is status post small bowel resection. We plan to go back to operating room tomorrow for further debridement and possible closure. Neurologically, the patient initially had question of encephalopathy while in the hospital secondary to slow awakening after previous intubation; however, he did clear eventually, and was able to follow commands. I did not suspect any sort of pathologic abnormality of his neurologic status as he has further CT scan of his brain, which was normal. Currently, we will keep him sedated and on fentanyl drip to ease pain and facilitate ventilation on the respirator. We will form daily sedation holidays to assess his neurologic status and avoid over sedating with Ativan.\n1. Cardiovascular. The patient currently is in septic shock requiring vasopressors maintained on MAP greater than 70. We will continue to try to wean the vasopressin after continued volume loading, also place SvO2 catheter to assess his oxygen delivery and consumption given his state of shock. Currently, his rhythm is of sinus tachycardia, I do not suspect AFib or any other arrhythmia at this time. If he does not improve as expected with volume resuscitation and with resolution of his sepsis, we will obtain an echocardiogram to assess his cardiac function. Once he is off the vasopressors, we will try low-dose beta blockade as tolerated to reduce his rate.\n2. Pulmonology. Currently, the patient is on full vent support with a rate of 20, tidal volume of 550, pressure support of 10, PEEP of 6, and FiO2 of 60. We will wean his FiO2 as tolerated to keep his saturation greater than 90% and wean his PEEP as tolerated to reduce preload compromise. We will keep the head of bed elevated and start chlorhexidine as swish and swallow for VAP prevention.\n3. Gastrointestinal. The patient has known mesenteric venous occlusion secondary to the thrombus formation at the portal vein as well as the SMV. He is status post immediate resection of jejunum leaving a blind proximal jejunum and blind distal jejunum. We will maintain NG tube as he has a blind stump there, and we will preclude any further administration of any meds through this NG tube. I will keep him on GI prophylaxis as he is intubated. We will currently hold his TPN as he is undergoing a large amount of volume changes as well as he is undergoing electrolyte changes. He will have a long-term TPN after this acute episode. His LFTs are all normal currently. Once he is postop tomorrow, we will restart the Angiomax for his venous occlusion.\n4. Renal. The patient currently is in the acute renal insufficiency with anuria and an increase in his creatinine as well as his potassium. His critical hyperkalemia which is requiring dosing of dextrose insulin, bicarb, and calcium; we will recheck his potassium levels after this cocktail. He currently is started to make more urine since being volume resuscitated with Hespan as well as bicarb drip. Hopefully given his increased urine output, he will start to eliminate some potassium and will not need dialysis. We will re-consult Nephrology at this time.\n5. Endocrine. The patient has adrenal insufficiency based on lack of stem to cosyntropin. We will start hydrocortisone 50 q.6h.\n6. Infectious Disease. Currently, the patient is on broad-spectrum antibiotic prophylaxis imperially. Given his bowel ischemia, we will continue these, and appreciate ID service\\'s input.\n7. Hematology. Hematologically, the patient has a hypercoagulable syndrome, also had HIT secondary to his heparin administration. We will restart the Angiomax once he is back from the OR tomorrow. Currently, his INR is 2.2. Therefore, he should be covered at the moment. Appreciate the Hematology\\'s input in this matter.\n\nPlease note the total critical care time spent at the bedside excluding central line placement was 1 hour.\"\n       "
    )

    sepsisPhenotype = PhenotypeModel(owner='test',
                                     phenotype=ptype,
                                     description='this is a test!',
                                     data_models=[],
                                     includes=[clarity_core],
                                     value_sets=[],
                                     term_sets=[Ventilator, Sepsis],
                                     data_entities=[
                                         onVentilator, hasSepsis
                                     ],
                                     reports=[
                                         report1
                                     ])
    status = post_phenotype(sepsisPhenotype)
    log(json.dumps(sepsisPhenotype.to_json(), indent=4))

    job_id = status.get('job_id')
    while True:

        if job_id:
            results = paged_phenotype_results(job_id, False)
            results2 = paged_phenotype_results(job_id, True)
            res2len = (len(results2.get('results')))
            res1len = (len(results.get('results')))
            if res1len > 0:
                log(results)
                break
            if res2len > 0:
                log(results2)
                break

            time.sleep(1)
        else:
            break


