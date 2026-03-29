from typing import List, Tuple
import logging
from .audio import Chunk
from .config import MERGE_MIN_OVERLAP_WORDS
from .normalizer import normalize_for_scoring

logger = logging.getLogger(__name__)


def _find_overlap_word_count(previous_text: str, current_text: str) -> int:
    """
    Conservative overlap detection: only dedup when we have an EXACT
    sequence match of at least MERGE_MIN_OVERLAP_WORDS consecutive words.
    Also caps overlap at 50% of the shorter text to prevent over-aggressive dedup.
    """
    prev_words = previous_text.split()
    curr_words = current_text.split()

    if len(prev_words) < MERGE_MIN_OVERLAP_WORDS or len(curr_words) < MERGE_MIN_OVERLAP_WORDS:
        return 0

    # Cap: never dedup more than 50% of the current chunk's words
    max_overlap = min(len(prev_words), len(curr_words), len(curr_words) // 2 + 1)

    if max_overlap < MERGE_MIN_OVERLAP_WORDS:
        return 0

    normalized_prev = [normalize_for_scoring(word) for word in prev_words]
    normalized_curr = [normalize_for_scoring(word) for word in curr_words]

    for overlap in range(max_overlap, MERGE_MIN_OVERLAP_WORDS - 1, -1):
        if normalized_prev[-overlap:] == normalized_curr[:overlap]:
            logger.debug(f"Overlap dedup: removing {overlap} repeated words")
            return overlap

    return 0

def merge_chunks(processed_chunks: List[Chunk]) -> Tuple[str, list]:
    """
    Order-Safe Parallel Merge: 
    Merges transcriptions with conservative deduplication. Guaranteed order.
    Never drops unique content — only removes proven duplicates.
    """
    if not processed_chunks:
        return "", []
        
    # Sort processed chunks by their sequential index to guarantee order
    sorted_chunks = sorted(processed_chunks, key=lambda c: c.index)
    
    full_text = ""
    merged_segments = []
    
    for chunk in sorted_chunks:
        text = chunk.final_text or ""
        
        if not text.strip():
            # Even empty chunks: if raw_text exists, use it (no-drop policy)
            raw = getattr(chunk, 'raw_text', '') or ''
            if raw.strip():
                text = raw.strip()
                logger.info(f"Chunk {chunk.index}: rescued empty final_text with raw_text ({len(raw.split())} words)")
            else:
                continue
            
        # Conservative overlap deduplication
        if full_text:
            overlap_words = _find_overlap_word_count(full_text, text)
            if overlap_words:
                removed = text.split()[:overlap_words]
                text = ' '.join(text.split()[overlap_words:])
                logger.debug(f"Chunk {chunk.index}: deduped {overlap_words} words: {removed}")
        
        if text.strip():
            merged_segments.append({
                "text": text.strip(),
                "start": chunk.start_time,
                "end": chunk.end_time
            })
            full_text += (" " if full_text else "") + text.strip()
            
    return full_text, merged_segments
