import re
from .config import SENTENCE_MAX_WORDS, SENTENCE_MAX_WORDS_STRICT

def split_at_pauses(sentences: list[str], pauses: list, min_pause: float = 0.4) -> list[str]:
    """Splits sentences further if there's a significant prosody pause."""
    # Simplified placeholder logic since true prosody mapping requires aligned words before splitting
    # In a real implementation this would map pause timestamps to the text sequence
    return sentences

def split_sentences_v2(text: str, pauses: list = None, strict: bool = False) -> list[str]:
    """
    Sentence Splitter v2: 
    1. Punctuation split
    2. Prosody hints (if provided)
    3. Tighter word count fallback (10-12 words)
    """
    max_words = SENTENCE_MAX_WORDS_STRICT if strict else SENTENCE_MAX_WORDS
    
    # 1. Punctuation split (Multi-language awareness)
    # Bengali Danda '।' (U+0964) and Double Danda '॥' (U+0965)
    raw = re.split(r'[.\!?।॥]+', text)
    sentences = [s.strip() for s in raw if s.strip()]
    
    # 2. Prosody split
    if pauses:
        sentences = split_at_pauses(sentences, pauses, min_pause=0.4)
        
    # 3. Max-word fallback (Safety net)
    result = []
    for s in sentences:
        words = s.split()
        if len(words) <= max_words:
            result.append(s)
        else:
            # Chunk long sentences forcibly
            for i in range(0, len(words), max_words):
                result.append(' '.join(words[i:i+max_words]))
                
    return result
