from __future__ import annotations
import tempfile
from pathlib import Path
from acee6_k5_transaction_runner import execute_one
from acee6_k5_transaction_support import seed

with tempfile.TemporaryDirectory(prefix="acee6_k5_collision_fixture_test_") as tmp:
    root = Path(tmp) / "sandbox"
    root.mkdir(parents=True, exist_ok=True)
    seed(root)
    record = execute_one(root, "collision", 96)

assert record["expected_state"] == "STATE_CORRUPTED", record
assert record["observed_state"] == "STATE_CORRUPTED", record
assert record["ok"] is True, record
projection = record["projection"]
assert projection.get("committed") is not True, record
assert projection.get("candidate_written") is not True, record
assert projection.get("persistence_performed") is not True, record
assert projection.get("partial_success") is not True, record
reasons = projection.get("blocking_reasons") or []
assert any("divergence" in str(reason) for reason in reasons), record
print("ACEE6_K5_COLLISION_FIXTURE_OK")
