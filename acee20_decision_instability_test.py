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

from ontology.acee_prediction_engine import ACEEPredictionEngine
def main():
    engine=ACEEPredictionEngine(); inputs={"candidates":[{"candidate_id":"stable-a","predicted_gain":0.2,"confidence":0.9,"risk":0.1},{"candidate_id":"stable-b","predicted_gain":0.1,"confidence":0.8,"risk":0.2}]}
    decisions=[engine.step(inputs=inputs,persist=False)["recommended_candidate_id"] for _ in range(1000)]
    divergence=sum(1 for x in decisions if x!=decisions[0]); passed=divergence==0
    path=finalize({"campaign":"decision_instability","status":"DECISION_INSTABILITY_COMPLETE","passed":passed,"metrics":{"runs":len(decisions),"divergent_decisions":divergence},"thresholds":{"maximum_divergent_decisions":0},"limitations":[]},"decision_instability_report.json")
    print(f"ACEE20_DECISION_INSTABILITY_OK divergence={divergence} path={path}")
    raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
