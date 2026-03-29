import re

# Standard mapping for common numerals 
NUMERAL_MAP = {
    '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
    '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
}

def normalize_numerals(text: str) -> str:
    """Converts individual digits to words."""
    return re.sub(r'\b(\d)\b', lambda m: NUMERAL_MAP.get(m.group(1), m.group(1)), text)

def normalize_text(text: str) -> str:
    """Normalizes text by removing punctuation, lowercasing, and collapsing whitespace."""
    if not text:
        return ""
    
    t = text.lower()
    # Strip punctuation but keep word characters and whitespace
    t = re.sub(r'[^\w\s]', ' ', t)
    # Collapse multiple whitespace characters into a single space
    t = ' '.join(t.split())
    
    return t

def normalize_for_scoring(text: str) -> str:
    """Combined normalization for dual scorer"""
    t = normalize_numerals(text)
    return normalize_text(t)
