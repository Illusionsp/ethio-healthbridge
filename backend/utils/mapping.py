import difflib

AMHARIC_TO_MEDICAL = {
    "ራስ ምታት": "headache",
    "ትኩሳት": "fever",
    "ሳል": "cough",
    "ማስመለስ": "vomiting",
    "ተቅማጥ": "diarrhea",
    "ደረት ህመም": "chest pain",
    "የመተንፈስ ችግር": "shortness of breath / dyspnea",
    "ድንገተኛ": "emergency",
    "መድሃኒት": "medicine",
    "የሆድ ህመም": "abdominal pain",
    "ደም": "blood",
    "ድካም": "fatigue",
    "የቆዳ ሽፍታ": "rash",
    "የመገጣጠሚያ ህመም": "joint pain"
}

def translate_to_medical(amharic_term: str) -> str:
    return AMHARIC_TO_MEDICAL.get(amharic_term, "Unknown term")

def extract_known_symptoms(text: str) -> list[str]:
    found = []
    text_words = text.replace("፣", " ").replace("።", " ").split()
    
    for k in AMHARIC_TO_MEDICAL.keys():
        if k in text:
            if k not in found:
                found.append(k)
            continue
            
        key_words = k.split()
        for kw in key_words:
            matches = difflib.get_close_matches(kw, text_words, n=1, cutoff=0.8)
            if matches and k not in found:
                found.append(k)
                
    return found