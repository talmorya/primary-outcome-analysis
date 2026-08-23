# Revised pilot report (pilot_20260819_124046)

## Retrieval criteria
- StudyType = INTERVENTIONAL
- InterventionType = BEHAVIORAL
- Conditions: chronic back pain, fibromyalgia, migraine (IBS excluded)

## Studies retrieved by condition (API totalCount, deduplicated pool may overlap)

- chronic_back_pain: 330
- fibromyalgia: 233
- migraine: 153
- Unique studies in 1-page pool per condition: 298
- Pilot sample extracted: 40
- Primary outcome rows: 113

## Behavioral intervention counts
- Studies with psychological component identified: 38
- Flagged potentially non-psychological behavioral: 7 (17.5%)

## Multimodal studies
- Count: 13 (32.5%)

### Examples

- **NCT01666639**: component=cbt | self_management; other_type=physical_rehabilitation; other_name=Behavioral Medical Rehabilitation plus behavioral exercise therapy | Usual Behavioral Medical Rehabilitation
- **NCT07766616**: component=act | mindfulness_mbsr_mbct; other_type=physical_rehabilitation; other_name=Acceptance and Commitment Therapy (ACT) | Standard Physiotherapy Program
- **NCT05611476**: component=biofeedback; other_type=physical_rehabilitation; other_name=Cognitive Muscular Therapy for low back pain
- **NCT04142177**: component=cbt | pain_education | relaxation | self_management; other_type=complementary_integrative | surgical_procedure; other_name=Tailored exercise | Continued Care and Active Monitoring | Spinal Manipulation Therapy (SMT) | Yoga
- **NCT07179016**: component=coaching | digital_psychological | self_management; other_type=complementary_integrative; other_name=Auricular Point Acupressure (APA) - Self Management (SM)
- **NCT05571215**: component=pain_education; other_type=device; other_name=Transcranial Direct Current Stimulation
- **NCT05811624**: component=pain_education; other_type=physical_rehabilitation; other_name=Physiotherapy intervention, including behavioral weight reduction program combined with pain neuroscience education and cognition-targeted exercise therapy. | Physiotherapy intervention, including pain neuroscience education and cognition-targeted exercise therapy alone.
- **NCT01147120**: component=relaxation; other_type=surgical_procedure; other_name=Clinical Massage Therapy (CMT)

## Instrument false positives (ISI substring issue)
- Known false-positive cases in old pilot fixed: 8

Old false-positive outcome_ids:

- NCT03819907__po_1
- NCT07454395__po_1
- NCT07454395__po_2
- NCT07203339__po_2
- NCT07203339__po_3
- NCT07203339__po_4
- NCT07203339__po_5
- NCT07203339__po_6

- Remaining ISI false positives in revised pilot: 0

## outcome_purpose distribution

outcome_purpose
therapeutic_clinical          28
other                         20
psychological                 18
functional                    18
feasibility_recruitment       18
acceptability_satisfaction     6
safety_adverse_events          3
biological_physiological       1
uncertain                      1

## Multiple-primary-outcome examples

