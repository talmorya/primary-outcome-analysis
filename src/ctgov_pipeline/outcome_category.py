"""Hierarchical outcome category classification."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class OutcomeCategory:
    outcome_category: str
    outcome_subcategory: str
    rule: str
    review_flag: bool = False


def _text(measure: str | None, description: str | None, time_frame: str | None) -> str:
    return " ".join(part for part in [measure or "", description or "", time_frame or ""] if part).lower()


_MEASURE_ONLY_CATEGORIES = frozenset({"feasibility_acceptability", "mechanistic"})

_FIRST_PASS_RULES: list[tuple[str, str, str, list[str]]] = [
    # Mechanistic outcomes (experimental / biological measures). Like the feasibility rules they
    # read the measure NAME only. `biological_structural` is in the second pass.
    (
        "mechanistic",
        "neuroimaging_neural",
        "CAT_MECH_NEURO",
        [
            r"\bfmri\b", r"\beeg\b", r"\bmri\b", r"connectivity", r"neuroimaging", r"brain (?:activity|imaging|function)",
            r"\bneural\b", r"cerebral blood flow", r"arterial spin", r"\basl\b", r"magnetic resonance", r"\bmrs\b",
            r"resting[- ]state", r"late positive potential", r"error related negativity", r"evoked potential", r"\bvep\b",
            r"theta power", r"contingent negative variation", r"white matter", r"fronto-striatal",
            r"cortical (?:excitab|map)", r"motor cortical", r"transcranial magnetic", r"\br?tms\b", r"transverse relaxation", r"\bivim\b",
        ],
    ),
    (
        "mechanistic",
        "sensory_qst",
        "CAT_MECH_QST",
        [
            r"\bqst\b", r"quantitative sensory", r"pain threshold", r"pain tolerance", r"pain summation", r"temporal summation",
            r"pressure pain", r"conditioned pain modulation", r"\bcpm\b", r"hyperalgesia", r"detection threshold",
            r"sensory limen", r"thermal stimul", r"sensory stimul", r"psychophysical", r"pain sensitivity",
            r"(?:ischemic|evoked|heat|cold|thermal) pain", r"cold pressor", r"experimental pain", r"ratings of painful sensory",
            r"pain modulation", r"painful (?:heat|pressure)", r"pressure stimul", r"kg/cm",
        ],
    ),
    (
        "mechanistic",
        "biomarker_inflammatory",
        "CAT_MECH_BIOMARKER",
        [
            r"\bbiomarker", r"inflammat", r"cytokine", r"\bcortisol\b", r"gene expression", r"neuroimmune",
            r"tumou?r necrosis", r"\btnf\b", r"interleukin", r"\bil-\d", r"\bcrp\b", r"c-reactive", r"\bbdnf\b",
            r"myo-inositol", r"n-acetylaspartate", r"\bcholine\b", r"\blactate\b", r"\bcreatine\b",
        ],
    ),
    (
        "mechanistic",
        "psychophysiological",
        "CAT_MECH_PSYCHOPHYS",
        [r"heart rate variability", r"^hrv\b", r"\(hrv\)", r"psychophysiol", r"electrophysiol", r"peripheral arousal"],
    ),
    (
        "mechanistic",
        "other_mechanistic",
        "CAT_MECH_OTHER",
        [
            r"dopamine response", r"neurotransmitter", r"attentional bias", r"contingency awareness", r"pain expectancy",
            r"selective learning", r"temporal binding", r"psychophysical adaptation", r"petco2", r"provocation",
            r"inducible dizziness", r"point of subjective simultaneity", r"dataset of functional magnetic",
        ],
    ),
    (
        "feasibility_acceptability",
        "safety",
        "CAT_FEAS_SAFETY",
        [r"\badverse\b", r"\bsafety\b", r"side effect", r"tolerability", r"serious adverse"],
    ),
    (
        "feasibility_acceptability",
        "feasibility_recruitment",
        "CAT_FEAS_RECRUITMENT",
        [
            r"\bfeasibility\b",
            r"\brecruitment\b",
            r"\benrollment\b",
            r"\baccrual\b",
            r"screening rate",
            r"eligibility rate",
            r"\bscreened\b",
            r"\benrolled\b",
            r"\benrollees\b",
            r"\brefus",
            r"interested participants",
            r"eligibility criteria",
        ],
    ),
    (
        "feasibility_acceptability",
        "acceptability_satisfaction",
        "CAT_FEAS_ACCEPTABILITY",
        [
            r"\bacceptability\b",
            r"\bsatisfaction\b",
            r"\busability\b",
            r"user experience",
            r"participant experience",
            r"ease of use",
            r"^(?:participant[- ]rated )?enjoyment",
            r"\bfeedback\b",
            r"exit interview",
            r"treatment evaluation",
            r"agreed to",
        ],
    ),
    (
        "feasibility_acceptability",
        "adherence_fidelity",
        "CAT_FEAS_ADHERENCE",
        [
            r"\badherence\b",
            r"\bcompliance\b",
            r"\bfidelity\b",
            r"protocol adherence",
            r"therapist adherence",
            r"treatment integrity",
            r"\b(?:were|was) delivered",
            r"duration of (?:use|virtual reality sessions)",
            r"(?:days|minutes).{0,40}(?:spent|used|performed)",
            r"sessions? (?:completed|attended)",
        ],
    ),
    (
        "feasibility_acceptability",
        "other_feasibility",
        "CAT_FEAS_OTHER",
        [
            r"retention rate",
            r"drop[- ]?out rate",
            r"completion rate",
            r"completeness",
            r"(?:assessments?|questionnaires?|diar(?:y|ies)) completed",
            r"\bdiary completion",
            r"complet(?:e|ed|ion of) .{0,15}the intervention",
            r"definitive (?:rct|trial)",
        ],
    ),
    (
        "mood",
        "anxiety",
        "CAT_MOOD_ANXIETY",
        [r"\banxiety\b", r"\bpanic\b", r"state[- ]trait anxiety", r"\bgsi\b", r"\bbai\b"],
    ),
    (
        "mood",
        "depression",
        "CAT_MOOD_DEPRESSION",
        [r"\bdepress", r"\bphq", r"\bbeck depression", r"\bces-d\b", r"\bham-d\b"],
    ),
    (
        "pain_interference",
        "coping_adaptation",
        "CAT_INTERFERE_CATASTROPHIZING",
        [r"catastroph", r"\bpcs\b"],
    ),
    (
        "mood",
        "distress_stress",
        "CAT_MOOD_DISTRESS",
        [r"\bdistress\b", r"\bstress\b", r"\bmood\b", r"emotional distress", r"psychological stress"],
    ),
    (
        "pain_interference",
        "disability",
        "CAT_INTERFERE_DISABILITY",
        [
            r"\bdisability\b",
            r"\bfunctional\b",
            r"\bfunctioning\b",
            r"activities of daily living",
            r"\badl\b",
            r"\bfiq\b",
            r"fibromyalgia impact",
            r"\bpdih\b",
            r"\bpdii\b",
            r"\bodi\b",
            r"roland[- ]morris",
            r"rmdq",
        ],
    ),
    (
        "pain_interference",
        "work_participation",
        "CAT_INTERFERE_WORK",
        [r"return to work", r"work ability", r"work productivity", r"sick leave", r"presenteeism"],
    ),
    (
        "pain_interference",
        "coping_adaptation",
        "CAT_INTERFERE_COPING",
        [r"\bcoping\b", r"self[- ]efficacy", r"pain acceptance", r"adaptation", r"resilience"],
    ),
    (
        "pain_interference",
        "quality_of_life",
        "CAT_INTERFERE_QOL",
        [r"quality of life", r"\bqol\b", r"\bsf-36\b", r"\bsf36\b", r"\bpromis\b", r"health[- ]related quality"],
    ),
    (
        "pain_interference",
        "interference",
        "CAT_INTERFERE_GENERAL",
        [r"interference", r"interfering", r"impact on", r"life impact"],
    ),
    (
        "pain_recovery",
        "pain_intensity",
        "CAT_PAIN_INTENSITY",
        [
            r"pain intensity",
            r"pain severity",
            r"pain score",
            r"pain level",
            r"average pain",
            r"worst pain",
            r"current pain",
            r"\bvas\b",
            r"\bnrs\b",
            r"numeric rating",
            r"visual analog",
        ],
    ),
    (
        "pain_recovery",
        "pain_frequency",
        "CAT_PAIN_FREQUENCY",
        [
            r"headache frequency",
            r"migraine frequency",
            r"headache days",
            r"migraine days",
            r"number of headache",
            r"attack frequency",
            r"episodes per",
        ],
    ),
    (
        "pain_recovery",
        "global_impression",
        "CAT_PAIN_GLOBAL",
        [
            r"global impression",
            r"\bcgis\b",
            r"\bpgic\b",
            r"patient global",
            r"clinician global",
            r"overall improvement",
            r"pain relief",
            r"pain reduction",
        ],
    ),
    (
        "pain_recovery",
        "general_pain",
        "CAT_PAIN_GENERAL",
        [
            r"\bpain\b",
            r"\bheadache\b",
            r"\bmigraine\b",
            r"\bsymptom",
            r"photophobia",
            r"headache disability",
        ],
    ),
]


_SECOND_PASS_RULES: list[tuple[str, str, str, list[str]]] = [
    # Feasibility: retention / completion of assessments first (before recruitment funnel steps).
    (
        "feasibility_acceptability",
        "other_feasibility",
        "CAT_FEAS_OTHER_2",
        [
            r"drop[- ]?outs?\b", r"withdraw", r"\bretention\b", r"\bretain",
            r"(?:assessment|questionnaires?|outcome measures?|tests?)\b.{0,30}\b(?:complet|fulfilled|returned)",
            r"complet.{0,30}\b(?:assessment|questionnaires?|outcome measures?|screening)",
            r"^follow[- ]up$", r"\battrition\b",
        ],
    ),
    (
        "feasibility_acceptability",
        "feasibility_recruitment",
        "CAT_FEAS_RECRUITMENT_2",
        [r"\beligib", r"\bconsent", r"proportion of .{0,30}randomi[sz]ed", r"\breach\)", r"program initiation", r"intervention commencement"],
    ),
    (
        "feasibility_acceptability",
        "adherence_fidelity",
        "CAT_FEAS_ADHERENCE_2",
        [
            r"\battend", r"\busage\b", r"\bengagement\b", r"participation rate", r"treatment participation",
            r"program participation", r"at-home practice", r"(?:intervention|treatment|program) completion",
            r"completing the", r"\butili[sz]e the\b", r"\buptake\b", r"made an appointment", r"initiating",
            r"number of sessions", r"homework", r"successful completion", r"frequency of using", r"(?:days|minutes).{0,30}practice",
            r"contamination",
        ],
    ),
    (
        "feasibility_acceptability",
        "acceptability_satisfaction",
        "CAT_FEAS_ACCEPTABILITY_2",
        [r"credibility", r"expectancy", r"perceptions? of (?:the )?intervention", r"exercise perceptions", r"experience with the intervention", r"\btrust score", r"semi[- ]structured interview",
         r"appropriateness", r"continued interest", r"willingness to pay", r"\badoption\b", r"confidence in carrying out", r"benefits and barriers", r"barriers and facilitators"],
    ),
    # Cost / service use / medication before generic quality-of-life patterns (cost per QALY).
    (
        "healthcare_use_cost",
        "cost_economic",
        "CAT_HEALTHCARE_COST",
        [r"(?<!task )\bcosts?\b", r"economic", r"budget impact", r"\bqaly\b", r"cost-effective", r"cost-utility"],
    ),
    (
        "healthcare_use_cost",
        "service_use",
        "CAT_HEALTHCARE_USE",
        [
            r"utili[sz]ation", r"(?:number of|physicians?|doctors?|gp) visits?", r"visits? (?:of|to) (?:physicians?|doctors?|gps?)", r"consultations?", r"referral", r"specialist care",
            r"imaging (?:orders|requests)", r"diagnostic error", r"safe diagnosis", r"hospital", r"emergency",
        ],
    ),
    (
        "healthcare_use_cost",
        "medication_use",
        "CAT_HEALTHCARE_MEDICATION",
        [r"medication", r"opioid", r"analgesic (?:use|consumption)", r"dependence on medicine", r"prescri"],
    ),
    (
        "mechanistic",
        "biological_structural",
        "CAT_MECH_BIOLOGICAL",
        [
            r"\bserum\b", r"\bplasma\b", r"blood (?:flow|extraction|oxygen)", r"\bbold\b", r"gr[ae]y matter",
            r"\bbrain\b", r"microbio", r"hormone", r"voxel", r"cerebr", r"ampk", r"temperature", r"thickness", r"ultrasound", r"fascia",
            r"muscle tone", r"pulsatility", r"endocannabinoid", r"inflammat", r"heart rate", r"glucos", r"glyc",
            r"hba1c", r"diabetes", r"noxious inhibitory", r"\bblood\b",
        ],
    ),
    (
        "pain_interference",
        "coping_adaptation",
        "CAT_INTERFERE_FEAR_AVOIDANCE",
        [r"kinesiophobi", r"\btampa\b", r"fear[- ]avoidance", r"\bfabq\b", r"fear of (?:movement|pain|re-?injury)", r"pain[- ]related fear", r"\btsk\b"],
    ),
    (
        "mood",
        "wellbeing_positive_psychology",
        "CAT_MOOD_WELLBEING",
        [
            r"positive affect", r"negative affect", r"optimis", r"well-?being", r"self[- ]compassion",
            r"\bmaas\b", r"\bffmq\b", r"\bmindfulness\b", r"emotion regulation", r"life satisfaction",
            r"burnout", r"emotional exhaustion", r"personal accomplishment",
            r"body (?:awareness|appreciation|trusting|functionality)", r"embodiment", r"body connection", r"own body",
        ],
    ),
    (
        "mood",
        "distress_stress",
        "CAT_MOOD_DISTRESS_2",
        [r"\bbsi\b", r"brief symptom inventory"],
    ),
    (
        "pain_interference",
        "coping_adaptation",
        "CAT_INTERFERE_COPING_2",
        [r"locus of control", r"illness perception", r"ability to cope", r"empower", r"problem[- ]solving", r"patient-specific goal", r"psychological flexibility", r"valued"],
    ),
    (
        "pain_interference",
        "disability",
        "CAT_INTERFERE_DISABILITY_2",
        [r"activit(?:y|ies) limitation", r"back[- ]related function", r"\bquebec\b"],
    ),
    (
        "pain_interference",
        "quality_of_life",
        "CAT_INTERFERE_QOL_2",
        [r"\bsf\s*-?\s*12\b", r"eq-?5d", r"euroqol", r"general health questionnaire", r"\bghq"],
    ),
    (
        "pain_interference",
        "work_participation",
        "CAT_INTERFERE_WORK_2",
        [r"employment", r"work status", r"sickness", r"sick[- ]?list", r"\babsence\b"],
    ),
    (
        "pain_recovery",
        "global_impression",
        "CAT_PAIN_GLOBAL_2",
        [r"clinical global", r"\bcgi\b", r"global perceived", r"proportion of responders", r"therapeutic changes"],
    ),
    (
        "pain_recovery",
        "pain_frequency",
        "CAT_PAIN_FREQUENCY_2",
        [r"headaches? frequency", r"frequency of headaches?", r"reduction of headaches?"],
    ),
    (
        "pain_recovery",
        "general_pain",
        "CAT_PAIN_GENERAL_2",
        [r"\bheadaches\b", r"\bdiscomfort\b"],
    ),
    (
        "associated_symptoms",
        "sleep",
        "CAT_SYMPTOM_SLEEP",
        [r"\bsleep", r"insomnia", r"\bpsqi\b", r"total wake time", r"\bnaps?\b", r"circadian", r"light exposure", r"bedtime", r"awake during the night"],
    ),
    ("associated_symptoms", "fatigue", "CAT_SYMPTOM_FATIGUE", [r"fatigue", r"\bmfi\b"]),
    ("associated_symptoms", "dizziness_vestibular", "CAT_SYMPTOM_DIZZINESS", [r"dizz", r"vertigo"]),
    (
        "associated_symptoms",
        "cognition",
        "CAT_SYMPTOM_COGNITION",
        [r"cogniti", r"neuropsycholog", r"\bmemory\b", r"executive function"],
    ),
    (
        "other",
        "not_an_outcome_measure",
        "CAT_OTHER_NOT_OUTCOME",
        [r"trauma", r"ksads", r"diagnosis using", r"effect sizes?", r"sample size", r"characteri[sz]e"],
    ),
    (
        "physical_performance",
        "physical_activity_behavior",
        "CAT_PHYSICAL_ACTIVITY",
        [r"\bsteps?\b", r"step counts?", r"accelerometer", r"sedentary", r"\bsitting\b", r"physical activity", r"activity level", r"\bcycling\b"],
    ),
    (
        "physical_performance",
        "strength_endurance",
        "CAT_PHYSICAL_STRENGTH",
        [
            r"strength", r"muscle (?:capacity|function|endurance|activation)", r"muscular", r"\bgrip\b",
            r"endurance", r"fitness", r"muscle power", r"biering", r"deadlift", r"repetitions", r"d[iy]namometry", r"cybex", r"flexor to extensor", r"multifidus",
            r"abdominal dynamic", r"\bemg\b", r"electromyograph", r"trunk muscle", r"conditioning",
            r"\bbalance\b(?! confidence| questionnaire)",
        ],
    ),
    (
        "physical_performance",
        "mobility_balance_gait",
        "CAT_PHYSICAL_MOBILITY",
        [
            r"\bwalk", r"\bgait\b", r"timed up", r"get-up", r"\bchair\b", r"\bstair", r"sit to stand", r"posturograph",
            r"\bpostur", r"proprioception", r"flexib", r"range of motion", r"\brom\b", r"schober", r"sit and reach",
            r"straight leg", r"lumbar (?:spine|flexion)", r"segmental movement", r"stiffness", r"joint position",
            r"craniovertebral", r"tragus", r"pelvic tilt", r"movement control", r"motor control", r"luomajoki",
            r"ergospirometry", r"physical function", r"flexion rotation", r"pressure biofeedback", r"muscle", r"mobility", r"time up and go", r"5rsts", r"range of movement", r"craniocervical flexion",
            r"limits of stability", r"instability", r"alignment",
        ],
    ),
]



def classify_outcome_category(
    measure: str | None,
    description: str | None,
    time_frame: str | None,
) -> OutcomeCategory:
    text = _text(measure, description, time_frame)

    # Feasibility and mechanistic rules read the measure NAME only: descriptions and time frames
    # of clinical outcomes mention "enrollment", "feasibility", "adverse" or "pressure pain"
    # without being one.
    measure_text = (measure or "").lower()
    for category, subcategory, rule_id, patterns in _FIRST_PASS_RULES:
        searched = measure_text if category in _MEASURE_ONLY_CATEGORIES else text
        if any(re.search(pattern, searched) for pattern in patterns):
            return OutcomeCategory(
                outcome_category=category,
                outcome_subcategory=subcategory,
                rule=rule_id,
            )

    # Second pass: only outcomes that matched nothing above reach it, so it can never move an
    # outcome out of the categories above. It reads the measure NAME only (descriptions carry
    # boilerplate such as "eligible participants" that causes false hits).
    for category, subcategory, rule_id, patterns in _SECOND_PASS_RULES:
        if any(re.search(pattern, measure_text) for pattern in patterns):
            return OutcomeCategory(
                outcome_category=category,
                outcome_subcategory=subcategory,
                rule=rule_id,
            )

    return OutcomeCategory(
        outcome_category="other",
        outcome_subcategory="other",
        rule="CAT_OTHER",
        review_flag=True,
    )
