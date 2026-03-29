from collections import Counter
from typing import List

def is_english(token: str) -> bool:
    # Check if mostly ascii characters
    return all(ord(c) < 128 for c in token)

def is_hindi(token: str) -> bool:
    # Devanagari block: 0x0900 - 0x097F
    return any(0x0900 <= ord(c) <= 0x097F for c in token)

def is_bengali(token: str) -> bool:
    # Bengali block: 0x0980 - 0x09FF
    return any(0x0980 <= ord(c) <= 0x09FF for c in token)

def detect_language(tokens: List[str]) -> str:
    en = sum(1 for t in tokens if is_english(t))
    hi = sum(1 for t in tokens if is_hindi(t))
    bn = sum(1 for t in tokens if is_bengali(t))
    
    # Hinglish detection logic
    # If both English and Hindi are present in significant amounts
    if en > 0 and hi > 0 and (en / len(tokens) > 0.1) and (hi / len(tokens) > 0.1):
        return 'hinglish'  # Token mix ratio
        
    counts = [('english', en), ('hindi', hi), ('bengali', bn)]
    return max(counts, key=lambda x: x[1])[0]

def detect_language_majority(chunks_tokens: List[List[str]]) -> str:
    if not chunks_tokens:
        return 'english'
        
    votes = [detect_language(tokens) for tokens in chunks_tokens if tokens]
    if not votes:
        return 'english'
        
    return Counter(votes).most_common(1)[0][0]
