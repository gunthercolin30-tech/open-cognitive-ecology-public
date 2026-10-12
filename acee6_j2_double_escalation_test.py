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
    e1 = executor(root)
    make_transaction(e1, "tx-double", "QUARANTINE", rollback_executed=True, rollback_verified=False)
    first = e1.escalate_transaction("tx-double", persist=True)
    gate_path = Path(first["gate_path"])
    diag_path = Path(first["diagnostic_path"])
    gate_before = gate_path.read_bytes()
    diag_before = diag_path.read_bytes()
    e2 = AceeInstallationExecutor(root=root, now_utc=e1.now_utc + timedelta(days=1))
    second = e2.escalate_transaction("tx-double", persist=True)
    assert second["status"] == "ACEE6_J2_ESCALATION_COMPLETE"
    assert second["escalation_replayed"] is True
    assert second["persistence_performed"] is False
    assert gate_path.read_bytes() == gate_before
    assert diag_path.read_bytes() == diag_before
print("ACEE6_J2_DOUBLE_ESCALATION_OK")
