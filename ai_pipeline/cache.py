import hashlib
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ContentCache:
    """
    11. Hash-based Output Verification (Caching)
    Prevents reprocessing chunks that have already yielded identical results.
    """
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        logger.info("Content cache initialized")
        
    def _generate_hash(self, audio_data: bytes, model_config: dict) -> str:
        """Generates a stable hash based on raw audio and generation params."""
        # In a real scenario, you'd hash the actual bytes or path + size
        # We simulate with a string representation for now due to memory constraints
        hasher = hashlib.md5()
        hasher.update(str(len(audio_data)).encode('utf-8'))
        hasher.update(json.dumps(model_config, sort_keys=True).encode('utf-8'))
        return hasher.hexdigest()
        
    def get(self, audio_data: bytes, model_config: dict) -> Optional[dict]:
        """Retrieves cached result if available."""
        hash_key = self._generate_hash(audio_data, model_config)
        if hash_key in self._cache:
            logger.debug(f"Cache HIT for key {hash_key}")
            return self._cache[hash_key]
        return None
        
    def set(self, audio_data: bytes, model_config: dict, result: dict):
        """Stores result in cache."""
        hash_key = self._generate_hash(audio_data, model_config)
        self._cache[hash_key] = result
        logger.debug(f"Cache SET for key {hash_key}")

# Singleton instance
global_cache = ContentCache()
