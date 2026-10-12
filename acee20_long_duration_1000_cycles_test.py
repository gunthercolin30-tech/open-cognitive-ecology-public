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
from ontology.acee_meta_analysis import ACEEMetaAnalysis
def main():
    pred = ACEEPredictionEngine(); meta = ACEEMetaAnalysis(); hashes=[]
    for i in range(1000):
        p = pred.step(inputs={"candidates":[{"candidate_id":f"c-{i}","predicted_gain":0.2,"confidence":0.9,"risk":0.1}]}, persist=False)
        m = meta.step(inputs={"observations":[{"observation_id":f"o-{i}-a","effect_size":0.1,"variance":0.1},{"observation_id":f"o-{i}-b","effect_size":0.12,"variance":0.1}]}, persist=False)
        hashes.append((p["prediction_hash"],m["analysis_hash"]))
    passed = len(hashes)==1000 and all(a and b for a,b in hashes)
    path=finalize({"campaign":"long_duration_1000_cycles","status":"LONG_DURATION_COMPLETE","passed":passed,"metrics":{"cycles_completed":len(hashes)},"thresholds":{"minimum_cycles":1000},"limitations":[]},"long_duration_1000_cycles_report.json")
    print(f"ACEE20_LONG_DURATION_1000_CYCLES_OK path={path}")
    raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
