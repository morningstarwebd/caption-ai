import logging
from .normalizer import normalize_for_scoring
from .config import ALIGN_WORD_THRESHOLD, ALIGN_LOW_RATIO_MAX

logger = logging.getLogger(__name__)

def validate_alignment(segments: list, adaptive_thresholds: dict) -> bool:
    """
    Validates the alignment results using adaptive thresholds 
    derived from audio quality estimation.
    """
    if not segments:
        return False
        
    align_avg_threshold = adaptive_thresholds.get('align_avg', 0.65)
    
    word_scores = []
    
    for seg in segments:
        words = seg.get('words', [])
        for w in words:
            score = w.get('score', 0.0)
            word_scores.append(score)
            
    if not word_scores:
        return False
        
    avg_score = sum(word_scores) / len(word_scores)
    low_scores = sum(1 for s in word_scores if s < ALIGN_WORD_THRESHOLD)
    low_ratio = low_scores / len(word_scores)
    
    logger.info(f"Alignment Validation: Avg={avg_score:.2f} (Target>{align_avg_threshold:.2f}), "
                f"Low Ratio={low_ratio*100:.1f}% (Target<{ALIGN_LOW_RATIO_MAX*100:.1f}%)")
                
    if avg_score >= align_avg_threshold and low_ratio <= ALIGN_LOW_RATIO_MAX:
        return True
        
    return False

def check_hallucination(raw_text: str, final_text: str) -> bool:
    """Verifies that the LLM hasn't hallucinated large amounts of text."""
    from .hallucination_guard import word_count_diff_check
    return word_count_diff_check(raw_text, final_text)
