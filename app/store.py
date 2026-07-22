from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

@lru_cache(maxsize=1)
def load_rules() -> list[dict[str, Any]]:
    return json.loads((DATA / "rules.json").read_text(encoding="utf-8"))

@lru_cache(maxsize=1)
def load_case() -> dict[str, Any]:
    return json.loads((DATA / "demo_case.json").read_text(encoding="utf-8"))

@lru_cache(maxsize=1)
def load_queue() -> list[dict[str, Any]]:
    return json.loads((DATA / "case_queue.json").read_text(encoding="utf-8"))
