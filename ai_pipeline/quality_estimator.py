import librosa
import numpy as np
import logging
from .config import (
    DUAL_SCORE_THRESHOLD, ALIGN_AVG_THRESHOLD, CONFIDENCE_REPROCESS,
    NOISY_SNR_THRESHOLD, NOISY_DUAL_DELTA, NOISY_ALIGN_DELTA,
    FAST_SPEECH_THRESHOLD, FAST_SPEECH_ALIGN_DELTA
)

logger = logging.getLogger(__name__)

def measure_audio_quality(audio_path: str) -> dict:
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Volume RMS
        volume_rms = float(np.mean(librosa.feature.rms(y=y)))
        
        # SNR (Signal-to-Noise Ratio) estimation
        # Very rough estimate using harmonic/percussive source separation
        # Assuming harmonic is signal, percussive+margin is noise
        S = np.abs(librosa.stft(y))
        y_harmonic, y_percussive = librosa.decompose.hpss(S)
        signal_power = np.mean(y_harmonic**2)
        noise_power = np.mean(y_percussive**2) + 1e-10
        snr_db = float(10 * np.log10(signal_power / noise_power))
        
        # Speech rate estimation via onset detection
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')
        duration = librosa.get_duration(y=y, sr=sr)
        speech_rate = len(onsets) / duration if duration > 0 else 0
        
        return {
            'snr_db': round(snr_db, 2),
            'speech_rate': round(speech_rate, 2),
            'volume_rms': round(volume_rms, 4)
        }
    except Exception as e:
        logger.warning(f"Failed to measure audio quality: {e}")
        return {'snr_db': 20.0, 'speech_rate': 2.5, 'volume_rms': 0.05}

def adaptive_thresholds(snr_db: float, speech_rate: float) -> dict:
    base = {
        'dual_score': DUAL_SCORE_THRESHOLD,
        'align_avg': ALIGN_AVG_THRESHOLD,
        'confidence': CONFIDENCE_REPROCESS
    }
    
    # Apply deltas based on audio conditions
    if snr_db < NOISY_SNR_THRESHOLD:  # noisy audio
        base['dual_score'] += NOISY_DUAL_DELTA
        base['align_avg']  += NOISY_ALIGN_DELTA
        logger.info(f"Noisy audio detected (SNR {snr_db:.1f}dB) - Lowering thresholds.")
        
    if speech_rate > FAST_SPEECH_THRESHOLD:  # fast speech (words/sec)
        base['align_avg']  += FAST_SPEECH_ALIGN_DELTA
        logger.info(f"Fast speech detected ({speech_rate:.1f} w/s) - Lowering align threshold.")
        
    # Ensure thresholds don't drop below reasonable minimums
    base['dual_score'] = max(0.60, round(base['dual_score'], 2))
    base['align_avg'] = max(0.50, round(base['align_avg'], 2))
    
    return base
