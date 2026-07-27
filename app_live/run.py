"""Launcher for the standalone live-perception dashboard.

Starts the local FastAPI server and opens the dashboard in the default browser.

    python app_live/run.py            # port 8800
    python app_live/run.py 8899       # custom port
"""
from __future__ import annotations

import pathlib
import sys
import threading
import time
import webbrowser

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))   # repo root -> hpercept
sys.path.insert(0, str(HERE))          # so "server" is importable

import uvicorn  # noqa: E402


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8800
    url = f"http://127.0.0.1:{port}/"

    def _open():
        time.sleep(1.5)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()
    print(f">>> Live perception dashboard at {url}")
    print(">>> first frame is slow (models load lazily on first use)")
    uvicorn.run("server:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
