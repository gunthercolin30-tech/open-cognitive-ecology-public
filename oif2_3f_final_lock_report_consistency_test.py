from __future__ import annotations
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "oif2_3f_operational_navigation_final_lock_report.json"
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["status"] == "locked"
    assert report["primitive"] == "oif2_operational_navigation_layer"
    assert report["consciousness_proven"] is False
    assert report["functional_conclusion_only"] is True
    for rel, expected in report["sha256"].items(): assert digest(ROOT / rel) == expected, rel
    print("OIF2_3F_FINAL_LOCK_REPORT_CONSISTENCY_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())
