import logging
from .config import MAX_WORD_DIFF_RATIO

logger = logging.getLogger(__name__)

def word_count_diff_check(raw_text: str, refined_text: str) -> bool:
    """
    Checks if the word count difference between raw and refined text
    exceeds reasonable bounds, indicating a potential hallucination.
    """
    raw_words = len(raw_text.split())
    refined_words = len(refined_text.split())
    
    if raw_words == 0 and refined_words > 0:
        return False # Definitely hallucinated if raw had nothing
    elif raw_words == 0:
        return True # Both empty, that's fine
        
    diff_ratio = abs(raw_words - refined_words) / raw_words
    
    if diff_ratio > MAX_WORD_DIFF_RATIO:
        logger.warning(f"Hallucination Guard Triggered! Raw count: {raw_words}, Refined count: {refined_words}, Ratio: {diff_ratio:.2f}")
        return False
        
    return True

def repeat_ngram_check(text: str, n=3, max_repeats=3) -> bool:
    """Catches classic Whisper hallucination where it repeats the same phrase over and over."""
    words = text.split()
    if len(words) < n * max_repeats:
        return True
        
    # Simple check for exactly repeated sequences
    for i in range(len(words) - n):
        ngram = " ".join(words[i:i+n])
        count = text.count(ngram)
        if count > max_repeats:
            logger.warning(f"Hallucination Guard Triggered! Repeated ngram '{ngram}' found {count} times.")
            return False
            
    return True
