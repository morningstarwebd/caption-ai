from pydantic import BaseModel
from typing import Optional, List

class AlignedWord(BaseModel):
    word: str
    start: float
    end: float
    score: float = 0.0

class AlignedSegment(BaseModel):
    start: float
    end: float
    text: str
    words: Optional[List[AlignedWord]] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    filename: str
    target_lang: str

class JobDetailResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    filename: str
    target_lang: str
    error: Optional[str] = None
    srt: Optional[str] = None
    vtt: Optional[str] = None
    segments: Optional[List[AlignedSegment]] = None
    created_at: str
    completed_at: Optional[str] = None
