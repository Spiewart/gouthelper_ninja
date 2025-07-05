from .choices import MHTypes

CV_DISEASES = [
    MHTypes.ANGINA,  # Angina
    MHTypes.CAD,  # Coronary Artery Disease
    MHTypes.CHF,  # Congestive Heart Failure
    MHTypes.HEARTATTACK,  # Heart Attack
    # Hypertension is ommitted because it is not used for some prediction models.
    # It can be added as needed in other methods.
    MHTypes.STROKE,  # Stroke
    MHTypes.PAD,  # Peripheral Vascular Disease
]

GOALURATE_MEDHISTORYS: list[MHTypes] = [
    MHTypes.EROSIONS,  # Erosions
    MHTypes.TOPHI,  # Tophi
]

FLARE_MEDHISTORYS: list[MHTypes] = [
    MHTypes.ANGINA,  # Angina
    MHTypes.CAD,  # Coronary Artery Disease
    MHTypes.CHF,  # Congestive Heart Failure
    MHTypes.CKD,  # Chronic Kidney Disease
    MHTypes.GOUT,  # Gout
    MHTypes.HEARTATTACK,  # Heart Attack
    MHTypes.HYPERTENSION,  # Hypertension
    MHTypes.MENOPAUSE,  # Post-Menopausal
    MHTypes.PAD,  # Peripheral Vascular Disease
    MHTypes.STROKE,  # Stroke
]

FLAREAID_MEDHISTORYS: list[MHTypes] = [
    MHTypes.ANGINA,  # Angina
    MHTypes.ANTICOAGULATION,  # Anticoagulation
    MHTypes.BLEED,  # History of Serious Bleeding
    MHTypes.CAD,  # Coronary Artery Disease
    MHTypes.CHF,  # Congestive Heart Failure
    MHTypes.CKD,  # Chronic Kidney Disease
    MHTypes.COLCHICINEINTERACTION,  # Colchicine Interaction
    MHTypes.DIABETES,  # Diabetes
    MHTypes.GASTRICBYPASS,  # Gastric Bypass
    MHTypes.HEARTATTACK,  # Heart Attack
    MHTypes.HYPERTENSION,  # Hypertension
    MHTypes.IBD,  # Inflammatory Bowel Disease
    MHTypes.ORGANTRANSPLANT,  # Organ Transplant
    MHTypes.PUD,  # Peptic Ulcer Disease
    MHTypes.PAD,  # Peripheral Vascular Disease
    MHTypes.STROKE,  # Stroke
]

OTHER_NSAID_CONTRAS: list[MHTypes] = [
    MHTypes.ANTICOAGULATION,  # Anticoagulation
    MHTypes.BLEED,  # History of Serious Bleeding
    MHTypes.GASTRICBYPASS,  # Gastric Bypass
    MHTypes.IBD,  # Inflammatory Bowel Disease
    MHTypes.PUD,  # Peptic Ulcer Disease
]

PPX_MEDHISTORYS: list[MHTypes] = [
    MHTypes.GOUT,  # Gout
]

PPXAID_MEDHISTORYS: list[MHTypes] = [
    MHTypes.ANGINA,  # Angina
    MHTypes.ANTICOAGULATION,  # Anticoagulation
    MHTypes.BLEED,  # History of Serious Bleeding
    MHTypes.CAD,  # Coronary Artery Disease
    MHTypes.CHF,  # Congestive Heart Failure
    MHTypes.CKD,  # Chronic Kidney Disease
    MHTypes.COLCHICINEINTERACTION,  # Colchicine Interaction
    MHTypes.DIABETES,  # Diabetes
    MHTypes.GASTRICBYPASS,  # Gastric Bypass
    MHTypes.HEARTATTACK,  # Heart Attack
    MHTypes.HYPERTENSION,  # Hypertension
    MHTypes.IBD,  # Inflammatory Bowel Disease
    MHTypes.ORGANTRANSPLANT,  # Organ Transplant
    MHTypes.PUD,  # Peptic Ulcer Disease
    MHTypes.PAD,  # Peripheral Vascular Disease
    MHTypes.STROKE,  # Stroke
]

ULT_MEDHISTORYS: list[MHTypes] = [
    MHTypes.CKD,  # Chronic Kidney Disease
    MHTypes.EROSIONS,  # Erosions
    MHTypes.HYPERURICEMIA,  # Hyperuricemia
    MHTypes.TOPHI,  # Tophi
    MHTypes.URATESTONES,  # Urate Stones
]

ULTAID_MEDHISTORYS: list[MHTypes] = [
    MHTypes.ANGINA,  # Angina
    MHTypes.CAD,  # Coronary Artery Disease
    MHTypes.CHF,  # Congestive Heart Failure
    MHTypes.CKD,  # Chronic Kidney Disease
    MHTypes.HEARTATTACK,  # Heart Attack
    MHTypes.HEPATITIS,  # Hepatitis or Cirrhosis
    MHTypes.ORGANTRANSPLANT,  # Organ Transplant
    MHTypes.PAD,  # Peripheral Vascular Disease
    MHTypes.STROKE,  # Stroke
    MHTypes.URATESTONES,  # Urate Stones
    MHTypes.XOIINTERACTION,  # XOI Interaction
]
