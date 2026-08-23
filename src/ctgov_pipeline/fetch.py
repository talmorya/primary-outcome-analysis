"""Fetch studies from ClinicalTrials.gov API v2."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests

API_BASE = "https://clinicaltrials.gov/api/v2"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "primary-outcome-analysis/0.1"})


def get_api_version() -> dict[str, Any]:
    response = SESSION.get(f"{API_BASE}/version", timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_study(nct_id: str) -> dict[str, Any]:
    response = SESSION.get(f"{API_BASE}/studies/{nct_id}", params={"format": "json"}, timeout=60)
    response.raise_for_status()
    return response.json()


def search_studies(params: dict[str, str | int]) -> dict[str, Any]:
    response = SESSION.get(f"{API_BASE}/studies", params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def search_all_studies(
    params: dict[str, str | int],
    *,
    max_pages: int | None = None,
    pause_seconds: float = 0.2,
) -> list[dict[str, Any]]:
    studies: list[dict[str, Any]] = []
    page_params = dict(params)
    page = 0
    while True:
        payload = search_studies(page_params)
        studies.extend(payload.get("studies", []))
        page += 1
        token = payload.get("nextPageToken")
        if not token or (max_pages is not None and page >= max_pages):
            break
        page_params["pageToken"] = token
        time.sleep(pause_seconds)
    return studies


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def fetch_and_save_studies(
    nct_ids: list[str],
    output_dir: Path,
    *,
    pause_seconds: float = 0.2,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "nct_ids": nct_ids,
        "saved": [],
        "errors": [],
    }
    for nct_id in nct_ids:
        target = output_dir / f"{nct_id}.json"
        try:
            study = fetch_study(nct_id)
            save_json(study, target)
            manifest["saved"].append(nct_id)
        except requests.RequestException as exc:
            manifest["errors"].append({"nct_id": nct_id, "error": str(exc)})
        time.sleep(pause_seconds)
    save_json(manifest, output_dir / "manifest.json")
    return manifest
