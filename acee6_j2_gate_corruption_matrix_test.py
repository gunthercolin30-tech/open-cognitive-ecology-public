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

cases = [b"{", b"{}", json.dumps({"installation_blocked": True}).encode(), json.dumps({"installation_blocked": True, "gate_hash": "0" * 64}).encode()]
for index, content in enumerate(cases):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        e = executor(root)
        gate = e._j2_gate_path()
        gate.parent.mkdir(parents=True, exist_ok=True)
        gate.write_bytes(content)
        result = e.inspect_escalation_gate()
        assert result["installation_blocked"] is True, (index, result)
        assert result["gate_integrity_verified"] is False, (index, result)
print("ACEE6_J2_GATE_CORRUPTION_MATRIX_OK")
