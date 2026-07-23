from __future__ import annotations

import importlib.util
from pathlib import Path

_CANONICAL = Path(__file__).resolve().parents[2] / "app" / "v5_cases.py"
_SPEC = importlib.util.spec_from_file_location("pruefpilot_canonical_v5_cases", _CANONICAL)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Could not load canonical V5 cases from {_CANONICAL}")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

list_cases = _MODULE.list_cases
get_case = _MODULE.get_case
answer = _MODULE.answer
evidence = _MODULE.evidence
memo = _MODULE.memo
