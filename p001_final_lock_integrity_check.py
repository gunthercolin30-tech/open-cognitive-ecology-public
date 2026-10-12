from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "evidence" / "p001" / "p001_final_lock_report.json"

if not REPORT.is_file():
    raise SystemExit("P001_FINAL_LOCK_INTEGRITY_FAIL missing_report")

report = json.loads(REPORT.read_text(encoding="utf-8"))
if report.get("status") != "LOCKED":
    raise SystemExit("P001_FINAL_LOCK_INTEGRITY_FAIL status")

expected = report.get("protected_hashes")
if not isinstance(expected, dict) or not expected:
    raise SystemExit("P001_FINAL_LOCK_INTEGRITY_FAIL protected_hashes")

for rel, wanted in sorted(expected.items()):
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f"P001_FINAL_LOCK_INTEGRITY_FAIL missing:{rel}")
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != wanted:
        raise SystemExit(
            f"P001_FINAL_LOCK_INTEGRITY_FAIL tamper:{rel} expected={wanted} got={got}"
        )

print("P001_FINAL_LOCK_INTEGRITY_OK")
