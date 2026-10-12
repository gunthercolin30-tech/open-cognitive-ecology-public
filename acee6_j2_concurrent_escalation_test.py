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

WORKER = r"""
import sys
from datetime import datetime, timezone
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor
root = Path(sys.argv[1])
e = AceeInstallationExecutor(root=root, now_utc=datetime(2026, 7, 16, tzinfo=timezone.utc))
r = e.escalate_transaction("tx-concurrent", persist=True)
print(r["status"], r.get("escalation_replayed"))
"""
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    e = executor(root)
    make_transaction(e, "tx-concurrent", "QUARANTINE", rollback_executed=True, rollback_verified=False)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent)
    processes = [subprocess.Popen([sys.executable, "-c", WORKER, str(root)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env) for _ in range(6)]
    results = [p.communicate(timeout=60) + (p.returncode,) for p in processes]
    assert all(code == 0 for _, _, code in results), results
    gate = json.loads((root / "acee6_transactions" / "installation_block_gate.json").read_text())
    diagnostic = json.loads(Path(gate["diagnostic_path"]).read_text())
    assert gate["diagnostic_hash"] == diagnostic["diagnostic_hash"]
    assert gate["gate_hash"] == _sha({k: v for k, v in gate.items() if k != "gate_hash"})
    assert diagnostic["diagnostic_hash"] == _sha({k: v for k, v in diagnostic.items() if k != "diagnostic_hash"})
print("ACEE6_J2_CONCURRENT_ESCALATION_OK")
