<div align="center">

# 🎬 Caption AI

### AI-Powered Video Captioning Engine with Premiere Pro-Inspired Editor

**Generate pixel-perfect captions** for Bengali, Hindi, English & Hinglish videos — completely free, local-first, and open-source.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#-features) · [Demo](#-demo) · [Quick Start](#-quick-start) · [Setup Wizard (Windows)](#-setup-wizard-windows) · [Architecture](#-architecture) · [Contributing](#-contributing)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌍 **Multi-Language** | Bengali, Hindi, English & Hinglish with auto-detection |
| 🎯 **92–97% Accuracy** | 15-step deterministic pipeline with adaptive thresholds |
| ⏱️ **Millisecond Sync** | WhisperX forced alignment for frame-perfect timing |
| 🎨 **16 Caption Themes** | Minimal, Cinematic, Viral Shorts, Karaoke Neon & more |
| 🖥️ **Premiere Pro Editor** | 5-panel browser-based NLE with timeline editing |
| 🔧 **Self-Calibrating** | Audio-aware engine adapts to noise, speech rate & language |
| 🇮🇳 **Hindi/Hinglish Mastery** | 3-pass normalizer + transliteration-aware scoring |
| 📤 **Multiple Exports** | Burned MP4, SRT, ASS with headless pixel-perfect rendering |
| 💰 **100% Free** | Uses Groq's free API — no paid services required |
| 🔒 **Local-First** | Your videos never leave your machine |

---

## 🖥️ Demo

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│ Caption AI    File  Edit  Sequence  Captions  Export        │
├──────────┬──────────────────────────┬───────────────────────┤
│          │                          │ Caption Editor        │
│  Media   │   Program Monitor        │ ┌─────────────────┐  │
│  Panel   │   (Video Preview +       │ │ 00:01.2 - 00:03 │  │
│          │    Caption Overlay)       │ │ "আজকে আমরা..."  │  │
│          │                          │ │ 00:03.1 - 00:05 │  │
│          │                          │ │ "देखेंगे कैसे" │  │
├──────────┴──────────────────────────┴───────────────────────┤
│ ▶ 00:00:03.200  ├────┤────┤────┤────┤────┤────┤            │
│ V1 ████████░░░░░░░░░░░░░░░░░  Timeline                     │
│ C1 ██ ████ ███ ██████ ██████  Caption Track                 │
│ A1 ▁▃▅▇▅▃▁▃▅▇▅▃▁▃▅▇▅▃▁▃▅▇  Waveform                      │
└─────────────────────────────────────────────────────────────┘
```

</div>

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** — [Download](https://python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **FFmpeg** — [Download](https://ffmpeg.org/download.html)
- **Groq API Key** (free) — [Get one here](https://console.groq.com/keys)

### 1. Clone & Setup

```bash
git clone https://github.com/morningstarweb/caption-ai.git
cd caption-ai
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Run

```bash
# Terminal 1 — Backend (port 8000)
python -m server.main

# Terminal 2 — Frontend (port 3000)
cd frontend
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** and start captioning! 🎉

---

## 🧙 Setup Wizard (Windows)

The project now includes a Windows setup wizard in the [wizard](wizard) folder.

### Run Wizard (normal mode)

```bash
python -m wizard.wizard
```

### Run Wizard (dry-run mode)

Dry-run mode tests the full UI flow without performing real installs or writing `.env` / `start.bat`.

```bash
python -m wizard.wizard --dry-run
```

You can also enable dry-run using an environment variable:

```powershell
$env:CAPTION_AI_WIZARD_DRY_RUN="1"
python -m wizard.wizard
```

### Build `.exe` Wizard

```bat
wizard\build.bat
```

`build.bat` auto-uses `wizard/icon.ico` if present; otherwise it builds without an icon.

---

## 🏗️ Architecture

### Pipeline Overview

```
Video → Audio Extract → Quality Estimation → Adaptive Thresholds
  → Chunking → ASR (Groq Whisper) → Language Detection
  → Hindi Normalization → LLM Refinement → Hallucination Guard
  → Dual Scoring → LM Check → Merge → Sentence Split
  → WhisperX Alignment → Drift Clamp → SRT/VTT Output
