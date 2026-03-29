from spellchecker import SpellChecker
from typing import Optional

# Initialize English spellchecker
spell = SpellChecker(language='en')

def lightweight_lm_check(text: str, lang_hint: Optional[str] = None) -> float:
    """
    Fast pre-check to reject obvious garbage text before heavy embedding processing.
    Returns score 0.0 - 1.0 (higher means better/real text).
    """
    if not text or not text.strip():
        return 0.0
        
    words = text.split()
    if not words:
        return 0.0

    # Only run spell check for English words since Bengali/Hindi 
    # dictionaries aren't built-in to pyspellchecker by default.
    # For Hinglish/Bengali/Hindi, we rely on basic letter-ratio checks.
    
    if lang_hint == 'english':
        correct = sum(1 for w in words if spell.correction(w) == w)
        spell_score = correct / len(words)
        return spell_score
    else:
        # Generic heuristic: check proportion of alphanumeric + basic punctuation
        # (reject purely numeric strings or heavily garbled strings)
        alnum_chars = sum(1 for c in text if c.isalnum() or c.isspace())
        ratio = alnum_chars / len(text)
        
        # Penalize if it's purely digits or mostly special chars
        if text.replace(" ", "").isdigit():
            return 0.2
            
        return ratio
