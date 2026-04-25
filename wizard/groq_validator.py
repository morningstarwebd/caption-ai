"""Groq API key validation and lightweight diagnosis helpers."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

MODELS_URL = "https://api.groq.com/openai/v1/models"
CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def validate_groq_key(api_key: str) -> tuple[bool, str]:
    """
    Validate a Groq API key.

    Returns (True, "") when valid, else (False, error_message).
    """
    try:
        key = (api_key or "").strip()
        if not key:
            return False, "API key is empty"

        req = urllib.request.Request(MODELS_URL, method="GET")
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return True, ""
            return False, f"Status: {resp.status}"
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            body = ""
        if body:
            return False, f"HTTP {exc.code}: {body}"
        return False, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return False, f"Network error: {exc.reason}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _local_fallback(lang: str, error_text: str) -> str:
    """Return a local diagnosis when remote diagnosis is unavailable."""
    error_text = (error_text or "").strip() or "Unknown error"

    if lang == "bn":
        return (
            f"সমস্যা: {error_text}. সাধারণত Key ভুল, নেটওয়ার্ক ব্লক, বা internet timeout হলে এটা হয়। "
            "Key আবার copy-paste করুন, internet/VPN check করুন, তারপর আবার Try করুন।"
        )
    if lang == "hi":
        return (
            f"समस्या: {error_text}. आमतौर पर यह गलत Key, नेटवर्क ब्लॉक, या timeout से होता है। "
            "Key दोबारा paste करें, internet/VPN जांचें, फिर दोबारा Try करें।"
        )
    return (
        f"Issue: {error_text}. This is usually caused by an invalid key, blocked network, or timeout. "
        "Paste the key again, check internet/VPN/firewall, and try once more."
    )


def diagnose_error_with_groq(api_key: str, error_text: str, lang: str) -> str:
    """
    Ask Groq for a short diagnosis in bn/en/hi.

    Falls back to a local message if the key is invalid or request fails.
    """
    try:
        key = (api_key or "").strip()
        if not key:
            return _local_fallback(lang, error_text)

        is_valid, _ = validate_groq_key(key)
        if not is_valid:
            return _local_fallback(lang, error_text)

        lang_instruction = {
            "bn": "বাংলায় উত্তর দাও। সহজ ভাষায়।",
            "en": "Reply in English. Keep it simple.",
            "hi": "हिंदी में जवाब दो। सरल भाषा में।",
        }
        instruction = lang_instruction.get(lang, lang_instruction["en"])

        prompt = (
            "A user is trying to install Caption AI on Windows.\n"
            f"This error occurred: {error_text}\n\n"
            f"{instruction}\n"
            "Tell them: 1) What went wrong 2) Exactly what to do to fix it. "
            "Keep it under 3 sentences."
        )

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You explain setup issues clearly and briefly."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 160,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(CHAT_URL, data=data, method="POST")
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="ignore")

        parsed = json.loads(body)
        choices = parsed.get("choices") or []
        if not choices:
            return _local_fallback(lang, error_text)

        message = (choices[0].get("message") or {}).get("content", "").strip()
        return message or _local_fallback(lang, error_text)
    except Exception:  # noqa: BLE001
        return _local_fallback(lang, error_text)
