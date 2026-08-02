"""Assemble and upload the YOLO+ HuggingFace *model* repo (free, no Space needed).

Bundles the model card (hf_model/README.md) + a runnable copy of the app and the
hpercept package + taxonomy, so the repo is a self-contained landing page people
can also clone and run locally.

Prereq (once): huggingface-cli login
Usage: python scripts/deploy_hf_model.py <owner>/<name> [--private]
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "build" / "hf_model_build"


def assemble() -> Path:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    shutil.copy2(REPO / "hf_model" / "README.md", BUILD / "README.md")
    shutil.copy2(REPO / "hf_space" / "app.py", BUILD / "app.py")
    shutil.copy2(REPO / "hf_space" / "requirements.txt", BUILD / "requirements.txt")
    shutil.copytree(REPO / "hpercept", BUILD / "hpercept",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "openworld"))
    shutil.copy2(REPO / "taxonomy.yaml", BUILD / "taxonomy.yaml")
    print(f">>> assembled model repo at {BUILD}")
    return BUILD


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    repo_id, private = args[0], "--private" in sys.argv
    build = assemble()
    from huggingface_hub import HfApi, whoami
    try:
        whoami()
    except Exception:
        print("!! Not logged in. Run:  huggingface-cli login")
        sys.exit(1)
    api = HfApi()
    api.create_repo(repo_id, repo_type="model", private=private, exist_ok=True)
    api.upload_folder(folder_path=str(build), repo_id=repo_id, repo_type="model",
                      commit_message="YOLO+ hierarchical perception: card + runnable code")
    print(f">>> done: https://huggingface.co/{repo_id}")


if __name__ == "__main__":
    main()
