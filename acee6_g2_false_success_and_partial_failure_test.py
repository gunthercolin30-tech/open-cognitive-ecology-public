from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory

import ontology.acee_rollback_engine as rollback_module
from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload
from ontology.acee_installation_executor import AceeInstallationExecutor


class FalseSuccessRollback:
    def __init__(self, root: Path):
        self.root = root

    def step(self, inputs=None, persist=False):
        return {
            "rollback_performed": True,
            "status": "ACEE11_ROLLBACK_COMPLETE",
        }


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        target = root / "ontology" / "sample_candidate.py"
        target.write_text("ORIGINAL = 1\n", encoding="utf-8")

        inputs = payload(root)
        context = dict(inputs["admission_context"])
        context["requested_stage"] = "ACEE6-D2"
        context["fault_injection"] = {
            "enabled": True,
            "point": "write",
            "occurrence": 1,
            "execute_rollback": False,
        }
        inputs["admission_context"] = context
        engine = AceeInstallationExecutor(root=root, now_utc=fixed_now())
        g1 = engine.step(inputs=inputs, persist=True)
        assert g1["transaction_state"] == "FAULT_INJECTED", g1

        original_class = rollback_module.AceeRollbackEngine
        rollback_module.AceeRollbackEngine = FalseSuccessRollback
        try:
            result = engine._g2_rollback_fault(g1)
        finally:
            rollback_module.AceeRollbackEngine = original_class

        assert result["transaction_state"] == "QUARANTINE", result
        assert result["rollback_verified"] is False, result
        assert result["quarantined"] is True, result
        assert result["committed"] is False, result
        assert result["partial_success"] is False, result
        assert result["retry_allowed"] is False, result
        assert "target_restore_not_verified" in result["blocking_reasons"], result
    print("ACEE6_G2_FALSE_SUCCESS_AND_PARTIAL_FAILURE_OK")


if __name__ == "__main__":
    main()
