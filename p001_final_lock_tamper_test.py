from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "evidence" / "p001" / "p001_final_lock_report.json"
CHECKER = ROOT / "p001_final_lock_integrity_check.py"

report = json.loads(REPORT.read_text(encoding="utf-8"))
protected = sorted(report["protected_hashes"])
assert protected

with tempfile.TemporaryDirectory() as td:
    fake = Path(td)
    (fake / "evidence" / "p001").mkdir(parents=True)
    shutil.copy2(REPORT, fake / "evidence" / "p001" / REPORT.name)
    shutil.copy2(CHECKER, fake / CHECKER.name)

    for rel in protected:
        src = ROOT / rel
        dst = fake / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    victim = fake / protected[0]
    victim.write_bytes(victim.read_bytes() + b"\n# adversarial tamper\n")

    proc = subprocess.run(
        [sys.executable, str(fake / CHECKER.name)],
        cwd=str(fake),
        text=True,
        capture_output=True,
    )
    assert proc.returncode != 0
    assert "P001_FINAL_LOCK_INTEGRITY_FAIL" in (proc.stdout + proc.stderr)

print("P001_CROWN_FINAL_LOCK_TAMPER_OK")