### NCT06605248 (16 primaries)
- NOTUS Feasibility Study: Reducing Chronic Low Back Pain With Mobile App Intervention
- Purposes: acceptability_satisfaction, feasibility_recruitment, other, safety_adverse_events
  - PO1: Individuals meeting the preliminary eligibility criteria [feasibility_recruitment] instruments=nan
  - PO2: General practitioners who agreed to prescribe a digital intervention [feasibility_recruitment] instruments=nan
  - PO3: Individuals who recieved participant information form compared to those that met the preliminary eli [feasibility_recruitment] instruments=nan
  - PO4: Individuals who completed the full eligibility criteria compared to those who shared their details [feasibility_recruitment] instruments=nan
  - PO5: Number of individuals who provided consent to participate [feasibility_recruitment] instruments=nan
  - PO6: Number of individuals who provided consent for the research group to collect MBS and PBS data. [feasibility_recruitment] instruments=nan
  - PO7: Proportion of individuals who completed the baseline questionnaires [feasibility_recruitment] instruments=nan
  - PO8: Recruitment rate per day, week or month. [feasibility_recruitment] instruments=nan
  - PO9: The Acceptability of Intervention Measure [acceptability_satisfaction] instruments=nan
  - PO10: The Appropriateness of Intervention Measure [other] instruments=nan
  - PO11: Completion rate of questionnaires [acceptability_satisfaction] instruments=Numeric Rating Scale | Tampa Scale of Kinesiophobia | Pain Self-Efficacy Questionnaire
  - PO12: Adherence to the digital intervention [other] instruments=nan
  - PO13: Mobile App Rating Satisfaction Sub-Scale [acceptability_satisfaction] instruments=nan
  - PO14: Participants experience through semi-structured interview [feasibility_recruitment] instruments=nan
  - PO15: Adverse events [safety_adverse_events] instruments=nan
  - PO16: Participants experience with the intervention [other] instruments=nan

