from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "p015_official_dna_definition_report.json"

def digest():
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()

def main():
    cmd = [sys.executable, "-m", "validation.p015_official_dna_definition"]
    subprocess.run(cmd, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    first = digest()
    subprocess.run(cmd, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    second = digest()
    assert first == second
    print("P015_DETERMINISM_TEST_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
