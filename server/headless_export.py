"""
Headless Browser Export — Pixel-perfect caption rendering via Playwright + FFmpeg.

Captures each caption frame as a transparent PNG from the Next.js /render page,
then composites onto the original video using FFmpeg overlay filter.
"""

import os
import json
import asyncio
import logging
import struct
from typing import Callable, Awaitable, Optional

logger = logging.getLogger(__name__)

# Resolution presets
RESOLUTION_MAP = {
    "1080p": (1920, 1080),
    "720p": (1280, 720),
    "480p": (854, 480),
}

RENDER_PAGE_URL = "http://localhost:3000/render"
EXPORT_FPS = 30


async def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds via ffprobe."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            video_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, _ = await proc.communicate()
        return float(out.decode().strip())
    except Exception as e:
        logger.error(f"ffprobe failed: {e}")
        return 0.0


async def export_headless(
    job_id: str,
    video_path: str,
    captions_json: str,
    theme: str,
    resolution: str,
    progress_callback: Callable[[str, int, str], Awaitable[None]],
) -> str:
    """
    Export video with pixel-perfect burned captions using headless browser.
    
    Returns the path to the output MP4 file.
    """
    from playwright.async_api import async_playwright

    width, height = RESOLUTION_MAP.get(resolution, (1920, 1080))
    output_dir = os.path.dirname(video_path)
    output_path = os.path.join(output_dir, f"{job_id}_exported_{resolution}.mp4")

    await progress_callback("export_started", 0, "Launching headless browser...")

    # Get video duration
    duration = await get_video_duration(video_path)
    if duration <= 0:
        raise RuntimeError("Could not determine video duration")

    total_frames = int(duration * EXPORT_FPS)
    logger.info(f"Headless export: {total_frames} frames @ {EXPORT_FPS}fps, duration={duration:.2f}s")

    async with async_playwright() as p:
        # Launch headless Chromium
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = await browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=1,
        )

        await progress_callback("exporting", 2, "Loading render page...")

        # Navigate to the render page
        await page.goto(RENDER_PAGE_URL, wait_until="networkidle")

        # Wait for the page to be ready
        await page.wait_for_function("() => window.__RENDER_PAGE_LOADED__ === true", timeout=10000)

        # Inject caption data
        escaped_json = captions_json.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        inject_result = await page.evaluate(
            f"() => window.setCaptionData(`{escaped_json}`, '{theme}', {width}, {height})"
        )
        if not inject_result:
            await browser.close()
            raise RuntimeError("Failed to inject caption data into render page")

        await progress_callback("exporting", 5, "Starting frame capture...")

        # Start FFmpeg process for compositing
        # Input 1: original video
        # Input 2: PNG frames piped via stdin (transparent overlay)
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            # Input 0: original video
            "-i", video_path,
            # Input 1: piped PNG frames as overlay
            "-f", "image2pipe", "-framerate", str(EXPORT_FPS), "-c:v", "png", "-i", "pipe:0",
            # Filter: overlay transparent PNGs onto video
            "-filter_complex",
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2[base];"
            f"[1:v]format=rgba[ov];"
            f"[base][ov]overlay=0:0:shortest=1[out]",
            "-map", "[out]",
            "-map", "0:a?",
            # Encoding
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-c:a", "copy",
            "-pix_fmt", "yuv420p",
            output_path,
        ]

        ffmpeg_proc = await asyncio.create_subprocess_exec(
            *ffmpeg_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Capture frames
        last_pct = 5
        try:
            for frame_idx in range(total_frames):
                current_time = frame_idx / EXPORT_FPS

                # Set the caption time in the render page
                await page.evaluate(f"() => window.setCaptionTime({current_time})")

                # Small delay to let React re-render
                await asyncio.sleep(0.01)

                # Capture the #render-frame element as transparent PNG
                element = page.locator("#render-frame")
                screenshot_bytes = await element.screenshot(
                    type="png",
                    omit_background=True,
                )

                # Write PNG bytes to FFmpeg stdin
                if ffmpeg_proc.stdin:
                    ffmpeg_proc.stdin.write(screenshot_bytes)
                    await ffmpeg_proc.stdin.drain()

                # Progress update (throttle to every 2%)
                pct = 5 + int((frame_idx / total_frames) * 90)  # 5% to 95%
                if pct >= last_pct + 2:
                    last_pct = pct
                    await progress_callback(
                        "exporting", pct,
                        f"Rendering frame {frame_idx + 1}/{total_frames} ({pct}%)"
                    )

        except Exception as e:
            logger.error(f"Frame capture error at frame {frame_idx}: {e}")
            raise
        finally:
            # Close FFmpeg stdin and wait for it to finish
            if ffmpeg_proc.stdin:
                ffmpeg_proc.stdin.close()

            await ffmpeg_proc.wait()
            await browser.close()

        # Check FFmpeg result
        if ffmpeg_proc.returncode != 0:
            stderr_out = await ffmpeg_proc.stderr.read() if ffmpeg_proc.stderr else b""
            logger.error(f"FFmpeg failed: {stderr_out.decode()}")
            raise RuntimeError(f"FFmpeg compositing failed (exit code {ffmpeg_proc.returncode})")

        await progress_callback("export_complete", 100, "Done!")
        logger.info(f"Headless export complete: {output_path}")

    return output_path
