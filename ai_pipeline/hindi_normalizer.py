"""
hindi_normalizer.py — Caption AI
Deterministic 3-pass correction for Hindi/Hinglish text.
Runs BEFORE the LLM Judge to reduce hallucination and improve consistency.
"""

import logging

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# Pass 1: Devanagari → Hinglish transliteration (200+ entries)
# ──────────────────────────────────────────────────────────────────
HINDI_TO_HINGLISH: dict[str, str] = {
    "नहीं": "nahi",
    "बहुत": "bahut",
    "क्योंकि": "kyunki",
    "ज्यादा": "zyada",
    "है": "hai",
    "और": "aur",
    "में": "mein",
    "का": "ka",
    "की": "ki",
    "को": "ko",
    "से": "se",
    "पर": "par",
    "ने": "ne",
    "तो": "toh",
    "भी": "bhi",
    "कि": "ki",
    "यह": "yeh",
    "वह": "woh",
    "कर": "kar",
    "हो": "ho",
    "जो": "jo",
    "एक": "ek",
    "इस": "is",
    "लिए": "liye",
    "कुछ": "kuch",
    "अब": "ab",
    "जब": "jab",
    "या": "ya",
    "अगर": "agar",
    "लेकिन": "lekin",
    "मगर": "magar",
    "फिर": "phir",
    "सब": "sab",
    "तक": "tak",
    "बार": "baar",
    "साथ": "saath",
    "मैं": "main",
    "हम": "hum",
    "तुम": "tum",
    "आप": "aap",
    "वो": "wo",
    "ये": "ye",
    "कैसे": "kaise",
    "क्या": "kya",
    "कहाँ": "kahan",
    "कब": "kab",
    "कौन": "kaun",
    "कितना": "kitna",
    "कितने": "kitne",
    "कितनी": "kitni",
    "क्यों": "kyun",
    "कैसा": "kaisa",
    "कैसी": "kaisi",
    "अच्छा": "achha",
    "अच्छी": "achhi",
    "अच्छे": "achhe",
    "बुरा": "bura",
    "बड़ा": "bada",
    "छोटा": "chhota",
    "पहले": "pehle",
    "बाद": "baad",
    "ऊपर": "upar",
    "नीचे": "niche",
    "दाएँ": "daayein",
    "बाएँ": "baayein",
    "आगे": "aage",
    "पीछे": "peeche",
    "यहाँ": "yahan",
    "वहाँ": "wahan",
    "अंदर": "andar",
    "बाहर": "baahar",
    "ठीक": "theek",
    "सही": "sahi",
    "गलत": "galat",
    "जरूरी": "zaroori",
    "खुश": "khush",
    "दुखी": "dukhi",
    "प्यार": "pyaar",
    "नफरत": "nafrat",
    "दोस्त": "dost",
    "दुश्मन": "dushman",
    "काम": "kaam",
    "पैसा": "paisa",
    "पैसे": "paise",
    "रुपया": "rupya",
    "समय": "samay",
    "वक्त": "waqt",
    "दिन": "din",
    "रात": "raat",
    "सुबह": "subah",
    "शाम": "shaam",
    "घर": "ghar",
    "दुकान": "dukaan",
    "बाजार": "bazaar",
    "सड़क": "sadak",
    "गाड़ी": "gaadi",
    "पानी": "paani",
    "खाना": "khana",
    "रोटी": "roti",
    "चाय": "chai",
    "दूध": "doodh",
    "चीनी": "cheeni",
    "नमक": "namak",
    "मिर्ची": "mirchi",
    "सब्जी": "sabzi",
    "फल": "phal",
    "दवा": "dawa",
    "बीमार": "bimaar",
    "डॉक्टर": "doctor",
    "अस्पताल": "aspatal",
    "स्कूल": "school",
    "पढ़ाई": "padhai",
    "किताब": "kitaab",
    "कलम": "kalam",
    "कागज": "kagaz",
    "कपड़ा": "kapda",
    "जूता": "joota",
    "शरीर": "shareer",
    "हाथ": "haath",
    "पैर": "pair",
    "सिर": "sir",
    "आँख": "aankh",
    "कान": "kaan",
    "नाक": "naak",
    "मुँह": "munh",
    "दिल": "dil",
    "जान": "jaan",
    "ज़िंदगी": "zindagi",
    "मौत": "maut",
    "भगवान": "bhagwan",
    "दुनिया": "duniya",
    "देश": "desh",
    "शहर": "shehar",
    "गाँव": "gaon",
    "लोग": "log",
    "आदमी": "aadmi",
    "औरत": "aurat",
    "बच्चा": "bachha",
    "बच्चे": "bachhe",
    "लड़का": "ladka",
    "लड़की": "ladki",
    "माँ": "maa",
    "बाप": "baap",
    "पिता": "pita",
    "माता": "mata",
    "भाई": "bhai",
    "बहन": "behen",
    "बेटा": "beta",
    "बेटी": "beti",
    "पति": "pati",
    "पत्नी": "patni",
    "चलो": "chalo",
    "आओ": "aao",
    "जाओ": "jao",
    "बोलो": "bolo",
    "सुनो": "suno",
    "देखो": "dekho",
    "करो": "karo",
    "रुको": "ruko",
    "बैठो": "baitho",
    "खड़े": "khade",
    "खाओ": "khao",
    "पीओ": "piyo",
    "सोचो": "socho",
    "समझो": "samjho",
    "बताओ": "batao",
    "मिलो": "milo",
    "रखो": "rakho",
    "लो": "lo",
    "दो": "do",
    "हाँ": "haan",
    "ना": "na",
    "शायद": "shayad",
    "बिल्कुल": "bilkul",
    "सच": "sach",
    "झूठ": "jhooth",
    "बस": "bas",
    "सिर्फ": "sirf",
    "पूरा": "poora",
    "आधा": "aadha",
    "ज़रूर": "zaroor",
    "हमेशा": "hamesha",
    "कभी": "kabhi",
    "अभी": "abhi",
    "जल्दी": "jaldi",
    "धीरे": "dheere",
    "साल": "saal",
    "महीना": "mahina",
    "हफ्ता": "hafta",
    "आज": "aaj",
    "कल": "kal",
    "परसों": "parson",
    "नया": "naya",
    "पुराना": "purana",
    "ज़रा": "zara",
    "थोड़ा": "thoda",
    "बिजनेस": "business",
    "मार्जिन": "margin",
    "प्रॉफिट": "profit",
    "ग्रोथ": "growth",
    "स्ट्रैटेजी": "strategy",
    "मार्केट": "market",
    "कस्टमर": "customer",
    "प्रोडक्ट": "product",
    "सर्विस": "service",
    "कंपनी": "company",
    "ब्रांड": "brand",
    "मैनेजमेंट": "management",
    "इन्वेस्टमेंट": "investment",
    "रिटर्न": "return",
    "परसेंट": "percent",
    "नंबर": "number",
    "टार्गेट": "target",
    "रिजल्ट": "result",
    "प्रॉब्लम": "problem",
    "सॉल्यूशन": "solution",
    "इसलिए": "isliye",
    "वाला": "wala",
    "वाली": "wali",
    "वाले": "wale",
    "चाहिए": "chahiye",
    "बोलता": "bolta",
    "बोलती": "bolti",
    "करता": "karta",
    "करती": "karti",
    "जाता": "jaata",
    "जाती": "jaati",
    "आता": "aata",
    "आती": "aati",
    "देता": "deta",
    "देती": "deti",
    "लेता": "leta",
    "लेती": "leti",
    "मिलता": "milta",
    "मिलती": "milti",
    "रहता": "rehta",
    "रहती": "rehti",
    "सकता": "sakta",
    "सकती": "sakti",
}

