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

def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        h.update(path.relative_to(root).as_posix().encode())
        h.update(path.read_bytes())
    return h.hexdigest()
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    e = executor(root)
    make_transaction(e, "tx-audit", "QUARANTINE", rollback_executed=True, rollback_verified=False)
    before = tree_hash(root)
    result = e.escalate_transaction("tx-audit", persist=False)
    after = tree_hash(root)
    assert result["persistence_performed"] is False
    assert before == after
    assert not e._j2_gate_path().exists()
print("ACEE6_J2_PERSIST_FALSE_TREE_HASH_OK")
