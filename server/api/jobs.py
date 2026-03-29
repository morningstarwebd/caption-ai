import os
import json
import uuid
import logging
from threading import Thread
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, WebSocket, WebSocketDisconnect
import aiosqlite
import aiofiles

from ..database import get_db, DB_PATH
from ..models import JobResponse, JobDetailResponse
from ..pipeline_runner import run_pipeline_sync
from ..progress import manager

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'storage', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=JobResponse)
async def create_job(
    target_lang: str = Form('en'),
    file: UploadFile = File(...)
):
    """Uploads a video and starts a background captioning job."""
    job_id = str(uuid.uuid4())
    filename = file.filename
    
    # Save file to disk
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{filename}")
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Insert initial job state
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO jobs (id, status, filename, target_lang) VALUES (?, ?, ?, ?)",
            (job_id, "processing", filename, target_lang)
        )
        await db.commit()

    # Start background thread for heavy processing
    t = Thread(target=run_pipeline_sync, args=(job_id, file_path, target_lang))
    t.daemon = True
    t.start()

    return JobResponse(
        job_id=job_id,
        status="processing",
        progress=0,
        filename=filename,
        target_lang=target_lang
    )

@router.get("/", response_model=List[JobDetailResponse])
async def list_jobs(db: aiosqlite.Connection = Depends(get_db)):
    """List all recent jobs."""
    cursor = await db.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50")
    rows = await cursor.fetchall()
    
    jobs = []
    for r in rows:
        jobs.append(JobDetailResponse(
            job_id=r['id'],
            status=r['status'],
            progress=r['progress'],
            filename=r['filename'],
            target_lang=r['target_lang'],
            error=r['error'],
            created_at=r['created_at'],
            completed_at=r['completed_at']
        ))
    return jobs

@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(job_id: str, db: aiosqlite.Connection = Depends(get_db)):
    """Get detailed state of a specific job, including output blocks."""
    cursor = await db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    r = await cursor.fetchone()
    
    if not r:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Parse segments from JSON
    segments = None
    if r['segments_json']:
        try:
            segments = json.loads(r['segments_json'])
        except (json.JSONDecodeError, TypeError):
            segments = None

    return JobDetailResponse(
        job_id=r['id'],
        status=r['status'],
        progress=r['progress'],
        filename=r['filename'],
        target_lang=r['target_lang'],
        error=r['error'],
        vtt=r['vtt_content'],
        srt=r['srt_content'],
        segments=segments,
        created_at=r['created_at'],
        completed_at=r['completed_at']
    )

@router.get("/{job_id}/video")
async def get_video(job_id: str, db: aiosqlite.Connection = Depends(get_db)):
    """Stream the uploaded video file for browser playback."""
    from fastapi.responses import FileResponse
    
    cursor = await db.execute("SELECT filename FROM jobs WHERE id = ?", (job_id,))
    r = await cursor.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Job not found")
    
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}_{r['filename']}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(file_path, media_type="video/mp4")