```

### 15-Step AI Engine

| Step | Module | Description |
|------|--------|-------------|
| 1 | `audio.py` | Extract & chunk audio with overlap |
| 2 | `quality_estimator.py` | Measure SNR & speech rate |
| 3 | `config.py` | Adaptive threshold calibration |
| 4 | `audio.py` | Profile-aware chunking (strict/normal) |
| 5 | `transcriber.py` | Groq Whisper + retry with prompt biasing |
| 6 | `lang_detector.py` | Per-chunk language detection |
| 7 | `hindi_normalizer.py` | 3-pass deterministic Hindi/Hinglish correction |
| 8 | `llm_judge.py` | LLM contextual refinement (Llama 3.3 70B) |
| 9 | `hallucination_guard.py` | Word-count validation guard |
| 10 | `dual_scorer.py` | Semantic + keyword dual scoring |
| 11 | `lm_check.py` | Language model validation |
| 12 | `chunk_merger.py` | Order-safe parallel merge |
| 13 | `sentence_splitter.py` | Smart sentence splitting (prosody-aware) |
| 14 | `aligner.py` | WhisperX forced alignment |
| 15 | `drift_clamp.py` | Alignment drift correction & validation |

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Engine** | Python, Groq Whisper large-v3, Llama 3.3 70B, WhisperX |
| **Backend** | FastAPI, SQLite (aiosqlite), WebSocket real-time progress |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Zustand |
| **Rendering** | FFmpeg, Playwright (headless pixel-perfect), ImageMagick |
| **Timeline** | react-resizable-panels, WaveSurfer.js, dnd-kit |

### Project Structure

```
caption-ai/
├── ai_pipeline/                # 🧠 AI captioning engine (15 modules)
│   ├── main.py                 # Pipeline orchestrator
│   ├── config.py               # All thresholds & settings
│   ├── transcriber.py          # Groq Whisper ASR
│   ├── hindi_normalizer.py     # Hindi/Hinglish 3-pass normalizer
│   ├── aligner.py              # WhisperX forced alignment
│   ├── dual_scorer.py          # Semantic + keyword scoring
│   ├── llm_judge.py            # LLM contextual refinement
│   ├── hallucination_guard.py  # Word-count validation
│   ├── quality_estimator.py    # Audio quality & SNR analysis
│   ├── sentence_splitter.py    # Prosody-aware sentence split
│   ├── drift_clamp.py          # Alignment drift correction
│   └── ...                     # + 8 more pipeline modules
├── server/                     # ⚡ FastAPI backend
│   ├── main.py                 # Server entry point
│   ├── database.py             # SQLite async database
│   ├── pipeline_runner.py      # Background pipeline executor
│   ├── headless_export.py      # Pixel-perfect video export
│   └── api/
│       ├── jobs.py             # Upload, status, export, WebSocket
│       └── health.py           # Health check endpoint
├── frontend/                   # 🎨 Next.js 14 Premiere Pro editor
│   └── src/
│       ├── app/                # Pages & layout
│       ├── components/editor/  # 12 editor components
│       │   ├── ProgramMonitor  # Video preview + caption overlay
│       │   ├── Timeline        # Track-based composition editor
│       │   ├── CaptionEditor   # Caption list + inline editing
│       │   ├── MediaPanel      # File browser & import
│       │   └── Toolbar         # Menu bar + tool selection
│       ├── store/              # Zustand state (4 stores)
│       ├── hooks/              # Custom React hooks
│       └── lib/                # API client, types, utilities
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── CONTRIBUTING.md             # Contribution guidelines
└── LICENSE                     # MIT License
```

---

## 🎨 Caption Themes

16 built-in themes — fully customizable per caption:

| Theme | Style | Theme | Style |
|-------|-------|-------|-------|
| `minimal` | Clean white text | `neon_glow` | Bright neon colors |
| `viral_shorts` | Bold yellow, high impact | `typewriter` | Monospace typewriter |
| `cinematic` | Elegant serif, letter-spaced | `comic_pop` | Comic book style |
| `karaoke_neon` | Glowing cyan neon | `elegant_serif` | Refined serif typography |
| `kalakar_fire` | Bold red gradient | `gradient_wave` | Gradient color flow |
| `glassmorphism` | Frosted glass background | `outline_bold` | Heavy outline text |
| `retro_vhs` | VHS distortion feel | `shadow_3d` | 3D shadow effect |
| `dramatic` | Italic dramatic feel | `highlight_box` | Highlighted background |

---

## 🌍 Language Support

| Language | ASR | Normalization | Alignment Model | Status |
|----------|-----|---------------|-----------------|--------|
| 🇺🇸 English | ✅ Groq Whisper | — | WAV2VEC2_ASR_BASE | ✅ Stable |
| 🇮🇳 Hindi | ✅ Groq Whisper | ✅ 3-pass normalizer | Wav2Vec2-large-xlsr-hindi | ✅ Stable |
| 🇮🇳 Hinglish | ✅ Groq Whisper | ✅ 3-pass normalizer | Wav2Vec2-large-xlsr-hindi | ✅ Stable |
| 🇧🇩 Bengali | ✅ Groq Whisper | — | WAV2VEC2_ASR_BASE | ✅ Stable |

---

## 🔌 API Reference

### Upload Video & Start Captioning
```http
POST /api/jobs
Content-Type: multipart/form-data

