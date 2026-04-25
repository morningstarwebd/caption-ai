"""System detection helpers for Caption AI setup wizard."""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run(cmd: list[str], timeout: int = 20) -> tuple[bool, str, str]:
    """Run a command safely and return (ok, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as exc:  # noqa: BLE001
        return False, "", str(exc)


def _bytes_to_gb(total_bytes: int) -> int:
    if total_bytes <= 0:
        return 0
    return max(1, round(total_bytes / (1024**3)))


def check_all() -> dict[str, Any]:
    """Collect all setup-relevant system details without raising exceptions."""
    try:
        return {
            "os": platform.system(),
            "ram_gb": get_ram_gb(),
            "gpu": get_gpu_info(),
            "python": get_python_info(),
            "node": get_node_info(),
            "ffmpeg": get_ffmpeg_info(),
            "playwright": check_playwright(),
        }
    except Exception:  # noqa: BLE001
        return {
            "os": platform.system(),
            "ram_gb": 0,
            "gpu": {"found": False, "name": "", "cuda": ""},
            "python": {"found": False, "version": "", "path": ""},
            "node": {"found": False, "version": ""},
            "ffmpeg": {"found": False, "path": ""},
            "playwright": {"found": False},
        }


def get_ram_gb() -> int:
    """Return total RAM in GB on Windows with WMIC-first strategy."""
    try:
        if platform.system().lower() != "windows":
            return 0

        # Primary method: sum all memory chip capacities.
        ok, out, _ = _run(["wmic", "memorychip", "get", "capacity"], timeout=20)
        if ok and out:
            numbers = [int(val) for val in re.findall(r"\d+", out)]
            if numbers:
                return _bytes_to_gb(sum(numbers))

        # Fallback 1: total physical memory from computersystem.
        ok, out, _ = _run(["wmic", "computersystem", "get", "TotalPhysicalMemory", "/value"], timeout=20)
        if ok and out:
            match = re.search(r"TotalPhysicalMemory=(\d+)", out)
            if match:
                return _bytes_to_gb(int(match.group(1)))

        # Fallback 2: modern PowerShell query.
        ok, out, _ = _run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory",
            ],
            timeout=20,
        )
        if ok and out:
            value_match = re.search(r"(\d+)", out)
            if value_match:
                return _bytes_to_gb(int(value_match.group(1)))

        return 0
    except Exception:  # noqa: BLE001
        return 0


def get_gpu_info() -> dict[str, Any]:
    """Detect NVIDIA GPU and CUDA version via nvidia-smi."""
    try:
        if not shutil.which("nvidia-smi"):
            return {"found": False, "name": "", "cuda": ""}

        ok_name, out_name, _ = _run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            timeout=20,
        )
        if not ok_name or not out_name:
            return {"found": False, "name": "", "cuda": ""}

        gpu_name = out_name.splitlines()[0].strip()

        ok_info, out_info, err_info = _run(["nvidia-smi"], timeout=20)
        combined = "\n".join(part for part in (out_info, err_info) if part)
        cuda_match = re.search(r"CUDA\s+Version:\s*([0-9.]+)", combined)
        cuda_version = cuda_match.group(1) if cuda_match else ""

        return {
            "found": bool(gpu_name),
            "name": gpu_name,
            "cuda": cuda_version,
        }
    except Exception:  # noqa: BLE001
        return {"found": False, "name": "", "cuda": ""}


def _normalize_python_version(raw: str) -> str:
    match = re.search(r"Python\s+([0-9]+\.[0-9]+\.[0-9]+)", raw)
    if match:
        return match.group(1)
    return ""


def get_python_info() -> dict[str, str | bool]:
    """Detect strict Python 3.11 using py launcher first."""
    try:
        ok, out, err = _run(["py", "-3.11", "--version"], timeout=20)
        version = _normalize_python_version(out or err)
        if ok and version.startswith("3.11"):
            ok_path, out_path, _ = _run(
                ["py", "-3.11", "-c", "import sys; print(sys.executable)"],
                timeout=20,
            )
            return {
                "found": True,
                "version": version,
                "path": out_path.strip() if ok_path else "",
            }

        # Fallback: plain python command if it is 3.11.
        ok, out, err = _run(["python", "--version"], timeout=20)
        version = _normalize_python_version(out or err)
        if ok and version.startswith("3.11"):
            ok_path, out_path, _ = _run(
                ["python", "-c", "import sys; print(sys.executable)"],
                timeout=20,
            )
            return {
                "found": True,
                "version": version,
                "path": out_path.strip() if ok_path else "",
            }

        return {"found": False, "version": "", "path": ""}
    except Exception:  # noqa: BLE001
        return {"found": False, "version": "", "path": ""}


def get_node_info() -> dict[str, str | bool]:
    """Detect Node.js version."""
    try:
        ok, out, err = _run(["node", "--version"], timeout=20)
        raw = out or err
        version = raw.strip().lstrip("v") if raw else ""
        if ok and version:
            return {"found": True, "version": version}
        return {"found": False, "version": ""}
    except Exception:  # noqa: BLE001
        return {"found": False, "version": ""}


def _read_env_ffmpeg_path() -> str:
    """Read FFMPEG_PATH from project root .env file without extra dependencies."""
    try:
        env_path = _project_root() / ".env"
        if not env_path.exists():
            return ""
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line or line.strip().startswith("#"):
                continue
            if line.startswith("FFMPEG_PATH="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                return value
        return ""
    except Exception:  # noqa: BLE001
        return ""


def get_ffmpeg_info() -> dict[str, str | bool]:
    """Detect FFmpeg from .env override first, then PATH."""
    try:
        env_path = _read_env_ffmpeg_path()
        if env_path and os.path.exists(env_path):
            return {"found": True, "path": env_path}

        ffmpeg_on_path = shutil.which("ffmpeg")
        if ffmpeg_on_path:
            return {"found": True, "path": ffmpeg_on_path}

        return {"found": False, "path": ""}
    except Exception:  # noqa: BLE001
        return {"found": False, "path": ""}


def check_playwright() -> dict[str, bool]:
    """Check whether Playwright is importable in Python 3.11 or current interpreter."""
    try:
        ok, out, _ = _run(
            [
                "py",
                "-3.11",
                "-c",
                "import importlib.util; print('1' if importlib.util.find_spec('playwright') else '0')",
            ],
            timeout=20,
        )
        if ok and out.strip() == "1":
            return {"found": True}

        # Fallback to current interpreter context.
        import importlib.util

        return {"found": importlib.util.find_spec("playwright") is not None}
    except Exception:  # noqa: BLE001
        return {"found": False}