### NCT04084795 (13 primaries)
- Augmentation of EMDR With tDCS in the Treatment of Fibromyalgia
- Purposes: functional, other, psychological, therapeutic_clinical
  - PO1: Change in severity and in pain intensity as measured by the Visual Analogue Scale (VAS) [therapeutic_clinical] instruments=Visual Analog Scale
  - PO2: Change in physical impairment due to FM assessed by The Revised Fibromyalgia Impact Questionnaire (F [functional] instruments=Fibromyalgia Impact Questionnaire
  - PO3: Change in catastrophic thinking related to pain experiences assessed by the Pain Catastrophizing Sca [psychological] instruments=Pain Catastrophizing Scale
  - PO4: Change in the impact of fatigue as assessed by the Brief Fatigue Inventory (BFI) [psychological] instruments=nan
  - PO5: PTSD diagnosis assessed by the Global Evaluation of Posttraumatic Stress (EGEP-5) [psychological] instruments=nan
  - PO6: Complex PTSD diagnosis assessed by The International Trauma Questionnaire (ITQ) [psychological] instruments=nan
  - PO7: Change in PTSD symptoms as measured by the Posttraumatic Stress Disorder Checklist (PCL-5) [psychological] instruments=nan
  - PO8: Change in subjective perceived distress assessed by Subjective unit of distress (SUD) [psychological] instruments=nan
  - PO9: Quantifying childhood trauma assessed by The Childhood Trauma Questionnaire (CTQ) [other] instruments=nan
  - PO10: Assessing lifetime trauma with the Timeline of traumatic experiences [other] instruments=nan
  - PO11: Change in depersonalization symptoms assessed by The Cambridge Depersonalization Scale (CDS) [therapeutic_clinical] instruments=nan
  - PO12: Change in somatoform dissociation symptoms assessed by Somatoform Dissociation Questionnaire 20 (SDQ [therapeutic_clinical] instruments=nan
  - PO13: Change in anxious and depressive symptoms assessed by with the Hospital Anxiety and Depression Scale [psychological] instruments=Hospital Anxiety and Depression Scale

### NCT03319355 (8 primaries)
- Multicomponent Therapy for Fibromyalgia
- Purposes: other, psychological, therapeutic_clinical
  - PO1: Fibromyalgia Impact Questionnaire [other] instruments=Fibromyalgia Impact Questionnaire
  - PO2: Tampa scale for kinesiophobia [other] instruments=Tampa Scale of Kinesiophobia
  - PO3: Beck Depression Index [psychological] instruments=nan
  - PO4: Pain Coping Inventory [therapeutic_clinical] instruments=nan
  - PO5: Pain at tenderpoints [therapeutic_clinical] instruments=nan
  - PO6: Grip strength [other] instruments=nan
  - PO7: Walking [other] instruments=nan
  - PO8: cycling [other] instruments=nan

### NCT04257539 (7 primaries)
- Reducing Sedentary Time in Chronic Low Back Pain: Sedentary Intervention Using Motivational Interviewing and Technology
- Purposes: other, psychological, therapeutic_clinical
  - PO1: Change from baseline monitor-assessed sedentary time at 8 weeks [other] instruments=nan
  - PO2: Change from baseline depressive symptoms at 8 weeks [psychological] instruments=PHQ-9
  - PO3: Change from baseline low back pain symptoms at 8 weeks [therapeutic_clinical] instruments=nan
  - PO4: Change from baseline pain sensitivity levels at 8 weeks [therapeutic_clinical] instruments=nan
  - PO5: Change from baseline pain inhibition at 8 weeks [therapeutic_clinical] instruments=nan
  - PO6: Change from baseline plasma cytokine levels at 8 weeks [other] instruments=nan
  - PO7: Change from baseline plasma endocannabinoid levels at 8 weeks [other] instruments=nan

### NCT00170118 (5 primaries)
- Effects of Motivational Interviewing on Self-Efficacy and Standardized Low Back Pain Outcomes in Patients With Chronic Back Pain"
- Purposes: acceptability_satisfaction, functional, other, therapeutic_clinical, uncertain
  - PO1: SF - 12 [uncertain] instruments=nan
  - PO2: Self-efficacy for Managing Chronic disease 6-Item scale [other] instruments=nan
  - PO3: Roland and Morris Disability Questionnaire [functional] instruments=nan
  - PO4: Pain Visual analog scale [therapeutic_clinical] instruments=Visual Analog Scale
  - PO5: Satisfaction with care question [acceptability_satisfaction] instruments=nan


## NCT05658185 preserved outcomes

### NCT05658185__po_1
- Measure: Change Emotional Distress Baseline T1, Baseline T2-Pre, Post-Treatment T3 and Follow-up T4.
- Description: Assessment with Hospital Anxiety and Depression Scale in caregivers (HADS): Screening instrument for the detection of affective disorders, in non-psychiatric subjects who go to hospitals. The scale is made up of 14 items, with a range of scores from 0 to 42. The interpretation is that the higher the score, the greater the presence of anxiety-depressive symptoms.
- Time frame: T1. Start T2.10 weeks after T1, T3. Evaluation 10 weeks after T2, after the intervention is finished. T4. Follow-up, 10 weeks after post-treatment.
- Instruments: Hospital Anxiety and Depression Scale
- Acronyms: HADS
- Purpose: psychological

### NCT05658185__po_2
- Measure: Change in Perception of psychological stress. Baseline T1, Baseline T2-Pre, Post-Treatment T3 and Follow-up T4.
- Description: Assessment with EEP-10. The Spanish version of the EEP-10 used by Remor in a validation study with adults in Spain was used. The scale includes a series of direct queries that explore the level of stress experienced during the last month. The items are easily understood. The scale provides five response options: 'never', 'hardly ever', 'occasionally', 'many times' and 'always', which are ranked from zero to four.
- Time frame: T1. Start T2.10 weeks after T1, T3. Evaluation 10 weeks after T2, after the intervention is finished. T4. Follow-up, 10 weeks after post-treatment.
- Instruments: nan
- Acronyms: EEP-10
- Purpose: psychological

### NCT05658185__po_3
- Measure: Change in quality of life. Baseline T1, Baseline T2-Pre, Post-Treatment T3 and Follow-up T4.
- Description: Assessment with MSQ 21. (Migraine-Specific Quality of Life Questionnaire or MSQ)21 is a migraine-specific questionnaire designed to assess limitations in quality of life and the effect of treatments.
- Time frame: T1. Start T2.10 weeks after T1, T3. Evaluation 10 weeks after T2, after the intervention is finished. T4. Follow-up, 10 weeks after post-treatment.
- Instruments: Migraine-Specific Quality of Life Questionnaire
- Acronyms: MSQ
- Purpose: therapeutic_clinical
