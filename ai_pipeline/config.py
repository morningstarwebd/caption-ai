# config.py — Caption AI Engine Configuration

PIPELINE_VERSION = 'v4.3'

# -- Server --
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000

STORAGE_DIR = 'storage'
UPLOAD_DIR  = 'storage/uploads'
OUTPUT_DIR  = 'storage/outputs'
DB_PATH     = 'storage/caption_ai.db'

MAX_UPLOAD_SIZE_MB = 500

# -- Config Profile --
PROFILE = 'accurate'  # 'fast' | 'balanced' | 'accurate'

# -- Base Thresholds (overridden by adaptive engine) --
DUAL_SCORE_THRESHOLD   = 0.80
ALIGN_AVG_THRESHOLD    = 0.65
CONFIDENCE_REPROCESS   = 0.50
CONFIDENCE_DIM         = 0.60
CONFIDENCE_MICRO_REALIGN = 0.40

# -- Adaptive Engine Deltas --
NOISY_SNR_THRESHOLD      = 10
NOISY_DUAL_DELTA         = -0.05
NOISY_ALIGN_DELTA        = -0.05
FAST_SPEECH_THRESHOLD    = 3.5
FAST_SPEECH_ALIGN_DELTA  = -0.03

# -- Scoring Weights --
SEMANTIC_WEIGHT          = 0.60
KEYWORD_WEIGHT           = 0.40
ALIGN_LOW_RATIO_MAX      = 0.30
ALIGN_WORD_THRESHOLD     = 0.50

# -- Chunking --
CHUNK_SIZE_NORMAL        = 20
CHUNK_OVERLAP_NORMAL     = 4
CHUNK_SIZE_STRICT        = 12
CHUNK_OVERLAP_STRICT     = 5

# -- Sentence Split --
SENTENCE_MAX_WORDS       = 5
SENTENCE_MAX_WORDS_STRICT = 3
PROSODY_PAUSE_THRESHOLD  = 0.4

# -- Modern Caption Mode (word-by-word) --
WORD_GROUP_SIZE          = 3    # Words per caption group for modern display
MERGE_MIN_OVERLAP_WORDS  = 3

# -- Retry --
RETRY_GROQ  = 3
RETRY_LLM   = 1
RETRY_ALIGN = 3

# -- Alignment --
OVERLAP_TOLERANCE        = 0.10
DRIFT_MIN_GAP            = 0.02
MICRO_REALIGN_WINDOW     = 1.0

# -- Embedding --
EMBED_BATCH_SIZE         = 16

# -- LLM --
LLM_MODE                 = 'normal'

# -- LM Check --
LM_CHECK_MIN_SCORE       = 0.50

# -- Consistency Pass --
CONSISTENCY_WORD_DIFF_MAX = 0.05

# -- Cache --
CACHE_DIR                = 'storage/cache'

# -- Alignment Models --
MODEL_ALIGN_EN           = 'WAV2VEC2_ASR_BASE_960H'
MODEL_ALIGN_HI           = 'theainerd/Wav2Vec2-large-xlsr-hindi'

# -- Fallback Score --
MIN_SCORE_FALLBACK       = 0.60
MIN_REFINEMENT_WORD_KEEP_RATIO = 0.85
ALWAYS_KEEP_RAW_CHUNKS   = True
PRESERVE_FILLERS         = True

# -- Language-Aware Confidence --
CONFIDENCE_HINDI         = 0.70
CONFIDENCE_ENGLISH       = 0.78
CONFIDENCE_HINGLISH      = 0.72

# -- Hallucination Guard --
MAX_WORD_DIFF_RATIO      = 0.40

# -- Whisper Prompt Injection --
WHISPER_PROMPTS = {
    "hindi":    "bahut, nahi, kya, kaise, phir, toh, aur, lekin, business, margin",
    "hinglish": "bahut achha, nahi yaar, kya kar rahe, phir bhi, toh theek hai",
    "english":  "",
    "bengali":  "",
    "hi":       "bahut, nahi, kya, kaise, phir, toh, aur, lekin, business, margin",
    "en":       "",
    "bn":       "",
}

# -- Weak Segment Re-Transcription --
WEAK_SEGMENT_LOGPROB     = -0.4    # segments with avg_logprob below this get re-transcribed
WEAK_SEGMENT_NOSPEECH    = 0.6     # segments with no_speech_prob above this get re-transcribed
RETRANSCRIBE_WEAK        = True    # enable double-pass for shaky segments

# -- Observability --
LOG_STRUCTURED           = True
LOG_DIR                  = 'storage/logs'
