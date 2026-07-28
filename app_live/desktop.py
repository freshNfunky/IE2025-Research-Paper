"""Frozen (PyInstaller) entry point for the live-perception dashboard.

Unlike ``run.py`` (which uses uvicorn's string import for dev reload), this
imports the FastAPI app object directly so it works inside a one-file/one-dir
bundle, prepares a writable runtime directory (the bundle itself is read-only),
and opens the dashboard in the browser.

    HPERCEPT_HOME  overrides the writable runtime dir (default: ~/.hpercept-live)
    HPERCEPT_PORT  overrides the port (default: 8800)
"""
from __future__ import annotations

import os
import pathlib
import shutil
import sys
import threading
import time
import webbrowser


def _prepare_runtime_dir() -> pathlib.Path:
    """A writable working directory: YOLO downloads/writes here, uploads too."""
    home = pathlib.Path(os.environ.get("HPERCEPT_HOME",
                                       pathlib.Path.home() / ".hpercept-live"))
    home.mkdir(parents=True, exist_ok=True)
    if getattr(sys, "frozen", False):
        # Make the bundled YOLO weights available in the writable cwd so
        # ultralytics finds them by name instead of re-downloading.
        src = pathlib.Path(sys._MEIPASS) / "yolov8s.pt"
        dst = home / "yolov8s.pt"
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    os.chdir(home)
    return home


def main() -> None:
    _prepare_runtime_dir()
    from server import app                      # noqa: E402  (after chdir)
    import uvicorn                              # noqa: E402

    port = int(os.environ.get("HPERCEPT_PORT", "8800"))
    url = f"http://127.0.0.1:{port}/"

    def _open():
        time.sleep(2.5)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()
    print(f">>> hpercept-live dashboard at {url}")
    print(">>> the first processed frame is slow (models load on first use)")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