file: <video_file>
target_lang: "auto" | "english" | "hindi" | "hinglish" | "bengali"

→ { "job_id": "uuid", "status": "processing", "filename": "video.mp4" }
```

### Get Job Status & Results
```http
GET /api/jobs/{job_id}

→ { "job_id": "...", "status": "completed", "srt": "...", "segments": [...] }
```

### List All Jobs
```http
GET /api/jobs

→ [ { "job_id": "...", "status": "completed", "filename": "..." }, ... ]
```

### Real-time Progress (WebSocket)
```http
WS /api/jobs/{job_id}/ws

→ { "status": "transcribing", "percent": 45, "details": "Chunk 3/7" }
```

### Export Video with Burned Captions
```http
POST /api/jobs/{job_id}/export

render_mode: "headless" | "ass"
resolution: "720p" | "1080p"

→ Binary MP4 file
```

### Health Check
```http
GET /api/health

→ { "status": "ok", "version": "5.0.0" }
```

---

## 🤝 Contributing

We love contributions! Whether it's a bug fix, new feature, or documentation improvement — every PR matters.

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

```bash
# Quick start for contributors
git fork https://github.com/morningstarweb/caption-ai.git
git checkout -b feature/amazing-feature
# Make your changes...
git commit -m "feat: add amazing feature"
git push origin feature/amazing-feature
# Open a Pull Request!
```

### Ideas for Contribution

- 🌐 **New Languages** — Add support for more languages
- 🎨 **Caption Themes** — Design new caption styles
- ⚡ **Performance** — Optimize pipeline speed
- 📱 **Mobile UI** — Improve responsive editor
- 🧪 **Testing** — Add test coverage
- 📖 **Docs** — Improve documentation & examples
- 🔧 **Integrations** — YouTube upload, cloud storage, etc.

---

## 📋 System Requirements

### Minimum
- 4GB RAM
- Python 3.10+
- Node.js 18+
- Any modern browser (Chrome, Firefox, Edge)
- Internet connection (for Groq API calls)

### Recommended
- 8GB+ RAM
- NVIDIA GPU (for faster WhisperX alignment)
- SSD storage
- FFmpeg installed globally

---

## ❓ FAQ

<details>
<summary><strong>Is it really free?</strong></summary>

Yes! Caption AI uses Groq's free API tier for both Whisper transcription and LLM refinement. No credit card required.
</details>

<details>
<summary><strong>Do my videos get uploaded anywhere?</strong></summary>

No. Everything runs locally on your machine. Videos are processed on your own hardware, and the only external API call is for transcription text (audio is sent to Groq's API, but no video data leaves your machine).
</details>

<details>
<summary><strong>What video formats are supported?</strong></summary>

Any format that FFmpeg can decode — MP4, MKV, AVI, MOV, WebM, and more.
</details>

<details>
<summary><strong>Can I use my own Whisper model instead of Groq?</strong></summary>

The pipeline is designed around Groq's hosted Whisper for speed and zero-cost. Self-hosted Whisper support is a great contribution opportunity!
</details>

<details>
<summary><strong>How accurate are the captions?</strong></summary>

92–97% accuracy depending on audio quality, language, and speech clarity. The adaptive engine automatically adjusts thresholds for noisy audio or fast speech.
</details>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Free to use, modify, and distribute. Attribution appreciated but not required.

---

## ⭐ Support the Project

If Caption AI helps you, consider:
- ⭐ **Starring** this repo — helps others discover it
- 🐛 **Filing issues** — helps us improve
- 🔀 **Contributing** — helps everyone
- 📢 **Sharing** — tell others about it!

---

<div align="center">

**Built with ❤️ for the open-source community**

[Report Bug](https://github.com/morningstarweb/caption-ai/issues) · [Request Feature](https://github.com/morningstarweb/caption-ai/issues) · [Discussions](https://github.com/morningstarweb/caption-ai/discussions)

</div>
