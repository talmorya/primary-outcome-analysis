"""Map NCT IDs to which API condition searches returned them."""

from __future__ import annotations

import json
from pathlib import Path

from .config_loader import PROJECT_ROOT


def load_api_query_hits(extraction_run_id: str) -> dict[str, list[str]]:
    """For each NCT ID, sorted list of condition search keys (e.g. headache, migraine)."""
    pages_dir = PROJECT_ROOT / "data" / "raw" / "full" / extraction_run_id / "search_pages"
    if not pages_dir.is_dir():
        return {}

    hits: dict[str, set[str]] = {}
    for path in sorted(pages_dir.glob("*_page_*.json")):
        condition_key = path.name.split("_page_")[0]
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for study in payload.get("studies", []):
            nct_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
            if not nct_id:
                continue
            hits.setdefault(nct_id, set()).add(condition_key)

    return {nct: sorted(keys) for nct, keys in hits.items()}
