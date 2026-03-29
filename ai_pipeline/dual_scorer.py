from sentence_transformers import SentenceTransformer
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
import torch
import torch.nn.functional as F

from .config import SEMANTIC_WEIGHT, KEYWORD_WEIGHT, EMBED_BATCH_SIZE
from .normalizer import normalize_for_scoring
import hashlib

# Load a lightweight, multilingual embedding model globally
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
EMBED_CACHE = {}

def get_embedding(text: str):
    """Hash-based embedding cache."""
    key = hashlib.md5(text.encode('utf-8')).hexdigest()
    if key in EMBED_CACHE:
        return EMBED_CACHE[key]
    
    emb = embed_model.encode(text, convert_to_tensor=True)
    EMBED_CACHE[key] = emb
    return emb

def batch_encode(texts: list[str], batch_size: int = EMBED_BATCH_SIZE) -> list:
    """Batch encoding for performance."""
    if not texts: return []
    return embed_model.encode(texts, batch_size=batch_size, convert_to_tensor=True)

def semantic_similarity(raw: str, corrected: str) -> float:
    """Computes cosine similarity between two sentences."""
    emb1 = get_embedding(raw)
    emb2 = get_embedding(corrected)
    # Cosine similarity
    cos_sim = F.cosine_similarity(emb1.unsqueeze(0), emb2.unsqueeze(0)).item()
    return max(0.0, cos_sim)  # Clamped to 0-1

def keyword_retention(raw: str, corrected: str) -> float:
    """Measures keyword preservation via simple Jaccard index."""
    raw_words = set(raw.split())
    corr_words = set(corrected.split())
    
    if not raw_words or not corr_words:
        return 0.0
        
    intersection = raw_words.intersection(corr_words)
    union = raw_words.union(corr_words)
    return len(intersection) / len(union)

def compute_dual_score(raw: str, corrected: str) -> float:
    """Computes the combined score using normalized text."""
    # Normalize before scoring! (PRD v4.3 Requirement)
    norm_raw = normalize_for_scoring(raw)
    norm_corr = normalize_for_scoring(corrected)
    
    if not norm_raw or not norm_corr:
        return 0.0
        
    semantic = semantic_similarity(norm_raw, norm_corr)
    keyword = keyword_retention(norm_raw, norm_corr)
    
    return (semantic * SEMANTIC_WEIGHT) + (keyword * KEYWORD_WEIGHT)
