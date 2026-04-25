"""Installation helpers for Caption AI setup wizard."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[str, int], None]
DRY_RUN_ENV_VAR = "CAPTION_AI_WIZARD_DRY_RUN"

_console_cb: Callable[[str], None] | None = None

def set_console_callback(cb: Callable[[str], None] | None) -> None:
    global _console_cb
    _console_cb = cb

def _print_console(text: str) -> None:
    if _console_cb:
        _console_cb(text)


HEAVY_PACKAGES = [
    ("faster-whisper", "faster_whisper"),
    ("whisperx", "whisperx"),
    ("sentence-transformers", "sentence_transformers"),
]


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _venv_paths() -> dict[str, Path]:
    root = _project_root()
    venv = root / "venv"
    return {
        "root": root,
        "venv": venv,
        "python": venv / "Scripts" / "python.exe",
        "pip": venv / "Scripts" / "pip.exe",
    }


def _emit(progress_cb: ProgressCallback | None, message: str, percent: int) -> None:
    try:
        if progress_cb:
            progress_cb(message, max(0, min(100, int(percent))))
    except Exception:
        # UI callback failures should not break installation logic.
        return


def resolve_dry_run(dry_run: bool | None = None) -> bool:
    """Resolve dry-run mode from explicit input or environment variable."""
    if dry_run is not None:
        return bool(dry_run)

    value = os.environ.get(DRY_RUN_ENV_VAR, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _simulate_step(
    progress_cb: ProgressCallback | None,
    messages: list[str],
    result: str,
    sleep_seconds: float = 0.2,
) -> tuple[bool, str]:
    """Simulate a step for UI testing without changing the host system."""
    steps = messages or ["Simulating..."]
    step_count = len(steps)
    for index, message in enumerate(steps, start=1):
        pct = int((index / step_count) * 100)
        _emit(progress_cb, message, pct)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
    return True, result


def run_cmd(cmd: list[str], cwd: str | Path | None = None, timeout: int = 600) -> tuple[bool, str]:
    """Run a shell command, stream its output, and return (success, output_or_error)."""
    try:
        _print_console(f"> {' '.join(cmd)}\n")
        kwargs = {}
        if os.name == 'nt':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(cwd or _project_root()),
            bufsize=1,
            **kwargs
        )

        output_lines = []
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                output_lines.append(line)
                _print_console(line)

        process.wait(timeout=timeout)
        output = "".join(output_lines).strip()

        if process.returncode == 0:
            return True, output or "OK"
        return False, output or f"Command failed with exit code {process.returncode}"
    except Exception as exc:  # noqa: BLE001
        _print_console(f"Error: {exc}\n")
        return False, str(exc)


def _download_file(url: str, dest: Path, progress_cb: ProgressCallback | None, label: str) -> tuple[bool, str]:
    """Download a file using urllib with optional progress callback and streaming console log."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        _print_console(f"Downloading: {url}\n")
        
        last_print = 0
        def _hook(block_count: int, block_size: int, total_size: int) -> None:
            nonlocal last_print
            if total_size <= 0:
                _emit(progress_cb, label, 0)
                return
            downloaded = block_count * block_size
            pct = int((downloaded / total_size) * 100)
            _emit(progress_cb, label, pct)
            
            # Print to console every 10%
            if (pct - last_print) >= 10 or pct == 100:
                mb_down = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                if last_print != pct:
                    _print_console(f"  ... {pct}% ({mb_down:.1f}MB / {mb_total:.1f}MB)\n")
                    last_print = pct

        urllib.request.urlretrieve(url, str(dest), reporthook=_hook)
        _print_console(f"Saved to: {dest}\n")
        _emit(progress_cb, label, 100)
        return True, str(dest)
    except Exception as exc:  # noqa: BLE001
        _print_console(f"Download error: {exc}\n")
        return False, str(exc)


