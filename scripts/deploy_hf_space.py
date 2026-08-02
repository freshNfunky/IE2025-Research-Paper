"""Assemble and upload the YOLO+ HuggingFace Space.

A Space needs the app files AND the hpercept package + taxonomy.yaml at its root.
This copies them into a build folder and uploads it as a Gradio Space.

Prereq (once, in your terminal): huggingface-cli login   (paste your HF token)

Usage:
    python scripts/deploy_hf_space.py <owner>/<space-name> [--private]
    # e.g.  python scripts/deploy_hf_space.py XIXUM-ORG/yolo-plus-perception
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "build" / "hf_space_build"


def assemble() -> Path:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    # app + card + requirements from hf_space/
    for f in ("app.py", "requirements.txt", "README.md"):
        shutil.copy2(REPO / "hf_space" / f, BUILD / f)
    # the package + taxonomy
    shutil.copytree(REPO / "hpercept", BUILD / "hpercept",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "openworld"))
    shutil.copy2(REPO / "taxonomy.yaml", BUILD / "taxonomy.yaml")
    print(f">>> assembled Space at {BUILD}")
    return BUILD


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    repo_id = args[0]
    private = "--private" in sys.argv

    build = assemble()

    from huggingface_hub import HfApi, whoami
    try:
        whoami()
    except Exception:
        print("!! Not logged in. Run:  huggingface-cli login   then retry.")
        sys.exit(1)

    api = HfApi()
    api.create_repo(repo_id, repo_type="space", space_sdk="gradio",
                    private=private, exist_ok=True)
    api.upload_folder(folder_path=str(build), repo_id=repo_id, repo_type="space",
                      commit_message="Deploy YOLO+ hierarchical perception demo")
    print(f">>> done: https://huggingface.co/spaces/{repo_id}")


if __name__ == "__main__":
    main()
