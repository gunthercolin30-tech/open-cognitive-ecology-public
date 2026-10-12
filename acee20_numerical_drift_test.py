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

import math
from ontology.acee_meta_analysis import ACEEMetaAnalysis
def main():
    engine=ACEEMetaAnalysis(); values=[]
    inputs={"observations":[{"observation_id":"a","effect_size":0.2,"variance":0.04},{"observation_id":"b","effect_size":0.4,"variance":0.01}]}
    for _ in range(1000): values.append(engine.step(inputs=inputs,persist=False)["pooled_effect"])
    drift=max(values)-min(values); passed=all(math.isfinite(v) for v in values) and drift<=1e-12
    path=finalize({"campaign":"numerical_drift","status":"NUMERICAL_DRIFT_COMPLETE","passed":passed,"metrics":{"minimum":min(values),"maximum":max(values),"drift":drift},"thresholds":{"maximum_drift":1e-12},"limitations":[]},"numerical_drift_report.json")
    print(f"ACEE20_NUMERICAL_DRIFT_OK drift={drift} path={path}")
    raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
