import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence" / "p001"
EVIDENCE.mkdir(parents=True, exist_ok=True)

tests = [
    "p001_objective_director_functional_test.py",
    "p001_objective_director_degradation_test.py",
    "p001_objective_director_non_regression_test.py",
    "p001_objective_director_cwd_test.py",
]
results = []
for name in tests:
    proc = subprocess.run(
        [sys.executable, str(ROOT / name)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    results.append({
        "test": name,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    })
    if proc.returncode != 0:
        print(json.dumps(results, indent=2))
        raise SystemExit(2)

from validation.p001_objective_director import audit
audit_result = audit(ROOT)
if audit_result["decision"] != "P001_REPRESENTABLE":
    raise SystemExit(3)

protected = [
    ROOT / "validation" / "p001_objective_director.py",
    *(ROOT / name for name in tests),
]
hashes = {}
for path in protected:
    hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

report = {
    "canonical_id": "P001",
    "status": "LOCKED",
    "lock_scope": "P001 functional architectural representability only",
    "functional_only": True,
    "phenomenology_undetermined": True,
    "audit": audit_result,
    "tests": results,
    "protected_hashes": hashes,
    "baseline_comparison_status": "DEFERRED_TO_P007",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
}
stable = dict(report)
stable.pop("lock_hash", None)
report["lock_hash"] = hashlib.sha256(
    json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

path = EVIDENCE / "p001_final_lock_report.json"
path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print("P001_FINAL_LOCK_OK")
print(f"report={path}")
print(f"lock_hash={report['lock_hash']}")
