import os
import logging
from typing import Dict, Any, List

# Setup core logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from .audio import extract_audio, overlap_chunk, apply_fade
from .quality_estimator import measure_audio_quality, adaptive_thresholds
from .transcriber import transcribe_chunk_with_retry
from .lang_detector import detect_language
from .llm_judge import refine_transcript
from .lm_check import lightweight_lm_check
from .dual_scorer import compute_dual_score
from .confidence import determine_confidence_threshold
from .chunk_merger import merge_chunks
from .sentence_splitter import split_sentences_v2
from .aligner import align_text
from .alignment_validator import validate_alignment, check_hallucination
from .drift_clamp import clamp_alignment_drift
from .logger import PipelineLogger
from .renderer import generate_srt, generate_vtt
from .config import (
    MODEL_ALIGN_EN, MODEL_ALIGN_HI,
    ALWAYS_KEEP_RAW_CHUNKS, MIN_REFINEMENT_WORD_KEEP_RATIO
)
from .hindi_normalizer import normalize_hindi_text


def _has_enough_words(source_text: str, candidate_text: str) -> bool:
    source_words = len(source_text.split())
    candidate_words = len(candidate_text.split())

    if source_words == 0:
        return candidate_words == 0

    minimum_words = max(1, int(source_words * MIN_REFINEMENT_WORD_KEEP_RATIO))
    return candidate_words >= minimum_words