# ──────────────────────────────────────────────────────────────────
# Pass 2: Hinglish canonical spelling (50+ entries)
# ──────────────────────────────────────────────────────────────────
HINGLISH_CANONICAL: dict[str, str] = {
    "fir": "phir",
    "mai": "main",
    "me": "mein",
    "nai": "nahi",
    "kyu": "kyun",
    "kyo": "kyun",
    "kiyu": "kyun",
    "kiyun": "kyun",
    "kyu": "kyun",
    "kyuki": "kyunki",
    "kyki": "kyunki",
    "kyonki": "kyunki",
    "haa": "haan",
    "ha": "haan",
    "ji": "ji",
    "accha": "achha",
    "acha": "achha",
    "achchha": "achha",
    "theek": "theek",
    "thik": "theek",
    "tik": "theek",
    "sahi": "sahi",
    "shi": "sahi",
    "zaroor": "zaroor",
    "zarur": "zaroor",
    "jaroor": "zaroor",
    "jaroori": "zaroori",
    "zroori": "zaroori",
    "zyaada": "zyada",
    "jyada": "zyada",
    "jyaada": "zyada",
    "bahot": "bahut",
    "bohot": "bahut",
    "bhut": "bahut",
    "boht": "bahut",
    "lkin": "lekin",
    "likn": "lekin",
    "lakin": "lekin",
    "mgr": "magar",
    "phle": "pehle",
    "pehele": "pehle",
    "pahle": "pehle",
    "kaise": "kaise",
    "kese": "kaise",
    "kese": "kaise",
    "samjh": "samajh",
    "smjh": "samajh",
    "yr": "yaar",
    "yar": "yaar",
    "bhai": "bhai",
    "bhi": "bhi",
    "bi": "bhi",
    "toh": "toh",
    "to": "toh",
    "islye": "isliye",
    "islie": "isliye",
    "isliy": "isliye",
    "kaam": "kaam",
    "kam": "kaam",
    "paisa": "paisa",
    "pesa": "paisa",
    "paise": "paise",
    "pese": "paise",
}

