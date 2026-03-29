import os
import logging
from groq import Groq
from .retry import with_retry
from .config import (
    RETRY_GROQ, WHISPER_PROMPTS,
    WEAK_SEGMENT_LOGPROB, WEAK_SEGMENT_NOSPEECH, RETRANSCRIBE_WEAK
)

logger = logging.getLogger(__name__)

LANGUAGE_HINTS = {
    "english": "en",
    "en": "en",
    "hindi": "hi",
    "hi": "hi",
    "bengali": "bn",
    "bn": "bn",
}


def _call_groq(client, audio_path: str, prompt: str, language_hint: str | None,
               temperature: float = 0.0) -> dict:
    """Single Groq Whisper call returning normalized dict."""
    with open(audio_path, "rb") as file:
        kwargs = {
            "file": (audio_path, file.read()),
            "model": "whisper-large-v3",
            "response_format": "verbose_json",
            "timestamp_granularities": ["word", "segment"],
            "temperature": temperature,
        }
        if prompt:
            kwargs["prompt"] = prompt
        if language_hint:
            kwargs["language"] = language_hint

        transcription = client.audio.transcriptions.create(**kwargs)

    if hasattr(transcription, "model_dump"):
        payload = transcription.model_dump()
    elif isinstance(transcription, dict):
        payload = transcription
    else:
        payload = {"text": str(transcription).strip()}

    return {
        "text": (payload.get("text") or "").strip(),
        "language": payload.get("language"),
        "duration": payload.get("duration"),
        "segments": payload.get("segments") or [],
        "words": payload.get("words") or [],
    }


def _has_weak_segments(result: dict) -> bool:
    """Check if any segment has low confidence or high no-speech probability."""
    for seg in result.get("segments", []):
        logprob = seg.get("avg_logprob", 0.0)
        nospeech = seg.get("no_speech_prob", 0.0)
        if logprob is not None and logprob < WEAK_SEGMENT_LOGPROB:
            return True
        if nospeech is not None and nospeech > WEAK_SEGMENT_NOSPEECH:
            return True
    return False


def _merge_word_lists(primary: list, secondary: list) -> list:
    """Combine word lists, taking the longer/richer version."""
    if not primary:
        return secondary
    if not secondary:
        return primary
    # Pick whichever returned more words — more words = more recall
    return primary if len(primary) >= len(secondary) else secondary


@with_retry(max_retries=RETRY_GROQ)
def transcribe_chunk_with_retry(audio_path: str, language: str = "") -> dict:
    """Groq Whisper with double-pass on weak segments for maximum recall."""
    api_key = os.environ.get("GROQ_API_KEY", "dummy")
    client = Groq(api_key=api_key)

    prompt = WHISPER_PROMPTS.get(language, "")
    language_hint = LANGUAGE_HINTS.get(language)

    # Pass 1: deterministic decode (temperature=0)
    result = _call_groq(client, audio_path, prompt, language_hint, temperature=0.0)

    # Pass 2: if weak segments detected, re-transcribe with slight temperature
    # to catch words the deterministic pass missed
    if RETRANSCRIBE_WEAK and _has_weak_segments(result):
        logger.info(f"Weak segments detected in {audio_path}, running rescue pass...")
        try:
            rescue = _call_groq(client, audio_path, prompt, language_hint, temperature=0.2)
            # Take whichever has more text (more recall)
            if len(rescue["text"].split()) > len(result["text"].split()):
                logger.info(f"Rescue pass recovered more words: {len(rescue['text'].split())} vs {len(result['text'].split())}")
                result["text"] = rescue["text"]
                result["segments"] = rescue["segments"]
            # Always merge word lists for max coverage
            result["words"] = _merge_word_lists(result["words"], rescue["words"])
        except Exception as e:
            logger.warning(f"Rescue pass failed: {e}. Using first pass only.")

    return result
