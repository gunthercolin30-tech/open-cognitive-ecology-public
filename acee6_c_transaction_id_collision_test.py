from pathlib import Path
from tempfile import TemporaryDirectory

from acee5_hardening_test_support import valid_context
from acee6_b1_test_support import fixed_now
from ontology.acee_governed_code_generation_gate import (
    AceeGovernedCodeGenerationGate,
)
from ontology.acee_installation_executor import AceeInstallationExecutor


class ForcedCollisionExecutor(AceeInstallationExecutor):
    def _transaction_id(self, result):
        return "acee6c-forced-collision"


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    first_decision = AceeGovernedCodeGenerationGate(root=root).step(
        inputs=valid_context(root, candidate_hash="a" * 64),
        persist=False,
    )
    second_decision = AceeGovernedCodeGenerationGate(root=root).step(
        inputs=valid_context(root, candidate_hash="b" * 64),
        persist=False,
    )

    executor = ForcedCollisionExecutor(root=root, now_utc=fixed_now())
    first = executor.step(inputs=first_decision, persist=True)
    assert first["transaction_state"] == "PREPARED"

    second = executor.step(inputs=second_decision, persist=True)
    assert second["transaction_prepared"] is False
    assert second["transaction_state"] == "STATE_CORRUPTED"
    assert second["status"] == "ACEE6_TRANSACTION_PREPARATION_REJECTED"
    assert "existing_transaction_plan_divergence" in (
        second["blocking_reasons"]
    )
    assert second["candidate_written"] is False

print("ACEE6_C_TRANSACTION_ID_COLLISION_OK")