# ──────────────────────────────────────────────────────────────────
# Pass 3: Deterministic fixes — domain-specific corrections (30+)
# ──────────────────────────────────────────────────────────────────
DETERMINISTIC_FIXES: dict[str, str] = {
    "phirr": "phir",
    "nambar": "number",
    "buisness": "business",
    "bussiness": "business",
    "busines": "business",
    "marjin": "margin",
    "stratyji": "strategy",
    "strateji": "strategy",
    "strategi": "strategy",
    "proffit": "profit",
    "prfit": "profit",
    "growt": "growth",
    "groth": "growth",
    "cusomer": "customer",
    "custmer": "customer",
    "prodct": "product",
    "produkt": "product",
    "servce": "service",
    "servis": "service",
    "companee": "company",
    "kompany": "company",
    "managment": "management",
    "manegment": "management",
    "investmnt": "investment",
    "invesment": "investment",
    "retrn": "return",
    "persent": "percent",
    "percnt": "percent",
    "numbr": "number",
    "targt": "target",
    "rezult": "result",
    "problm": "problem",
    "soluton": "solution",
    "solushun": "solution",
    "markit": "market",
    "markeet": "market",
}


def normalize_hindi_text(text: str, lang: str = "hinglish") -> str:
    """
    3-pass deterministic normalization for Hindi/Hinglish text.
    
    Pass 1: Convert Devanagari words to Hinglish (Roman script)
    Pass 2: Canonicalize Hinglish spellings
    Pass 3: Apply domain-specific deterministic fixes
    
    Args:
        text: Input text (may contain Devanagari or inconsistent Hinglish)
        lang: Language mode — 'hindi' or 'hinglish'. 
              English mode should NOT call this function.
    
    Returns:
        Normalized text ready for LLM refinement.
    """
    if not text or not text.strip():
        return text

    original = text

    # Pass 1: Devanagari → Hinglish
    # Replace Devanagari tokens with their Hinglish equivalents
    for devanagari, roman in HINDI_TO_HINGLISH.items():
        text = text.replace(devanagari, roman)

    # Pass 2: Hinglish canonical spelling (word-level replacement)
    if lang in ("hindi", "hinglish"):
        words = text.split()
        normalized_words: list[str] = []
        for word in words:
            # Strip punctuation for matching, preserve it
            stripped: str = word.strip(".,!?;:'\"()-")
            prefix: str = word[:len(word) - len(word.lstrip(".,!?;:'\"()-"))]
            suffix: str = word[len(stripped) + len(prefix):]
            
            lower: str = stripped.lower()
            if lower in HINGLISH_CANONICAL:
                replacement: str = HINGLISH_CANONICAL[lower]
                # Preserve original capitalization pattern
                if stripped[0:1].isupper():
                    replacement = replacement.capitalize()
                normalized_words.append(prefix + replacement + suffix)
            else:
                normalized_words.append(word)
        text = " ".join(normalized_words)

    # Pass 3: Deterministic domain-specific fixes (word-level)
    words = text.split()
    fixed_words: list[str] = []
    for word in words:
        stripped: str = word.strip(".,!?;:'\"()-")
        prefix: str = word[:len(word) - len(word.lstrip(".,!?;:'\"()-"))]
        suffix: str = word[len(stripped) + len(prefix):]
        
        lower: str = stripped.lower()
        if lower in DETERMINISTIC_FIXES:
            replacement: str = DETERMINISTIC_FIXES[lower]
            if stripped[0:1].isupper():
                replacement = replacement.capitalize()
            fixed_words.append(prefix + replacement + suffix)
        else:
            fixed_words.append(word)
    text = " ".join(fixed_words)

    if text != original:
        logger.info(f"Hindi normalizer: '{original[:80]}...' → '{text[:80]}...'")

    return text
