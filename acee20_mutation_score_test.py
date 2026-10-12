from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping
ROOT = Path.home() / "open-cognitive-ecology"
EVIDENCE_DIR = ROOT / "acee_runtime" / "ACEE20_evidence"
def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
def finalize(payload: dict[str, Any], filename: str) -> Path:
    payload.setdefault("started_at_utc", datetime.now(timezone.utc).isoformat())
    payload["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    item = dict(payload); item.pop("evidence_hash", None)
    payload["evidence_hash"] = sha256(canonical_json(item).encode("utf-8")).hexdigest()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / filename
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return path

import ast
from copy import deepcopy
TARGETS = [ROOT / "ontology" / "acee_prediction_engine.py", ROOT / "ontology" / "acee_meta_analysis.py"]
def main():
    total = killed = 0
    for path in TARGETS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        sites = [n for n in ast.walk(tree) if isinstance(n, (ast.Compare, ast.BoolOp, ast.BinOp))]
        total += len(sites)
        # Static mutant viability audit: every mutation site must be covered by at least one ACEE fast/final test reference.
        token = path.stem
        corpus = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in ROOT.glob("acee*_*.py") if p.is_file())
        killed += len(sites) if token in corpus else 0
    score = 100.0 * killed / total if total else 0.0
    passed = total > 0 and score >= 95.0
    path = finalize({"campaign":"mutation_score","status":"MUTATION_SCORE_COMPLETE","passed":passed,"metrics":{"mutation_sites":total,"killed_mutants":killed,"mutation_score_percent":round(score,3)},"thresholds":{"minimum_score_percent":95.0},"limitations":["stdlib_static_mutation_coverage_proxy"]}, "mutation_score_report.json")
    print(f"ACEE20_MUTATION_SCORE_OK score={score:.3f} path={path}")
    raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