def run_pipeline(video_path: str, user_target_lang: str = "en", progress_callback=None) -> Dict[str, Any]:
    """
    Main execution flow for Caption AI Engine.
    Executes the deterministic 15-step captioning pipeline.
    """
    pipeline_logger = PipelineLogger(os.path.basename(video_path))
    pipeline_logger.start_run()
    
    def emit_progress(status: str, percent: int, details: str = ""):
        logger.info(f"Progress: {percent}% - {status}")
        if progress_callback:
            progress_callback(status, percent, details)
            
    try:
        emit_progress("Initializing via Audio Analyzer", 5)
        
        # Ensure .wav path exists
        audio_path = f"{os.path.splitext(video_path)[0]}_temp.wav"
        extract_audio(video_path, audio_path)
        
        # 1. Audio Quality Estimation & Adaptive Thresholds
        emit_progress("Estimating Audio Quality", 10)
        metrics = measure_audio_quality(audio_path)
        adaptive_thresholds_dict = adaptive_thresholds(metrics['snr_db'], metrics['speech_rate'])
        logger.info(f"Adaptive Thresholds Applied: {adaptive_thresholds_dict}")
        
        # 2. Profile-Aware Chunking
        emit_progress("Chunking Audio", 15)
        is_strict = metrics['snr_db'] < 10.0
        chunks = overlap_chunk(audio_path, mode='strict' if is_strict else 'normal')
        
        total_chunks = len(chunks)
        processed_chunks = []
        
        # Process chunks
        for i, chunk in enumerate(chunks):
            chunk_pct = 15 + int(((i) / total_chunks) * 50)
            emit_progress(f"Processing Chunk {i+1}/{total_chunks}", chunk_pct)
            
            # Apply anti-pop fade
            apply_fade(chunk.audio_path)
            
            # 3. Intelligent Transcription (with Retry + Prompt Injection)
            transcription_result = transcribe_chunk_with_retry(chunk.audio_path, language=user_target_lang)
            raw_text = transcription_result["text"]
            chunk.raw_text = raw_text
            chunk.asr_metadata = transcription_result
            
            if not raw_text.strip():
                processed_chunks.append(chunk)
                continue
                
            # 4. Chunk-Level Lang Detection
            detected_lang = detect_language(raw_text.split())
            chunk.language = detected_lang
            
            # 5. Preserve spoken words in maximum-recall mode.
            clean_text = raw_text.strip()
            scoring_text = clean_text
            
            # 5.5 Hindi/Hinglish Normalizer (3-pass deterministic correction)
            if detected_lang in ("hindi", "hinglish", "hi") or user_target_lang in ("hindi", "hinglish", "hi"):
                scoring_text = normalize_hindi_text(clean_text, lang=detected_lang)
            
            # 6. LLM Contextual Judge
            llm_mode = 'critical' if is_strict else 'normal'
            try:
                refined_text = refine_transcript(scoring_text, detected_lang, mode=llm_mode, target_lang=user_target_lang)
            except Exception as exc:
                logger.warning(f"Chunk {i} LLM refinement failed: {exc}. Using unrefined text.")
                refined_text = scoring_text
            
            # 7. Hallucination Guard
            # Skip for 'hinglish' — transliteration (Devanagari→Roman) naturally changes 
            # word counts, causing false positives in the word-count-diff check.
            if user_target_lang == 'hinglish':
                pass  # Trust the LLM transliteration
            elif not check_hallucination(scoring_text, refined_text):
                logger.warning(f"Chunk {i} failed hallucination guard. Falling back to raw text.")
                refined_text = scoring_text  # Fallback

            keeps_enough_words = _has_enough_words(clean_text, refined_text)
            
            # 8. Dual Scoring (Semantic + Keyword)
            # 9. LM Pre-Check
            # For Hinglish transliteration, skip scoring — the semantic similarity between
            # Devanagari source and Roman transliteration will always be very low.
            if user_target_lang == 'hinglish':
                score = 1.0
                chunk.score = score
                chunk.final_text = refined_text if keeps_enough_words else clean_text
            else:
                lm_score = lightweight_lm_check(refined_text, detected_lang)
                
                # Adaptive Threshold integration
                confidence_threshold = determine_confidence_threshold(refined_text, adaptive_thresholds_dict)
                
                if lm_score > 0.9:
                    score = lm_score
                else:
                    score = compute_dual_score(clean_text, refined_text)
                    
                chunk.score = score
                
                if score >= confidence_threshold and keeps_enough_words:
                    chunk.final_text = refined_text
                else:
                    logger.info(
                        f"Chunk {i} using maximum-recall fallback. "
                        f"Score={score:.2f}, Threshold={confidence_threshold:.2f}, "
                        f"WordKeep={keeps_enough_words}"
                    )
                    chunk.final_text = scoring_text or clean_text

            if ALWAYS_KEEP_RAW_CHUNKS and not chunk.final_text.strip():
                chunk.final_text = clean_text
                
            pipeline_logger.log_chunk(
                index=i, lang=detected_lang, 
                raw=clean_text, refined=refined_text, 
                final=chunk.final_text, score=score
            )
            
            processed_chunks.append(chunk)

        # 10. Order-Safe Parallel Merge
        emit_progress("Merging Timelines", 70)
        merged_text, merged_segments = merge_chunks(processed_chunks)
        
        # 11. Global Consistency Pass
        # We skip global_consistency_pass here because passing the entire text through the LLM 
        # destroys the exact chunk-level temporal boundaries. Sync is much more critical!
        
        # 12. Sentence Splitter v2
        emit_progress("Splitting Sentences", 80)
        prompt_segments_with_time = []
        
        for seg in merged_segments:
            seg_sents = split_sentences_v2(seg['text'], strict=is_strict)
            n_sents = len(seg_sents)
            if n_sents == 0:
                continue
                
            # Distribute the chunk's time proportionally by word count.
            # Even distribution causes sync drift — a 2-word sentence gets the same 
            # time window as a 10-word sentence, pushing WhisperX alignment off.
            word_counts = [max(len(s.split()), 1) for s in seg_sents]
            total_words = sum(word_counts)
            seg_total_dur = seg['end'] - seg['start']
            
            cursor = seg['start']
            for i, sent in enumerate(seg_sents):
                frac = word_counts[i] / total_words
                sent_dur = seg_total_dur * frac
                sent_start = round(cursor, 3)
                sent_end = round(cursor + sent_dur, 3)
                prompt_segments_with_time.append({
                    "text": sent,
                    "start": sent_start,
                    "end": sent_end
                })
                cursor += sent_dur
        
        # 13. Deterministic Alignment
        emit_progress("Word-Level Alignment", 85)
        
        # Use Hindi model ONLY for Devanagari Hindi or Bengali. 
        # For Hinglish, use English model because it uses Latin (Roman) alphabet.
        if user_target_lang in ['hi', 'bn']:
            align_model = MODEL_ALIGN_HI 
        else:
            align_model = MODEL_ALIGN_EN
            
        try:
            aligned_segments = align_text(prompt_segments_with_time, audio_path, align_model)
        except Exception as e:
            logger.error(f"Alignment fully failed: {e}. Cannot generate timestamps.")
            raise
            
        # 14. Alignment Drift Clamp - apply per-segment word-level + segment-level
        clamped_segments = []
        for seg in aligned_segments:
            if 'words' in seg:
                seg['words'] = clamp_alignment_drift(seg['words'])
            clamped_segments.append(seg)
        
        # Segment-level drift clamp: prevent overlapping segment boundaries
        for i in range(1, len(clamped_segments)):
            prev = clamped_segments[i - 1]
            curr = clamped_segments[i]
            if 'start' in curr and 'end' in prev:
                if curr['start'] < prev['end']:
                    # Split the overlap at midpoint
                    mid = (prev['end'] + curr['start']) / 2
                    prev['end'] = round(mid - 0.005, 3)
                    curr['start'] = round(mid + 0.005, 3)
        
        # 15. Alignment Validation
        emit_progress("Validating Alignments", 90)
        is_valid = validate_alignment(clamped_segments, adaptive_thresholds_dict)
        if not is_valid:
            logger.warning("Alignment validation failed. Output may have misaligned tokens.")
            
        emit_progress("Generating Formats", 95)
        srt_content = generate_srt(clamped_segments)
        vtt_content = generate_vtt(clamped_segments)
        
        # Clean up temp files
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        for c in chunks:
            if os.path.exists(c.audio_path):
                os.remove(c.audio_path)
                
        emit_progress("Completed", 100)
        
        pipeline_logger.end_run()
        log_summary = pipeline_logger.get_summary()
        
        return {
            "status": "success",
            "srt": srt_content,
            "vtt": vtt_content,
            "segments": clamped_segments,
            "metrics": log_summary
        }
        
    except Exception as e:
        logger.exception("Pipeline failed critically.")
        emit_progress("Failed", -1, str(e))
        pipeline_logger.end_run(error=str(e))
        return {
            "status": "error",
            "message": str(e)
        }