@router.post("/{job_id}/export")
async def export_video(
    job_id: str,
    db: aiosqlite.Connection = Depends(get_db),
    captions_json: str = Form(None),
    theme: str = Form("viral_shorts"),
    ass_content: str = Form(None),
    resolution: str = Form("1080p"),
    render_mode: str = Form("headless"),
):
    """
    Export video with burned captions.
    
    render_mode='headless' (default): Pixel-perfect rendering via headless browser.
    render_mode='ass': Legacy ASS-based rendering via FFmpeg (faster but less accurate).
    """
    import asyncio
    from fastapi.responses import FileResponse

    logger.info(f"EXPORT STARTED for job {job_id}, mode={render_mode}, resolution={resolution}")
    
    cursor = await db.execute("SELECT filename FROM jobs WHERE id = ?", (job_id,))
    r = await cursor.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Job not found")

    original_video_name = f"{job_id}_{r['filename']}"
    original_video_path = os.path.join(UPLOAD_DIR, original_video_name)
    if not os.path.exists(original_video_path):
        raise HTTPException(status_code=404, detail="Original video file not found")

    # ── HEADLESS BROWSER EXPORT (pixel-perfect) ──
    if render_mode == "headless" and captions_json:
        from ..headless_export import export_headless

        async def progress_cb(status: str, percent: int, details: str):
            await manager.broadcast(job_id, {
                "status": status, "percent": percent, "details": details
            })

        try:
            output_path = await export_headless(
                job_id=job_id,
                video_path=original_video_path,
                captions_json=captions_json,
                theme=theme,
                resolution=resolution,
                progress_callback=progress_cb,
            )
            return FileResponse(
                output_path,
                media_type="video/mp4",
                filename=f"captioned_{resolution}_{r['filename']}",
            )
        except Exception as e:
            logger.error(f"Headless export failed: {e}")
            await manager.broadcast(job_id, {
                "status": "export_failed", "percent": -1, "details": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Headless export failed: {e}")

    # ── LEGACY ASS EXPORT (fallback) ──
    if not ass_content or not ass_content.strip():
        raise HTTPException(status_code=400, detail="No captions data provided (need captions_json or ass_content)")
        
    if "[Script Info]" not in ass_content or "[Events]" not in ass_content:
        raise HTTPException(status_code=400, detail="Invalid ASS content format")

    await manager.broadcast(job_id, {"status": "export_started", "percent": 0, "details": "Preparing export..."})

    ass_filename = f"{job_id}_temp.ass"
    ass_filepath = os.path.join(UPLOAD_DIR, ass_filename)
    with open(ass_filepath, 'w', encoding='utf-8') as f:
        f.write(ass_content)

    output_filename = f"{job_id}_exported_{resolution}.mp4"
    output_filepath = os.path.join(UPLOAD_DIR, output_filename)

    scale_filter = ""
    if resolution == "1080p":
        scale_filter = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
    elif resolution == "720p":
        scale_filter = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
    elif resolution == "480p":
        scale_filter = "scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2,"

    vf_string = f"{scale_filter}ass={ass_filename}"

    total_duration = 0.0
    try:
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            original_video_name,
        ]
        probe_proc = await asyncio.create_subprocess_exec(
            *probe_cmd, cwd=UPLOAD_DIR,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        probe_out, _ = await probe_proc.communicate()
        total_duration = float(probe_out.decode().strip())
    except Exception:
        logger.warning(f"ffprobe failed for {original_video_name}")

    await manager.broadcast(job_id, {"status": "exporting", "percent": 1, "details": "Burning subtitles..."})

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", original_video_name,
        "-vf", vf_string,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-c:a", "copy", "-progress", "pipe:1",
        output_filename,
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *ffmpeg_cmd, cwd=UPLOAD_DIR,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        last_broadcast_pct = 0
        while process.stdout:
            line_bytes = await process.stdout.readline()
            if not line_bytes:
                break
            line = line_bytes.decode("utf-8", errors="replace").strip()
            if line.startswith("out_time_us="):
                try:
                    time_us = int(line.split("=", 1)[1])
                    current_secs = time_us / 1_000_000
                    pct = min(99, int((current_secs / total_duration) * 100)) if total_duration > 0 else min(90, last_broadcast_pct + 1)
                    if pct >= last_broadcast_pct + 2:
                        last_broadcast_pct = pct
                        await manager.broadcast(job_id, {"status": "exporting", "percent": pct, "details": f"Rendering video... {pct}%"})
                except (ValueError, IndexError):
                    pass
        await process.wait()
        if process.returncode != 0:
            stderr_bytes = await process.stderr.read() if process.stderr else b""
            logger.error(f"FFmpeg subtitle burn failed: {stderr_bytes.decode()}")
            await manager.broadcast(job_id, {"status": "export_failed", "percent": -1, "details": "FFmpeg error"})
            raise HTTPException(status_code=500, detail="Failed to burn subtitles into video.")
        await manager.broadcast(job_id, {"status": "export_complete", "percent": 100, "details": "Done!"})
    except Exception as e:
        logger.error(f"Export exception: {e}")
        await manager.broadcast(job_id, {"status": "export_failed", "percent": -1, "details": str(e)})
        raise HTTPException(status_code=500, detail="Export process failed.")
    finally:
        if os.path.exists(ass_filepath):
            os.remove(ass_filepath)

    return FileResponse(
        output_filepath,
        media_type="video/mp4",
        filename=f"captioned_{r['filename']}",
    )

@router.websocket("/{job_id}/ws")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates of a specific job.
    """
    await manager.connect(websocket, job_id)
    try:
        while True:
            # We expect the client to keep the connection alive but we don't 
            # expect it to send commands.
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket, job_id)
