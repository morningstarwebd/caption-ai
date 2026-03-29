import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def with_retry(max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0, exceptions=(Exception,)):
    """
    Decorator for adding exponential backoff retry logic to API calls.
    Used for Groq LLM, Transcription, and Alignment phases.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            delay = base_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts. Last error: {e}")
                        raise
                        
                    logger.warning(f"Attempt {retries}/{max_retries} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor
                    
        return wrapper
    return decorator
