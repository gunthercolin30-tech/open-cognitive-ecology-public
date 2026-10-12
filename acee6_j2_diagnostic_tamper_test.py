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
    make_transaction(e, "tx-tamper", "QUARANTINE", rollback_executed=True, rollback_verified=False)
    result = e.escalate_transaction("tx-tamper", persist=True)
    diagnostic_path = Path(result["diagnostic_path"])
    diagnostic = json.loads(diagnostic_path.read_text())
    diagnostic["blocking_reasons"] = ["forged"]
    diagnostic_path.write_text(json.dumps(diagnostic), encoding="utf-8")
    inspected = e.inspect_escalation_gate()
    assert inspected["installation_blocked"] is True
    assert inspected["gate_integrity_verified"] is True
    assert inspected["diagnostic_integrity_verified"] is False
    assert "escalation_diagnostic_corrupted" in inspected["blocking_reasons"]
print("ACEE6_J2_DIAGNOSTIC_TAMPER_OK")
