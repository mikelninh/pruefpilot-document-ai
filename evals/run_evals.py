from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.retrieval import BM25Retriever
from app.store import load_rules

def main() -> int:
    cases = json.loads((ROOT / "evals" / "eval_cases.json").read_text(encoding="utf-8"))
    retriever = BM25Retriever(load_rules())
    passed = 0
    rows = []
    for case in cases:
        results = retriever.search(case["question"], limit=1)
        got = results[0][0]["id"] if results else None
        ok = got == case["expected_source"]
        passed += int(ok)
        rows.append({"question": case["question"], "expected": case["expected_source"], "got": got, "passed": ok})
    output = {"passed": passed, "total": len(cases), "results": rows}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if passed == len(cases) else 1

if __name__ == "__main__":
    raise SystemExit(main())
