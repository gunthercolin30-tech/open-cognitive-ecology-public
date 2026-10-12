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
    make_transaction(e, "tx-restart", "QUARANTINE", rollback_executed=True, rollback_verified=False)
    first = e.escalate_transaction("tx-restart", persist=True)
    gate_bytes = Path(first["gate_path"]).read_bytes()
    hashes = []
    for day in range(1, 4):
        restarted = AceeInstallationExecutor(root=root, now_utc=e.now_utc + timedelta(days=day))
        inspected = restarted.inspect_escalation_gate()
        replay = restarted.escalate_transaction("tx-restart", persist=True)
        assert inspected["installation_blocked"] is True
        assert replay["escalation_replayed"] is True
        assert Path(first["gate_path"]).read_bytes() == gate_bytes
        hashes.append(replay["gate_hash"])
    assert len(set(hashes)) == 1
print("ACEE6_J2_RESTART_PERSISTENCE_OK")
