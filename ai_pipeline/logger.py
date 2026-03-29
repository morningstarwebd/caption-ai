import json
import os
import time
import logging
from .config import LOG_DIR, LOG_STRUCTURED
from statistics import mean

logger = logging.getLogger(__name__)


class PipelineLogger:
    """Structured pipeline logger for the v4.3 orchestrator."""

    def __init__(self, filename: str):
        self.filename = filename
        self.chunks = []
        self.start_time = None
        self.end_time = None
        self.error = None

    def start_run(self):
        self.start_time = time.time()

    def end_run(self, error: str = None):
        self.end_time = time.time()
        self.error = error
        if LOG_STRUCTURED:
            self._write_log()

    def log_chunk(self, index: int, lang: str, raw: str, refined: str, final: str, score: float):
        self.chunks.append({
            'index': index,
            'lang': lang,
            'raw': raw,
            'refined': refined,
            'final': final,
            'score': score
        })

    def get_summary(self) -> dict:
        scores = [c['score'] for c in self.chunks if c.get('score') is not None]
        accepted = sum(1 for c in self.chunks if c.get('final'))
        return {
            'total_chunks': len(self.chunks),
            'accepted': accepted,
            'rejected': len(self.chunks) - accepted,
            'avg_score': round(mean(scores), 3) if scores else 0,
            'duration_s': round(self.end_time - self.start_time, 2) if self.start_time and self.end_time else 0,
            'error': self.error
        }

    def _write_log(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        log_file = os.path.join(LOG_DIR, f"{self.filename}_{int(time.time())}.jsonl")
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                for chunk in self.chunks:
                    f.write(json.dumps(chunk) + '\n')
        except Exception as e:
            logger.warning(f"Failed to write pipeline log: {e}")


class ChunkLogger:
    def __init__(self):
        self.chunk_logs = {}

    def log_chunk(self, job_id: str, chunk_index: int, data: dict):
        if not LOG_STRUCTURED:
            return
        if job_id not in self.chunk_logs:
            self.chunk_logs[job_id] = []
        os.makedirs(LOG_DIR, exist_ok=True)
        log_entry = {'timestamp': time.time(), 'chunk': chunk_index, **data}
        self.chunk_logs[job_id].append(log_entry)
        log_file = os.path.join(LOG_DIR, f"{job_id}.jsonl")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


class PipelineMetrics:
    def __init__(self):
        self.total_chunks = 0
        self.llm_accepted = 0
        self.llm_rejected = 0
        self.align_scores = []
        self.retry_counts = []
        self.flagged_chunks = []

    def add_chunk(self, accepted: bool, align_avg: float, retries: int, flagged: bool = False):
        self.total_chunks += 1
        if accepted:
            self.llm_accepted += 1
        else:
            self.llm_rejected += 1
        if align_avg is not None:
            self.align_scores.append(align_avg)
        self.retry_counts.append(retries)
        if flagged:
            self.flagged_chunks.append(self.total_chunks - 1)

    def summary(self) -> dict:
        return {
            'total_chunks': self.total_chunks,
            'llm_acceptance_rate': (self.llm_accepted / self.total_chunks) if self.total_chunks > 0 else 0,
            'avg_alignment_score': mean(self.align_scores) if self.align_scores else 0,
            'avg_retry_rate': mean(self.retry_counts) if self.retry_counts else 0,
            'flagged_count': len(self.flagged_chunks)
        }


chunk_logger = ChunkLogger()
metrics = PipelineMetrics()
