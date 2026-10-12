from __future__ import annotations
import ast
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "ontology" / "acee_installation_executor.py"
source = MODULE.read_text(encoding="utf-8")
ast.parse(source)
required = [
    "ACEE6-J2-ESCALATION-BEGIN",
    "ACEE6-J2-HARDENING-V1",
    "def escalate_transaction",
    "def inspect_escalation_gate",
    ".j2_escalation.lock",
    "diagnostic_gate_hash_divergence",
]
missing = [token for token in required if token not in source]
assert not missing, missing
for name in ["acee6_j2_fast_acceptance_suite.py", "acee6_j2_extended_hardening_suite.py"]:
    completed = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), text=True, capture_output=True, timeout=360)
    if completed.returncode != 0:
        raise SystemExit(f"{name} failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
    print(completed.stdout.strip())
print("ACEE6_J2_FINAL_LOCK_OK")
