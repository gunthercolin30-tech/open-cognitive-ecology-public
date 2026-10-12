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
    make_transaction(e, "tx-priority", "QUARANTINE", rollback_executed=True, rollback_verified=False)
    e.escalate_transaction("tx-priority", persist=True)
    (root / "acee6_transactions" / "tx-priority" / "journal.jsonl").write_text("not-json\n", encoding="utf-8")
    original = e._admit_and_dry_run
    def forbidden(*args, **kwargs):
        raise AssertionError("admission_must_not_run_while_gate_is_active")
    e._admit_and_dry_run = forbidden
    result = e.step(inputs={}, persist=False)
    e._admit_and_dry_run = original
    assert result["status"] == "ACEE6_J2_INSTALLATION_BLOCKED"
    assert result["candidate_executed"] is False
print("ACEE6_J2_GATE_PRIORITY_OK")
