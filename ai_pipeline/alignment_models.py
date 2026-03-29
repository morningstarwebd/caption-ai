import logging
import whisperx
import torch

logger = logging.getLogger(__name__)

_MODEL_CACHE = {}

def get_alignment_model(model_id: str, device: str = "cpu"):
    """Loads and caches a WhisperX alignment model."""
    if model_id in _MODEL_CACHE:
        return _MODEL_CACHE[model_id]

    try:
        model, metadata = whisperx.load_align_model(
            language_code="en" if "960H" in model_id else "hi",
            device=device,
            model_name=None if "960H" in model_id else model_id
        )
        _MODEL_CACHE[model_id] = (model, metadata)
        return model, metadata
    except Exception as e:
        logger.error(f"Failed to load alignment model {model_id}: {e}")
        if "960H" not in model_id:
            logger.warning("Falling back to English alignment model (WAV2VEC2_ASR_BASE_960H).")
            try:
                model, metadata = whisperx.load_align_model(
                    language_code="en",
                    device=device,
                    model_name=None
                )
                _MODEL_CACHE[model_id] = (model, metadata)
                return model, metadata
            except Exception as e2:
                logger.error(f"Fallback English alignment also failed: {e2}")
                raise
        raise
