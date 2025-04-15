from typing import Dict, List

GENDER_CHOICES: List[str] = ["male", "female"]

RACE_CHOICES: List[str] = ["black", "caucasian"]

ETHNICITY_CHOICES: List[str] = ["african american", "asian", "hispanic"]

TRUST_GAME_CHOICES: List[str] = ["prisoners_dilemma", "hiring_game", "investment_game"]

PERSONA_CHOICES: List[Dict[str, str]] = [
    {"gender": "male", "race": None, "ethnicity": None, "persona": "gender is male"},
    {"gender": "female", "race": None, "ethnicity": None, "persona": "gender is female"},
    {"gender": None, "race": "black", "ethnicity": None, "persona": "race is black"},
    {"gender": None, "race": "caucasian", "ethnicity": None, "persona": "race is caucasian"},
    {"gender": None, "race": None, "ethnicity": "african american", "persona": "ethnicity is african american"},
    {"gender": None, "race": None, "ethnicity": "asian", "persona": "ethnicity is asian"},
    {"gender": None, "race": None, "ethnicity": "hispanic", "persona": "ethnicity is hispanic"},
    {"gender": "male", "race": "black", "ethnicity": None, "persona": "gender is male, race is black"},
    {"gender": "male", "race": "caucasian", "ethnicity": None, "persona": "gender is male, race is caucasian"},
    {"gender": "female", "race": "black", "ethnicity": None, "persona": "gender is female, race is black"},
    {"gender": "female", "race": "caucasian", "ethnicity": None, "persona": "gender is female, race is caucasian"},
    {"gender": "male", "race": None, "ethnicity": "african american", "persona": "gender is male, ethnicity is african american"},
    {"gender": "male", "race": None, "ethnicity": "asian", "persona": "gender is male, ethnicity is asian"},
    {"gender": "male", "race": None, "ethnicity": "hispanic", "persona": "gender is male, ethnicity is hispanic"},
    {"gender": "female", "race": None, "ethnicity": "african american", "persona": "gender is female, ethnicity is african american"},
    {"gender": "female", "race": None, "ethnicity": "asian", "persona": "gender is female, ethnicity is asian"},
    {"gender": "female", "race": None, "ethnicity": "hispanic", "persona": "gender is female, ethnicity is hispanic"},
    {"gender": None, "race": "black", "ethnicity": "african american", "persona": "race is black, ethnicity is african american"},
    {"gender": None, "race": "caucasian", "ethnicity": "asian", "persona": "race is caucasian, ethnicity is asian"},
    {"gender": None, "race": "caucasian", "ethnicity": "hispanic", "persona": "race is caucasian, ethnicity is hispanic"},
    {"gender": "male", "race": "black", "ethnicity": "african american", "persona": "gender is male, race is black, ethnicity is african american"},
    {"gender": "male", "race": "caucasian", "ethnicity": "asian", "persona": "gender is male, race is caucasian, ethnicity is asian"},
    {"gender": "male", "race": "caucasian", "ethnicity": "hispanic", "persona": "gender is male, race is caucasian, ethnicity is hispanic"},
    {"gender": "female", "race": "black", "ethnicity": "african american", "persona": "gender is female, race is black, ethnicity is african american"},
    {"gender": "female", "race": "caucasian", "ethnicity": "asian", "persona": "gender is female, race is caucasian, ethnicity is asian"},
    {"gender": "female", "race": "caucasian", "ethnicity": "hispanic", "persona": "gender is female, race is caucasian, ethnicity is hispanic"}
]