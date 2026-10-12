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

import subprocess, sys
def main():
    tests=["acee13_hash_chain_restart_test.py","acee16_hash_chain_test.py"]
    results={}; passed=True
    for name in tests:
        path=ROOT/name
        if not path.exists(): results[name]="missing"; passed=False; continue
        cp=subprocess.run([sys.executable,str(path)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        results[name]={"returncode":cp.returncode,"output":cp.stdout[-2000:]}; passed &= cp.returncode==0
    out=finalize({"campaign":"hash_chain_drift","status":"HASH_CHAIN_DRIFT_COMPLETE","passed":bool(passed),"metrics":{"tests":results},"thresholds":{"all_hash_chain_tests_pass":True},"limitations":[]},"hash_chain_drift_report.json")
    print(f"ACEE20_HASH_CHAIN_DRIFT_OK path={out}")
    raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
