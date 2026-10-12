from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from acee6_j2_test_support import executor, make_transaction
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    e = executor(root)
    tx = make_transaction(e, "tx-legacy", "COMMITTED")
    before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    gate = e.inspect_escalation_gate()
    result = e.escalate_transaction("tx-legacy", persist=True)
    after = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert gate["installation_blocked"] is False
    assert result["status"] == "ACEE6_J2_ESCALATION_NOT_REQUIRED"
    assert before == after
print("ACEE6_J2_LEGACY_COMPATIBILITY_OK")
