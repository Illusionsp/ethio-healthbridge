import difflib

# Amharic symptom terms -> English medical terms
AMHARIC_TO_MEDICAL = {
    "ራስ ምታት": "headache",
    "ትኩሳት": "fever",
    "ሳል": "cough",
    "ማስመለስ": "vomiting",
    "ተቅማጥ": "diarrhea",
    "ደረት ህመም": "chest pain",
    "የመተንፈስ ችግር": "shortness of breath",
    "ድንገተኛ": "emergency",
    "መድሃኒት": "medicine",
    "የሆድ ህመም": "abdominal pain",
    "ደም": "blood",
    "ድካም": "fatigue",
    "የቆዳ ሽፍታ": "rash",
    "የመገጣጠሚያ ህመም": "joint pain",
    "ምች": "fever / viral infection",
    "ውጋት": "sharp chest or body pain",
    "ቁርጠት": "abdominal cramps",
    "ማዞር": "dizziness",
    "ቁርጥማት": "joint pain / bone aches",
    "ብርድ ብርድ ማለት": "chills",
}

# Afaan Oromoo symptom terms -> English medical terms
OROMOO_TO_MEDICAL = {
    "dhukkuba mataa": "headache",
    "ho'a qaamaa": "fever",
    "qufaa": "cough",
    "hanqaaquu": "vomiting",
    "garaa kaasaa": "diarrhea",
    "dhukkuba laphee": "chest pain",
    "rakkoo hafuura": "shortness of breath",
    "dhiiga": "blood",
    "dadhabina": "fatigue",
    "dhukkuba miila": "leg pain",
    "dhukkuba garaa": "abdominal pain",
    "qurxummii": "malaria / fever with chills",
    "hargansa": "breathing difficulty",
    "dhukkuba lafaa": "bone pain",
}

# Tigrinya symptom terms -> English medical terms
TIGRINYA_TO_MEDICAL = {
    "ቃንዛ ርእሲ": "headache",
    "ረስኒ": "fever",
    "ሳዕሪ": "cough",
    "ምትፋእ": "vomiting",
    "ተምሲ": "diarrhea",
    "ቃንዛ ደረት": "chest pain",
    "ጸገም ምስትንፋስ": "shortness of breath",
    "ደም": "blood",
    "ድኻምነት": "fatigue",
    "ቃንዛ ሆድ": "abdominal pain",
    "ምዝዛም": "dizziness",
    "ቁሪ ቁሪ": "chills",
}

# Combined lookup
ALL_SYMPTOM_MAPS = {
    **AMHARIC_TO_MEDICAL,
    **OROMOO_TO_MEDICAL,
    **TIGRINYA_TO_MEDICAL,
}


def translate_to_medical(term: str) -> str:
    return ALL_SYMPTOM_MAPS.get(term, "Unknown term")


def extract_known_symptoms(text: str) -> list:
    found = []
    text_clean = text.replace("፣", " ").replace("።", " ")
    text_words = text_clean.split()

    for k in ALL_SYMPTOM_MAPS.keys():
        if k in text_clean:
            if k not in found:
                found.append(k)
            continue

        key_words = k.split()
        for kw in key_words:
            matches = difflib.get_close_matches(kw, text_words, n=1, cutoff=0.8)
            if matches and k not in found:
                found.append(k)

    return found
