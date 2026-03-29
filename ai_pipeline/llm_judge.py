import os
from .config import LLM_MODE, RETRY_LLM
from .retry import with_retry

# Use Groq for LLM as well, since groq library is already installed
# and it provides fast Llama models suitable for this.
# client will be initialized lazily

PROMPTS = {
    'normal': "You are a helpful AI that strictly fixes grammar, spelling, and translation errors in a raw transcription chunk. DO NOT rewrite completely. Fix broken Hinglish.",
    'critical': "You are an expert caption reviewer. Fix all grammar strictly without changing word count significantly.",
    'consistency': '''You are a text consistency checker. DO NOT rewrite or rephrase any sentence. DO NOT add or remove any words. ONLY ensure consistent spelling of proper nouns, names, and technical terms across all sentences. Return the text exactly as given, with only spelling consistency fixes applied.'''
}

HINGLISH_INSTRUCTION = """
CRITICAL INSTRUCTION: The user wants "Hinglish" output. This means:
- The LANGUAGE is Hindi/Hinglish (spoken Hindi)  
- But it must be written in ROMAN/ENGLISH SCRIPT (Latin alphabet), NOT Devanagari
- Convert ALL Hindi/Devanagari text to Romanized Hindi
- Example: "मैं आज क्या कर रहा हूं" → "main aaj kya kar raha hoon"
- Example: "यह बहुत अच्छा है" → "yeh bahut accha hai"
- Keep English words as-is, only transliterate Hindi words to Roman script
- Use common Hinglish spelling conventions (e.g. "kya", "hai", "nahi", "accha")
- DO NOT use Devanagari script at all in your output
"""

@with_retry(max_retries=RETRY_LLM)
def refine_transcript(text: str, detected_lang: str = "en", mode: str = 'normal', target_lang: str = None) -> str:
    """Sends the chunk to LLM for correction. If target_lang is 'hinglish', transliterates to Roman script."""
    sys_prompt = PROMPTS.get(LLM_MODE if mode != 'consistency' else mode, PROMPTS['normal'])
    sys_prompt += f" The detected language is {detected_lang}."
    
    # Add Hinglish transliteration instruction
    if target_lang == 'hinglish':
        sys_prompt += HINGLISH_INSTRUCTION
    
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY", os.environ.get("LLM_API_KEY", "dummy"))
    client = Groq(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Successor to decommissioned llama3-8b-8192
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.1,  # Low temp for deterministic edits
    )
    return completion.choices[0].message.content.strip()

@with_retry(max_retries=RETRY_LLM)
def global_consistency_pass(full_transcript: str, target_lang: str = None) -> str:
    """
    1-pass LLM to normalize proper nouns and terms across the entire transcript.
    If target_lang is 'hinglish', also ensures Roman transliteration.
    """
    return refine_transcript(full_transcript, mode='consistency', target_lang=target_lang)
