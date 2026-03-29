import os
import subprocess
from pydub import AudioSegment
from dotenv import load_dotenv

# Initialize pydub with the correct ffmpeg path from .env
load_dotenv()
ffmpeg_path = os.getenv("FFMPEG_PATH")
if ffmpeg_path and os.path.exists(ffmpeg_path):
    AudioSegment.converter = ffmpeg_path

from .config import (
    CHUNK_SIZE_NORMAL, CHUNK_OVERLAP_NORMAL,
    CHUNK_SIZE_STRICT, CHUNK_OVERLAP_STRICT
)

class Chunk:
    def __init__(self, index: int, audio_path: str, start_time: float, end_time: float):
        self.index = index
        self.audio_path = audio_path
        self.start_time = start_time
        self.end_time = end_time
        
        # Pipeline fields
        self.raw_text = None
        self.llm_text = None
        self.final_text = None
        self.tokens = []
        self.language = None
        self.alignment = None
        self.asr_metadata = None

def extract_audio(video_path: str, output_path: str) -> str:
    """Extracts mono 16k PCM WAV audio for stable transcription and alignment."""
    ffmpeg_cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        output_path,
        "-y"
    ]
    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def overlap_chunk(audio_path: str, profile: str = 'balanced', mode: str = 'normal') -> list[Chunk]:
    """Splits an audio file into overlapping chunks."""
    audio = AudioSegment.from_file(audio_path)
    dur_seconds = len(audio) / 1000.0
    
    if mode == 'strict':
        size = CHUNK_SIZE_STRICT
        overlap = CHUNK_OVERLAP_STRICT
    else:
        size = CHUNK_SIZE_NORMAL
        overlap = CHUNK_OVERLAP_NORMAL
        
    chunks = []
    index = 0
    start = 0.0
    
    while start < dur_seconds:
        end = min(start + size, dur_seconds)
        
        # Extract milliseconds
        seg = audio[start*1000 : end*1000]
        chunk_path = f"{audio_path}_chunk_{index}.wav"
        seg.export(chunk_path, format="wav")
        
        chunks.append(Chunk(index=index, audio_path=chunk_path, start_time=start, end_time=end))
        
        if end == dur_seconds:
            break
            
        start += (size - overlap)
        index += 1
        
    return chunks

def apply_fade(chunk_path: str, fade_ms: int = 50) -> None:
    """Applies a quick crossfade to avoid pops on chunk boundaries."""
    try:
        audio = AudioSegment.from_file(chunk_path)
        audio = audio.fade_in(fade_ms).fade_out(fade_ms)
        export_format = os.path.splitext(chunk_path)[1].lstrip('.') or "wav"
        audio.export(chunk_path, format=export_format)
    except Exception:
        pass  # safe fallback
