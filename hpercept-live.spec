# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the standalone live-perception dashboard.

Build (from the repo root, inside the project venv):

    pyinstaller --noconfirm hpercept-live.spec

Produces a one-dir bundle in dist/hpercept-live/. The heavy ML stack
(torch, ultralytics, open_clip, transformers) is collected wholesale; the
CLIP / CLIPSeg model weights are still downloaded from Hugging Face on first
run, so the first launch needs a network connection.
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas, binaries, hiddenimports = [], [], []

# Whole-package collection for the ML stack and its runtime data / dylibs.
for pkg in ("torch", "torchvision", "ultralytics", "open_clip",
            "transformers", "tokenizers", "safetensors", "regex",
            "cv2", "PIL", "sympy", "networkx"):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

# Our own package + the app modules, plus uvicorn's dynamically-imported parts.
hiddenimports += collect_submodules("hpercept")
hiddenimports += collect_submodules("uvicorn")
hiddenimports += ["server", "anyio", "python_multipart", "multipart"]

# App data: config the pipeline reads from the repo root, plus the dashboard
# static assets, the demo manifest, and the YOLO weights (mirrored into the
# bundle so the app can run without a first-run YOLO download).
datas += [
    ("taxonomy.yaml", "."),
    ("segmentation.yaml", "."),
    ("yolov8s.pt", "."),
    ("app_live/static", "app_live/static"),
    ("app_live/demos.json", "app_live"),
]

block_cipher = None

a = Analysis(
    ["app_live/desktop.py"],
    pathex=["app_live"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # datasets and its dataframe backends (polars/pyarrow) are pulled in
    # transitively but never used by the live app -- dropping them saves ~300 MB.
    excludes=["tkinter", "matplotlib", "gradio", "datasets", "IPython",
              "notebook", "polars", "pyarrow"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="hpercept-live",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="hpercept-live",
)
