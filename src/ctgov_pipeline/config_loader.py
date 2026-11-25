"""Load YAML config files from the project config directory.

Workspaces: by default all data and outputs live in the project (`data/`, `analysis/`, `docs/`). Setting the
environment variable `CTGOV_WORKSPACE` to another directory redirects every read/write of data and outputs to
that directory (used for side analyses such as `chronic_pain_condition_addition/`, which never touches the
main results). A workspace may hold a `config/` directory whose YAML files are merged over the project config
(dicts merged key by key, anything else replaced), so a side analysis only states what it changes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
WORKSPACE_ROOT = Path(os.environ["CTGOV_WORKSPACE"]).resolve() if os.environ.get("CTGOV_WORKSPACE") else PROJECT_ROOT
IS_SIDE_WORKSPACE = WORKSPACE_ROOT != PROJECT_ROOT


def _merge(base: Any, overlay: Any) -> Any:
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = dict(base)
        for key, value in overlay.items():
            merged[key] = _merge(base[key], value) if key in base else value
        return merged
    return overlay


def load_yaml(name: str | Path) -> dict[str, Any]:
    path = CONFIG_DIR / name
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    overlay_path = WORKSPACE_ROOT / "config" / name
    if IS_SIDE_WORKSPACE and not Path(name).is_absolute() and overlay_path.is_file():
        with overlay_path.open(encoding="utf-8") as handle:
            config = _merge(config, yaml.safe_load(handle))
    return config


def config_hash(config: dict[str, Any]) -> str:
    return json.dumps(config, sort_keys=True)
