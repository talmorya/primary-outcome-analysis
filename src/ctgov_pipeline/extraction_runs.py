"""Locate CT.gov full extraction run directories."""

from __future__ import annotations

import json
from pathlib import Path

from .config_loader import PROJECT_ROOT


def list_full_extraction_run_ids() -> list[str]:
    root = PROJECT_ROOT / "data" / "raw" / "full"
    if not root.is_dir():
        return []
    runs = []
    for path in root.iterdir():
        if path.is_dir() and (path / "studies").is_dir() and any(path.glob("studies/*.json")):
            runs.append(path.name)
    return sorted(runs)


def latest_full_extraction_run_id() -> str | None:
    runs = list_full_extraction_run_ids()
    return runs[-1] if runs else None


def read_extraction_manifest(run_id: str) -> dict:
    path = PROJECT_ROOT / "data" / "raw" / "full" / run_id / "extraction_manifest.json"
    if not path.is_file():
        path = PROJECT_ROOT / "data" / "processed" / "full" / run_id / "extraction_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))
