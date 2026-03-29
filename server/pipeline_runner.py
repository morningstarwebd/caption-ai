import os
import json
import asyncio
import logging
from ai_pipeline.main import run_pipeline
from .database import DB_PATH
import aiosqlite
from .progress import manager

logger = logging.getLogger(__name__)

async def update_job_status(job_id: str, status: str, progress: int = None, 
                            error: str = None, srt: str = None, vtt: str = None,
                            segments: list = None):
    async with aiosqlite.connect(DB_PATH) as db:
        
        updates = []
        params = []
        
        updates.append("status = ?")
        params.append(status)
        
        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)
            
        if error is not None:
            updates.append("error = ?")
            params.append(error)
            
        if srt is not None:
            updates.append("srt_content = ?")
            params.append(srt)
            
        if vtt is not None:
            updates.append("vtt_content = ?")
            params.append(vtt)

        if segments is not None:
            updates.append("segments_json = ?")
            params.append(json.dumps(segments, ensure_ascii=False))
            
        if status in ['completed', 'failed']:
            updates.append("completed_at = CURRENT_TIMESTAMP")
            
        query = f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?"
        params.append(job_id)
        
        await db.execute(query, tuple(params))
        await db.commit()

def run_pipeline_sync(job_id: str, video_path: str, target_lang: str):
    """
    Synchronous wrapper to run the pipeline.
    This runs in a separate thread with its own event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    def on_progress(status: str, percent: int, details: str = ""):
        # Update DB via this thread's own event loop
        loop.run_until_complete(update_job_status(job_id, status, percent))
        # Broadcast WebSocket progress — broadcast_progress uses threading.Lock
        # so it's safe to call from any event loop
        loop.run_until_complete(manager.broadcast_progress(job_id, status, percent, details))

    try:
        on_progress("Pipeline started", 1)
        
        result = run_pipeline(
            video_path=video_path,
            user_target_lang=target_lang,
            progress_callback=on_progress
        )
        
        if result["status"] == "success":
            logger.info(f"Job {job_id} Completed successfully")
            loop.run_until_complete(
                update_job_status(
                    job_id, "completed", 100, 
                    srt=result.get("srt"), vtt=result.get("vtt"),
                    segments=result.get("segments")
                )
            )
            loop.run_until_complete(
                manager.broadcast_progress(job_id, "completed", 100, "Captioning finished successfully.")
            )
        else:
            err_msg = result.get("message", "Unknown pipeline error")
            logger.error(f"Job {job_id} Failed gracefully: {err_msg}")
            loop.run_until_complete(update_job_status(job_id, "failed", error=err_msg))
            loop.run_until_complete(manager.broadcast_progress(job_id, "failed", 0, err_msg))

    except Exception as e:
        logger.exception(f"Job {job_id} Pipeline crashed.")
        try:
            loop.run_until_complete(update_job_status(job_id, "failed", error=str(e)))
        except Exception:
            logger.error(f"Job {job_id} Failed to update DB after crash")
        try:
            loop.run_until_complete(manager.broadcast_progress(job_id, "failed", 0, str(e)))
        except Exception:
            logger.error(f"Job {job_id} Failed to broadcast after crash")
        
    finally:
        loop.close()
