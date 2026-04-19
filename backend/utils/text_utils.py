import re

def clean_latin_script(text: str) -> str:
    """
    Hard-enforcement of zero Latin script.
    1. Strips any parentheticals containing Latin characters.
    2. Strips any remaining standalone Latin characters (A-Z).
    3. Trims whitespace.
    """
    if not text:
        return ""
        
    # Remove (English text) or (Amharic እና English)
    # This regex looks for parentheses containing at least one Latin character
    cleaned = re.sub(r'\s*\([^)]*[a-zA-Z][^)]*\)', '', text)
    
    # Also remove any standalone Latin words/letters if they somehow leaked
    cleaned = re.sub(r'[a-zA-Z]+', '', cleaned)
    
    # Replace common Latin units if they appear outside parentheses
    # (Optional, but good for mg/ml)
    # Actually the regex above handles them if they are letters.
    
    return cleaned.strip()
