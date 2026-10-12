from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from acee6_k4_resource_runner import verify_report
ROOT = Path.home() / "open-cognitive-ecology"
subprocess.run([sys.executable, str(ROOT / "acee6_k3_final_lock.py")], cwd=str(ROOT), check=True, timeout=300)
subprocess.run([sys.executable, str(ROOT / "acee6_k4_fast_acceptance_suite.py")], cwd=str(ROOT), check=True, timeout=300)
path = ROOT / "acee6_k_evidence" / "acee6_k4_resource_report.json"
assert path.is_file(), "K4 evidence report missing"
report = json.loads(path.read_text(encoding="utf-8"))
verification = verify_report(report)
assert verification["valid"], verification
print("ACEE6_K4_FINAL_LOCK_OK")