def install_python(progress_cb: ProgressCallback | None, dry_run: bool | None = None) -> tuple[bool, str]:
    """Install Python 3.11 silently if missing."""
    try:
        if resolve_dry_run(dry_run):
            return _simulate_step(
                progress_cb,
                ["[Dry-run] Checking Python 3.11...", "[Dry-run] Python install skipped"],
                "Dry-run: simulated Python 3.11 installation",
            )

        ok, output = run_cmd(["py", "-3.11", "--version"], timeout=30)
        if ok:
            _emit(progress_cb, "Python 3.11 already installed", 100)
            return True, output

        _emit(progress_cb, "Downloading Python 3.11...", 0)
        installer_dest = Path(os.environ.get("TEMP", str(_project_root()))) / "python311.exe"
        url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        ok, message = _download_file(url, installer_dest, progress_cb, "Downloading Python 3.11...")
        if not ok:
            return False, message

        _emit(progress_cb, "Installing Python 3.11...", 100)
        return run_cmd(
            [
                str(installer_dest),
                "/quiet",
                "InstallAllUsers=0",
                "PrependPath=1",
                "Include_pip=1",
            ],
            timeout=1200,
        )
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def create_venv(progress_cb: ProgressCallback | None, dry_run: bool | None = None) -> tuple[bool, str]:
    """Create local virtual environment using Python 3.11."""
    try:
        paths = _venv_paths()

        if resolve_dry_run(dry_run):
            return _simulate_step(
                progress_cb,
                ["[Dry-run] Creating virtual environment...", "[Dry-run] venv step skipped"],
                str(paths["venv"]),
            )

        _emit(progress_cb, "Creating virtual environment...", 0)

        if paths["python"].exists() and paths["pip"].exists():
            _emit(progress_cb, "Virtual environment already exists", 100)
            return True, str(paths["venv"])

        if paths["venv"].exists() and not paths["python"].exists():
            shutil.rmtree(paths["venv"], ignore_errors=True)

        ok, message = run_cmd(["py", "-3.11", "-m", "venv", str(paths["venv"])], timeout=600)
        if ok:
            _emit(progress_cb, "Virtual environment ready", 100)
            return True, message

        return False, message
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def install_pytorch(
    cuda_version: str,
    ram_gb: int,
    progress_cb: ProgressCallback | None,
    dry_run: bool | None = None,
) -> tuple[bool, str]:
    """Install torch and auto-select CUDA index when possible."""
    try:
        if resolve_dry_run(dry_run):
            cuda_label = cuda_version or "cpu"
            return _simulate_step(
                progress_cb,
                [
                    f"[Dry-run] Preparing PyTorch for {cuda_label}...",
                    "[Dry-run] PyTorch install skipped",
                ],
                f"Dry-run: simulated torch install ({cuda_label})",
            )

        paths = _venv_paths()
        if not paths["pip"].exists():
            return False, "pip not found in virtual environment"

        _emit(progress_cb, "Installing PyTorch (large download)...", 0)
        cmd = [str(paths["pip"]), "install", "torch"]

        if cuda_version:
            try:
                cuda_int = int(cuda_version.replace(".", ""))
            except ValueError:
                cuda_int = 0

            if cuda_int >= 121:
                index_url = "https://download.pytorch.org/whl/cu121"
            elif cuda_int >= 118:
                index_url = "https://download.pytorch.org/whl/cu118"
            else:
                index_url = "https://download.pytorch.org/whl/cu118"

            cmd.extend(["--index-url", index_url])

        ok, message = run_cmd(cmd, timeout=3600)
        if not ok:
            return False, message

        if ram_gb and ram_gb <= 8:
            _emit(progress_cb, "Cooling RAM before next step...", 50)
            time.sleep(30)

        _emit(progress_cb, "PyTorch installation complete", 100)
        return True, message
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def install_heavy_package(
    pkg_name: str,
    import_name: str,
    ram_gb: int,
    progress_cb: ProgressCallback | None,
    dry_run: bool | None = None,
) -> tuple[bool, str]:
    """Install one heavy package at a time and verify import."""
    try:
        if resolve_dry_run(dry_run):
            return _simulate_step(
                progress_cb,
                [f"[Dry-run] Installing {pkg_name}...", f"[Dry-run] {pkg_name} install skipped"],
                f"Dry-run: simulated {pkg_name}",
            )

        paths = _venv_paths()
        if not paths["pip"].exists() or not paths["python"].exists():
            return False, "virtual environment is not ready"

        _emit(progress_cb, f"Installing {pkg_name}...", 0)
        ok, message = run_cmd([str(paths["pip"]), "install", pkg_name], timeout=3600)
        if not ok:
            return False, message

        # Import check catches broken wheels early.
        check_ok, check_message = run_cmd(
            [str(paths["python"]), "-c", f"import {import_name}; print('ok')"],
            timeout=120,
        )
        if not check_ok:
            return False, f"Installed {pkg_name} but import failed: {check_message}"

        if ram_gb and ram_gb <= 8:
            _emit(progress_cb, "Cooling RAM before next step...", 80)
            time.sleep(20)

        _emit(progress_cb, f"{pkg_name} installed", 100)
        return True, message
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def install_remaining(progress_cb: ProgressCallback | None, dry_run: bool | None = None) -> tuple[bool, str]:
    """Install the remaining Python dependencies in one pip call."""
    try:
        if resolve_dry_run(dry_run):
            return _simulate_step(
                progress_cb,
                ["[Dry-run] Installing remaining packages...", "[Dry-run] Remaining packages skipped"],
                "Dry-run: simulated remaining pip dependencies",
            )

        paths = _venv_paths()
        if not paths["pip"].exists():
            return False, "pip not found in virtual environment"

        _emit(progress_cb, "Installing remaining Python packages...", 0)
        packages = [
            "groq",
            "fastapi",
            "uvicorn[standard]",
            "aiosqlite",
            "python-multipart",
            "aiofiles",
            "python-dotenv",
            "librosa",
            "soundfile",
            "numpy",
            "langdetect",
            "pyspellchecker",
        ]

        ok, message = run_cmd([str(paths["pip"]), "install", *packages], timeout=3600)
        if ok:
            _emit(progress_cb, "Remaining packages installed", 100)
        return ok, message
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def install_node(progress_cb: ProgressCallback | None, dry_run: bool | None = None) -> tuple[bool, str]:
    """Install Node.js LTS silently if missing."""
    try:
        if resolve_dry_run(dry_run):
            return _simulate_step(
                progress_cb,
                ["[Dry-run] Downloading Node.js...", "[Dry-run] Node.js install skipped"],
                "Dry-run: simulated Node.js installation",
            )

        ok, output = run_cmd(["node", "--version"], timeout=30)
        if ok:
            _emit(progress_cb, "Node.js already installed", 100)
            return True, output

        _emit(progress_cb, "Downloading Node.js...", 0)
        node_dest = Path(os.environ.get("TEMP", str(_project_root()))) / "node_setup.msi"
        url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi"
        ok, message = _download_file(url, node_dest, progress_cb, "Downloading Node.js...")
        if not ok:
            return False, message

        _emit(progress_cb, "Installing Node.js...", 80)
        return run_cmd(["msiexec", "/i", str(node_dest), "/quiet", "/norestart"], timeout=1200)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def install_ffmpeg(progress_cb: ProgressCallback | None, dry_run: bool | None = None) -> tuple[bool, str]:
    """Download and extract FFmpeg into project-local folder."""
    try:
        if resolve_dry_run(dry_run):
            fake_path = _project_root() / "ffmpeg" / "bin" / "ffmpeg.exe"
            return _simulate_step(
                progress_cb,
                ["[Dry-run] Downloading FFmpeg...", "[Dry-run] FFmpeg install skipped"],
                str(fake_path),
            )

        existing = shutil.which("ffmpeg")
        if existing:
            _emit(progress_cb, "FFmpeg already available on PATH", 100)
            return True, existing

        root = _project_root()
        ffmpeg_dir = root / "ffmpeg"
        zip_dest = Path(os.environ.get("TEMP", str(root))) / "ffmpeg.zip"
        url = (
            "https://github.com/BtbN/FFmpeg-Builds/releases/download/"
            "latest/ffmpeg-master-latest-win64-gpl.zip"
        )

        _emit(progress_cb, "Downloading FFmpeg...", 0)
        ok, message = _download_file(url, zip_dest, progress_cb, "Downloading FFmpeg...")
        if not ok:
            return False, message

        _emit(progress_cb, "Extracting FFmpeg...", 70)
        if ffmpeg_dir.exists():
            shutil.rmtree(ffmpeg_dir, ignore_errors=True)
        ffmpeg_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_dest, "r") as archive:
            archive.extractall(ffmpeg_dir)

        ffmpeg_exe = ""
        for root_dir, _dirs, files in os.walk(ffmpeg_dir):
            if "ffmpeg.exe" in files:
                ffmpeg_exe = str(Path(root_dir) / "ffmpeg.exe")
                break

        if not ffmpeg_exe:
            return False, "ffmpeg.exe not found after extraction"

        _emit(progress_cb, "FFmpeg installed", 100)
        return True, ffmpeg_exe
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def install_frontend_deps(progress_cb: ProgressCallback | None, dry_run: bool | None = None) -> tuple[bool, str]:
    """Install frontend npm dependencies."""
    try:
        if resolve_dry_run(dry_run):
            return _simulate_step(
                progress_cb,
                ["[Dry-run] Installing frontend packages...", "[Dry-run] npm install skipped"],
                "Dry-run: simulated frontend npm install",
            )

        root = _project_root()
        frontend_dir = root / "frontend"
        if not frontend_dir.exists():
            return False, "frontend directory not found"

        _emit(progress_cb, "Installing frontend packages...", 0)
        ok, message = run_cmd(["npm", "install"], cwd=frontend_dir, timeout=3600)
        if ok:
            _emit(progress_cb, "Frontend packages installed", 100)
        return ok, message
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def install_playwright(progress_cb: ProgressCallback | None, dry_run: bool | None = None) -> tuple[bool, str]:
    """Install Playwright package and Chromium browser."""
    try:
        if resolve_dry_run(dry_run):
            return _simulate_step(
                progress_cb,
                ["[Dry-run] Installing Playwright...", "[Dry-run] Chromium download skipped"],
                "Dry-run: simulated Playwright + Chromium setup",
            )

        paths = _venv_paths()
        if not paths["pip"].exists() or not paths["python"].exists():
            return False, "virtual environment is not ready"

        _emit(progress_cb, "Installing Playwright...", 0)
        ok, message = run_cmd([str(paths["pip"]), "install", "playwright"], timeout=1800)
        if not ok:
            return False, message

        _emit(progress_cb, "Downloading Chromium...", 50)
        return run_cmd(
            [str(paths["python"]), "-m", "playwright", "install", "chromium"],
            timeout=3600,
        )
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _read_existing_env(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def create_env_file(groq_api_key: str, ffmpeg_path: str, dry_run: bool | None = None) -> tuple[bool, str]:
    """Create or update .env file with wizard-generated values."""
    try:
        env_path = _project_root() / ".env"

        if resolve_dry_run(dry_run):
            return _simulate_step(
                None,
                ["[Dry-run] Preparing .env values..."],
                str(env_path),
                sleep_seconds=0,
            )

        existing = _read_existing_env(env_path)

        existing["GROQ_API_KEY"] = (groq_api_key or "").strip()
        existing["FFMPEG_PATH"] = (ffmpeg_path or "").strip()
        existing.setdefault("PORT", "8000")
        existing.setdefault("HOST", "127.0.0.1")

        ordered_keys = ["GROQ_API_KEY", "FFMPEG_PATH", "PORT", "HOST"]
        output_lines = [f"{key}={existing.get(key, '')}" for key in ordered_keys]

        # Keep any custom keys the user may already have.
        for key, value in existing.items():
            if key not in ordered_keys:
                output_lines.append(f"{key}={value}")

        env_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
        return True, str(env_path)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def create_start_bat(dry_run: bool | None = None) -> tuple[bool, str]:
    """Create start.bat that launches backend and frontend development servers."""
    try:
        paths = _venv_paths()
        root = paths["root"]
        bat_path = root / "start.bat"

        if resolve_dry_run(dry_run):
            return True, str(bat_path)

        content = (
            "@echo off\n"
            "setlocal\n"
            "cd /d \"%~dp0\"\n"
            "echo Launching Caption AI...\n"
            "start \"Caption AI Backend\" \"%~dp0venv\\Scripts\\python.exe\" -m server.main\n"
            "timeout /t 3 /nobreak >nul\n"
            "start \"Caption AI Frontend\" cmd /c \"cd /d \"\"%~dp0frontend\"\" && npm run dev\"\n"
            "timeout /t 5 /nobreak >nul\n"
            "start \"\" http://localhost:3000\n"
        )
        bat_path.write_text(content, encoding="utf-8")
        return True, str(bat_path)
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
