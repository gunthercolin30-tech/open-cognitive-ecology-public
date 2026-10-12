from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMANDS = (
    ("fast_acceptance", [sys.executable, "p007_fast_acceptance_suite.py"], "P007_FAST_ACCEPTANCE_OK"),
    ("final_lock", [sys.executable, "p007_final_lock.py"], "P007_FINAL_LOCK_OK"),
)
results = []
for name, command, marker in COMMANDS:
    p = subprocess.run(
        command, cwd=str(ROOT), text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    print(p.stdout or "", end="")
    ok = p.returncode == 0 and marker in (p.stdout or "")
    results.append({"name": name, "returncode": p.returncode, "marker": marker, "ok": ok})
    if not ok:
        raise SystemExit(p.returncode or 3)

lock = json.loads((ROOT / "p007_final_lock_report.json").read_text(encoding="utf-8"))
report = {
    "milestone": "P007",
    "gate": "G0_BASELINE_INTEGRITY",
    "status": "PASSED",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "baseline_identity_sha256": lock["baseline_identity_sha256"],
    "results": results,
    "functional_only": True,
    "phenomenology_undetermined": True,
}
path = ROOT / "p007_campaign_report.json"
tmp = path.with_suffix(path.suffix + ".tmp")
tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
tmp.replace(path)
print("P007_CAMPAIGN_OK")
