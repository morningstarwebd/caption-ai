from .config import DRIFT_MIN_GAP
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def clamp_alignment_drift(words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enforces a minimum gap between consecutive words to prevent visual overlaps
    in the renderer. WhisperX sometimes produces overlapping timestamps.
    
    SAFETY: Never pushes start past end, never creates gaps > 0.15s,
    never drops words. Preserves every single word.
    """
    if not words:
        return words
        
    clamped_words = [words[0].copy()]
    
    for i in range(1, len(words)):
        current_word = words[i].copy()
        prev_word = clamped_words[i-1]
        
        if 'start' not in current_word or 'end' not in current_word:
            # Missing timestamps — keep word as-is, don't discard
            clamped_words.append(current_word)
            continue
            
        if 'end' not in prev_word:
            clamped_words.append(current_word)
            continue
        
        overlap = prev_word['end'] + DRIFT_MIN_GAP - current_word['start']
        
        if overlap > 0:
            # Small overlap: just nudge start forward
            current_word['start'] = round(prev_word['end'] + DRIFT_MIN_GAP, 3)
            
            # SAFETY: Ensure start never exceeds end
            if current_word['start'] >= current_word['end']:
                # Give the word a minimum 80ms duration starting right after prev
                current_word['start'] = round(prev_word['end'] + DRIFT_MIN_GAP, 3)
                current_word['end'] = round(current_word['start'] + 0.08, 3)
                    
        clamped_words.append(current_word)
        
    return clamped_words
