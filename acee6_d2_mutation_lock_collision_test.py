import fcntl
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import (
    AceeGovernedCodeGenerationGate,
)
from ontology.acee_installation_executor import AceeInstallationExecutor


content = "locked mutation\n"
content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    decision = AceeGovernedCodeGenerationGate(root=root).step(
        inputs=valid_context(root, candidate_hash=content_hash),
        persist=False,
    )
    inputs = {
        "acee5_decision": decision,
        "admission_context": {
            "requested_stage": "ACEE6-D2",
            "candidate_content": content,
        },
    }

    runtime = root / "acee6_transactions"
    runtime.mkdir()
    lock_path = runtime / ".mutation.lock"

    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        result = AceeInstallationExecutor(
            root=root,
            now_utc=fixed_now(),
        ).step(inputs=inputs, persist=True)
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    assert result["status"] == "ACEE6_TRANSACTION_MUTATION_BLOCKED"
    assert result["transaction_state"] == "BACKED_UP"
    assert "transaction_mutation_lock_busy" in result["blocking_reasons"]
    assert result["candidate_written"] is False

print("ACEE6_D2_MUTATION_LOCK_COLLISION_OK")
