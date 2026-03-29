import logging
from .lang_detector import detect_language
from .config import CONFIDENCE_HINDI, CONFIDENCE_ENGLISH, CONFIDENCE_HINGLISH

logger = logging.getLogger(__name__)

def determine_confidence_threshold(text: str, adaptive_thresholds: dict) -> float:
    """
    13. Language-Aware Confidence Thresholding
    Dynamically adjusts the required confidence score based on the detected language
    and the overall audio quality.
    """
    lang = detect_language(text)
    
    # Base thresholds
    if lang == "hi" or lang == "bn":
        base_threshold = CONFIDENCE_HINDI
    elif lang == "en":
        base_threshold = CONFIDENCE_ENGLISH
    else: # Hinglish or mixed
        base_threshold = CONFIDENCE_HINGLISH
        
    # Apply global audio quality modifier from adaptive engine
    # Delta is usually negative if audio is noisy, so threshold is lowered
    final_threshold = max(0.4, base_threshold + adaptive_thresholds.get('confidence_delta', 0.0))
    
    logger.info(f"Confidence Threshold: {final_threshold:.2f} (Lang: {lang})")
    return final_threshold
