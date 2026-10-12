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

import json, os, subprocess, sys
def main():
    env=os.environ.copy(); env["OCE_FULL_VALIDATION"]="1"
    cp=subprocess.run([sys.executable,"-m","validation.main"],cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    report_path=ROOT/"scientific_validation_report.json"; report={}
    if report_path.exists(): report=json.loads(report_path.read_text(encoding="utf-8"))
    diagnostics=report.get("diagnostics",{}); summary=report.get("summary",{})
    passed=cp.returncode==0 and summary.get("overall_success") is True and diagnostics.get("error_count")==0 and diagnostics.get("failed_calls")==0 and diagnostics.get("timeouts")==0 and not diagnostics.get("failed_modules")
    path=finalize({"campaign":"global_validation","status":"GLOBAL_VALIDATION_COMPLETE","passed":passed,"metrics":{"returncode":cp.returncode,"diagnostics":diagnostics,"summary":summary,"output_tail":cp.stdout[-4000:]},"thresholds":{"overall_success":True,"error_count":0,"failed_calls":0,"timeouts":0,"failed_modules":[]},"limitations":[]},"global_validation_report.json")
    print(f"ACEE20_GLOBAL_VALIDATION_OK path={path}")
    raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
