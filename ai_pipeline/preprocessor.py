import re

FILLER_WORDS = [
    r'\bum\b', r'\buh\b', r'\ber\b', r'\bah\b',
    r'\bআঃ\b', r'\bউম্ম\b', r'\bমানে\b',
    r'\btum\b', r'\bha\b'  # common hindi/hinglish fillers
]

def remove_fillers(text: str) -> str:
    """Removes common conversational filler words."""
    result = text
    for pattern in FILLER_WORDS:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Clean up double spaces resulting from removal
    result = ' '.join(result.split())
    return result
