"""Caption AI Setup Wizard (Tkinter)."""

from __future__ import annotations

import argparse
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk

try:
    from . import installer
    from .groq_validator import diagnose_error_with_groq, validate_groq_key
    from .lang import get_text
    from .system_check import check_all
except ImportError:
    import installer  # type: ignore
    from groq_validator import diagnose_error_with_groq, validate_groq_key  # type: ignore
    from lang import get_text  # type: ignore
    from system_check import check_all  # type: ignore


class CaptionAIWizard:
    def __init__(self, dry_run: bool = False) -> None:
        self.root = tk.Tk()
        self.root.title("Caption AI Setup")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.lang = "bn"
        self.dry_run = installer.resolve_dry_run(dry_run)
        self.system_info: dict = {}
        self.groq_key = ""
        self.ffmpeg_path = ""

        self.current_frame: tk.Frame | None = None
        self.install_widgets: list[dict] = []

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.show_language_screen()
        self.root.mainloop()

    def t(self, key: str) -> str:
        return get_text(self.lang, key)

    def _safe_ui(self, callback, *args, **kwargs) -> None:
        self.root.after(0, lambda: callback(*args, **kwargs))

    def _schedule_install_screen(self) -> None:
        self.root.after(600, self.show_install_screen)

    def _schedule_complete_screen(self) -> None:
        self.root.after(700, self.show_complete_screen)

    def switch_screen(self, new_frame_fn) -> None:
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = new_frame_fn()
        self.current_frame.pack(fill="both", expand=True)

    def show_language_screen(self) -> None:
        self.switch_screen(self._build_language_screen)

    def _build_language_screen(self) -> tk.Frame:
        frame = ttk.Frame(self.root, padding=24)

        ttk.Label(frame, text="Caption AI Setup Wizard", font=("Segoe UI", 18, "bold")).pack(pady=(20, 10))
        ttk.Label(frame, text=self.t("choose_lang"), font=("Segoe UI", 12)).pack(pady=(0, 18))

        buttons = [
            ("বাংলা", "bn"),
            ("English", "en"),
            ("हिंदी", "hi"),
        ]
        for label, code in buttons:
            ttk.Button(
                frame,
                text=label,
                width=24,
                command=lambda c=code: self._select_language(c),
            ).pack(pady=8)

        return frame

    def _select_language(self, lang_code: str) -> None:
        self.lang = lang_code
        self.show_system_check_screen()

    def show_system_check_screen(self) -> None:
        self.switch_screen(self._build_system_check_screen)

    def _build_system_check_screen(self) -> tk.Frame:
        frame = ttk.Frame(self.root, padding=20)

        ttk.Label(frame, text=self.t("title"), font=("Segoe UI", 16, "bold")).pack(pady=(10, 8))
        status_var = tk.StringVar(value=self.t("checking_system"))
        ttk.Label(frame, textvariable=status_var, font=("Segoe UI", 11)).pack(pady=(0, 8))

        if self.dry_run:
            ttk.Label(frame, text=self.t("dry_run_banner"), wraplength=540, justify="left").pack(pady=(0, 8), anchor="w")

        progress = ttk.Progressbar(frame, mode="indeterminate", length=420)
        progress.pack(pady=(0, 12))
        progress.start(10)

        details = tk.Text(frame, height=11, width=70, state="disabled", wrap="word")
        details.pack(pady=6)

        navigation_state = {"done": False}

        def _go_next() -> None:
            if navigation_state["done"]:
                return
            navigation_state["done"] = True
            self.show_groq_screen()

        continue_btn = ttk.Button(frame, text=self.t("continue_btn"), state="disabled", command=_go_next)
        continue_btn.pack(pady=(10, 6))

        def _complete_ui(lines: list[str]) -> None:
            progress.stop()
            status_var.set(self.t("system_ready"))
            details.configure(state="normal")
            details.delete("1.0", tk.END)
            details.insert(tk.END, "\n".join(lines))
            details.configure(state="disabled")
            continue_btn.configure(state="normal")
            self.root.after(1000, _go_next)

        def _worker() -> None:
            info = check_all()
            self.system_info = info

            gpu = info.get("gpu", {})
            py = info.get("python", {})
            node = info.get("node", {})
            ffmpeg = info.get("ffmpeg", {})
            playwright = info.get("playwright", {})

            lines = [f"OS: {info.get('os', 'Unknown')}", f"{self.t('ram')}: {info.get('ram_gb', 0)} GB"]
            lines.append(
                f"{self.t('gpu_found')}: {gpu.get('name', '')} (CUDA {gpu.get('cuda', 'N/A')})"
                if gpu.get("found")
                else self.t("gpu_not_found")
            )
            lines.append(
                f"{self.t('python_found')}: {py.get('version', '')}"
                if py.get("found")
                else self.t("python_not_found")
            )
            lines.append(
                f"{self.t('node_found')}: {node.get('version', '')}"
                if node.get("found")
                else self.t("node_not_found")
            )
            lines.append(
                f"{self.t('ffmpeg_found')}: {ffmpeg.get('path', '')}"
                if ffmpeg.get("found")
                else self.t("ffmpeg_not_found")
            )
            lines.append(self.t("playwright_found") if playwright.get("found") else self.t("playwright_not_found"))

            self._safe_ui(_complete_ui, lines)

        threading.Thread(target=_worker, daemon=True).start()
        return frame

    def show_groq_screen(self) -> None:
        self.switch_screen(self._build_groq_screen)

    def _build_groq_screen(self) -> tk.Frame:
        frame = ttk.Frame(self.root, padding=24)

        ttk.Label(frame, text=self.t("groq_title"), font=("Segoe UI", 16, "bold")).pack(pady=(10, 8))
        ttk.Label(frame, text=self.t("groq_hint"), font=("Segoe UI", 10)).pack(pady=(0, 12))

        if self.dry_run:
            ttk.Label(frame, text=self.t("dry_run_banner"), wraplength=540, justify="left").pack(pady=(0, 10), anchor="w")

        key_var = tk.StringVar(value=self.t("groq_placeholder"))
        status_var = tk.StringVar(value="")

        entry = ttk.Entry(frame, textvariable=key_var, width=56)
        entry.pack(pady=4)

        def _clear_placeholder(_event=None) -> None:
            if key_var.get() == self.t("groq_placeholder"):
                key_var.set("")

        entry.bind("<FocusIn>", _clear_placeholder)

        button_row = ttk.Frame(frame)
        button_row.pack(pady=12)

        ttk.Button(
            button_row,
            text=self.t("groq_get_key"),
            command=lambda: webbrowser.open("https://console.groq.com/keys", new=2),
        ).pack(side="left", padx=6)

        validate_btn = ttk.Button(button_row, text=self.t("groq_validate_btn"))
        validate_btn.pack(side="left", padx=6)

        def _on_skip() -> None:
            key = key_var.get().strip()
            if key and key != self.t("groq_placeholder"):
                self.groq_key = key
            else:
                self.groq_key = ""
            status_var.set(self.t("groq_skip_warn"))
            validate_btn.configure(state="disabled")
            skip_btn.configure(state="disabled")
            self._schedule_install_screen()

        skip_btn = ttk.Button(button_row, text=self.t("groq_skip"), command=_on_skip)
        skip_btn.pack(side="left", padx=6)

        status_label = ttk.Label(frame, textvariable=status_var, wraplength=520, justify="left")
        status_label.pack(pady=(8, 0), anchor="w")

        def _on_validate() -> None:
            key = key_var.get().strip()

            if self.dry_run:
                if not key or key == self.t("groq_placeholder"):
                    key = "gsk_dry_run"
                self.groq_key = key
                status_var.set(f"{self.t('groq_valid')} [{self.t('dry_run_banner')}]")
                validate_btn.configure(state="disabled")
                self._schedule_install_screen()
                return

            if not key or key == self.t("groq_placeholder"):
                status_var.set(self.t("groq_invalid"))
                return

            validate_btn.configure(state="disabled")
            status_var.set(self.t("groq_validating"))

            def _worker() -> None:
                ok, error = validate_groq_key(key)
                if ok:
                    self.groq_key = key
                    self._safe_ui(status_var.set, self.t("groq_valid"))
                    self._safe_ui(validate_btn.configure, state="disabled")
                    self._safe_ui(self._schedule_install_screen)
                    return

                diagnosis = diagnose_error_with_groq(key, error, self.lang)
                self._safe_ui(status_var.set, f"{self.t('groq_invalid')}\n{diagnosis}")
                self._safe_ui(validate_btn.configure, state="normal")

            threading.Thread(target=_worker, daemon=True).start()

        validate_btn.configure(command=_on_validate)
        entry.bind("<Return>", lambda _event: _on_validate())

        return frame

    def show_install_screen(self) -> None:
        self.switch_screen(self._build_install_screen)

    def _build_install_screen(self) -> tk.Frame:
        frame = ttk.Frame(self.root, padding=16)
        ttk.Label(frame, text=self.t("install_title"), font=("Segoe UI", 16, "bold")).pack(pady=(4, 6))
        ttk.Label(frame, text=self.t("close_apps"), wraplength=540, justify="left").pack(pady=(0, 8), anchor="w")

        if self.dry_run:
            ttk.Label(frame, text=self.t("dry_run_banner"), wraplength=540, justify="left").pack(pady=(0, 8), anchor="w")

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="x", pady=6)

        self.install_widgets = []
        steps = self._build_install_steps()
        for title, _runner in steps:
            row = ttk.Frame(list_frame)
            row.pack(fill="x", pady=3)

            title_lbl = ttk.Label(row, text=title, width=34)
            title_lbl.pack(side="left")

            progress = ttk.Progressbar(row, mode="determinate", maximum=100, length=190)
            progress.pack(side="left", padx=8)

            status = ttk.Label(row, text="⏳", width=3)
            status.pack(side="left")

            self.install_widgets.append({"progress": progress, "status": status})

        self.install_status_var = tk.StringVar(value=self.t("installing"))
        ttk.Label(frame, textvariable=self.install_status_var, wraplength=540, justify="left").pack(
            pady=(10, 2),
            anchor="w",
        )

        self.install_error_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.install_error_var, foreground="#b00020", wraplength=540, justify="left").pack(
            pady=(2, 0),
            anchor="w",
        )

        self.console_text = tk.Text(frame, height=10, width=70, font=("Consolas", 8), bg="#1e1e1e", fg="#d4d4d4", state="disabled")
        self.console_text.pack(pady=6, fill="both", expand=True)

        installer.set_console_callback(self._on_console_output)

        threading.Thread(target=self._run_install_steps, daemon=True).start()
        return frame

    def _on_console_output(self, line: str) -> None:
        def _append():
            if hasattr(self, "console_text") and self.console_text.winfo_exists():
                self.console_text.configure(state="normal")
                self.console_text.insert(tk.END, line)
                self.console_text.see(tk.END)
                self.console_text.configure(state="disabled")

        self.root.after(0, _append)

    def _build_install_steps(self):
        ram_gb = int(self.system_info.get("ram_gb") or 0)
        cuda_version = (self.system_info.get("gpu") or {}).get("cuda", "")

        steps = [
            (self.t("step_python"), lambda cb: self._step_python(cb)),
            (self.t("step_venv"), lambda cb: installer.create_venv(cb, dry_run=self.dry_run)),
            (
                self.t("step_torch"),
                lambda cb: installer.install_pytorch(cuda_version, ram_gb, cb, dry_run=self.dry_run),
            ),
        ]

        for pkg_name, import_name in installer.HEAVY_PACKAGES:
            title = f"{self.t('step_heavy')}: {pkg_name}"

            def _runner(cb, pkg=pkg_name, imp=import_name):
                return installer.install_heavy_package(pkg, imp, ram_gb, cb, dry_run=self.dry_run)

            steps.append((title, _runner))

        steps.extend(
            [
                (self.t("step_remaining"), lambda cb: installer.install_remaining(cb, dry_run=self.dry_run)),
                (self.t("step_node"), self._step_node),
                (self.t("step_ffmpeg"), self._step_ffmpeg),
                (self.t("step_frontend"), lambda cb: installer.install_frontend_deps(cb, dry_run=self.dry_run)),
                (self.t("step_playwright"), lambda cb: installer.install_playwright(cb, dry_run=self.dry_run)),
                (self.t("step_env"), self._step_env),
                (self.t("step_startbat"), lambda _cb: installer.create_start_bat(dry_run=self.dry_run)),
            ]
        )

        return steps

    def _update_step_progress(self, index: int, message: str, percent: int) -> None:
        widget = self.install_widgets[index]
        widget["progress"]["value"] = max(0, min(100, percent))
        widget["status"].configure(text="⏳")
        self.install_status_var.set(message)

    def _mark_step_success(self, index: int, message: str) -> None:
        widget = self.install_widgets[index]
        widget["progress"]["value"] = 100
        widget["status"].configure(text="✅")
        self.install_status_var.set(f"{self.t('install_done')}: {message}")

    def _mark_step_failed(self, index: int, message: str) -> None:
        widget = self.install_widgets[index]
        widget["status"].configure(text="❌")
        self.install_status_var.set(f"{self.t('install_fail')}: {message}")

    def _run_install_steps(self) -> None:
        steps = self._build_install_steps()
        for index, (_title, runner) in enumerate(steps):
            try:
                self._safe_ui(self._update_step_progress, index, self.t("installing"), 5)

                def _progress(msg: str, pct: int, i=index) -> None:
                    self._safe_ui(self._update_step_progress, i, msg, pct)

                ok, message = runner(_progress)
                if ok:
                    self._safe_ui(self._mark_step_success, index, message)
                    continue

                self._safe_ui(self._mark_step_failed, index, message)
                self._safe_ui(self.install_error_var.set, self.t("error_diagnosis"))
                diagnosis = diagnose_error_with_groq(self.groq_key, message, self.lang)
                self._safe_ui(self.install_error_var.set, diagnosis)
                return
            except Exception as exc:  # noqa: BLE001
                error_text = str(exc)
                self._safe_ui(self._mark_step_failed, index, error_text)
                self._safe_ui(self.install_error_var.set, error_text)
                return

        self._safe_ui(self.install_error_var.set, "")
        self._safe_ui(self.install_status_var.set, self.t("finished"))
        self._safe_ui(self._schedule_complete_screen)

    def _step_python(self, progress_cb):
        if (self.system_info.get("python") or {}).get("found"):
            progress_cb("Python 3.11 already available", 100)
            return True, "Python 3.11 already available"
        return installer.install_python(progress_cb, dry_run=self.dry_run)

    def _step_node(self, progress_cb):
        if (self.system_info.get("node") or {}).get("found"):
            progress_cb("Node.js already available", 100)
            return True, "Node.js already available"
        return installer.install_node(progress_cb, dry_run=self.dry_run)

    def _step_ffmpeg(self, progress_cb):
        existing_ffmpeg = (self.system_info.get("ffmpeg") or {}).get("path", "")
        if existing_ffmpeg and not self.dry_run:
            self.ffmpeg_path = existing_ffmpeg
            progress_cb("FFmpeg already available", 100)
            return True, existing_ffmpeg

        ok, message = installer.install_ffmpeg(progress_cb, dry_run=self.dry_run)
        if ok:
            self.ffmpeg_path = message
        return ok, message

    def _step_env(self, _progress_cb):
        ffmpeg_path = self.ffmpeg_path or (self.system_info.get("ffmpeg") or {}).get("path", "")
        return installer.create_env_file(self.groq_key, ffmpeg_path, dry_run=self.dry_run)

    def show_complete_screen(self) -> None:
        self.switch_screen(self._build_complete_screen)

    def _build_complete_screen(self) -> tk.Frame:
        frame = ttk.Frame(self.root, padding=24)
        ttk.Label(frame, text=self.t("launch_title"), font=("Segoe UI", 18, "bold")).pack(pady=(40, 14))
        hint_key = "dry_run_launch_hint" if self.dry_run else "launch_hint"
        ttk.Label(frame, text=self.t(hint_key), wraplength=520, justify="center").pack(pady=(0, 20))

        button_label = self.t("dry_run_launch_btn") if self.dry_run else self.t("launch_btn")
        button_action = self.root.destroy if self.dry_run else self._launch_caption_ai
        ttk.Button(frame, text=button_label, command=button_action, width=30).pack(pady=8)
        return frame

    def _launch_caption_ai(self) -> None:
        try:
            if self.dry_run:
                self.root.destroy()
                return

            project_root = Path(__file__).resolve().parent.parent
            start_bat = project_root / "start.bat"
            if not start_bat.exists():
                self.install_error_var.set("start.bat not found")
                return

            subprocess.Popen(["cmd", "/c", str(start_bat)], cwd=str(project_root))
            self.root.destroy()
        except Exception as exc:  # noqa: BLE001
            self.install_error_var.set(str(exc))


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Caption AI setup wizard")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the wizard without installing dependencies or writing files.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parsed = _parse_args(argv or [])
    CaptionAIWizard(dry_run=parsed.dry_run)


if __name__ == "__main__":
    main(sys.argv[1:])
