import os
import sys
from dotenv import load_dotenv

# 1. Load context and Inject FFmpeg into PATH immediately
# This MUST happen before any AI pipeline modules are imported
load_dotenv()
ffmpeg_exe = os.getenv("FFMPEG_PATH")
if ffmpeg_exe and os.path.exists(ffmpeg_exe):
    ffmpeg_bin = os.path.dirname(ffmpeg_exe)
    if ffmpeg_bin not in os.environ["PATH"]:
        os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
        sys.stdout.write(f"INFO: Global FFmpeg injection successful: {ffmpeg_bin}\n")

# 2. Add project root to path so `ai_pipeline` can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# These imports will trigger ai_pipeline logic
from .database import init_db
from .api import health, jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    await init_db()
    
    # Check for crucial API Keys
    if not os.getenv("GROQ_API_KEY") or "your_groq_api_key" in os.getenv("GROQ_API_KEY"):
        print("WARNING: GROQ_API_KEY is not set or is still a placeholder. Transcription will fail.")
        
    yield
    
    # Shutdown
    print("Shutting down the server...")


app = FastAPI(
    title="Caption AI",
    description="AI-powered video captioning engine for Bengali, Hindi, English & Hinglish",
    version="5.0.0",
    lifespan=lifespan
)

# CORS configuration for Frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Next.js frontend (port 3000) and any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API routers
app.include_router(health.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")

# v5: Frontend runs as separate Next.js app on port 3000
# Old CDN static mount removed to prevent route conflicts
