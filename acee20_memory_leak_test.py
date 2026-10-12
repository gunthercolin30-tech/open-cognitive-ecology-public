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

import gc, tracemalloc
from ontology.acee_prediction_engine import ACEEPredictionEngine
def main():
    tracemalloc.start(); samples=[]; engine=ACEEPredictionEngine()
    for i in range(300):
        engine.step(inputs={"candidates":[{"candidate_id":f"m-{i}","predicted_gain":0.2}]}, persist=False)
        if i%25==0: gc.collect(); samples.append(tracemalloc.get_traced_memory()[0])
    tracemalloc.stop(); growth=samples[-1]-samples[0] if len(samples)>1 else 0
    passed=growth <= 2_000_000
    path=finalize({"campaign":"memory_leak","status":"MEMORY_LEAK_CHECK_COMPLETE","passed":passed,"metrics":{"samples_bytes":samples,"net_growth_bytes":growth},"thresholds":{"maximum_net_growth_bytes":2000000},"limitations":["allocator_noise_tolerated"]},"memory_leak_report.json")
    print(f"ACEE20_MEMORY_LEAK_OK growth={growth} path={path}")
    raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
