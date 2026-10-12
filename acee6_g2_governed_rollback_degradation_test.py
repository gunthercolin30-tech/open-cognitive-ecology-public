from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_installation_executor import AceeInstallationExecutor
from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
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
        assert g1["transaction_state"] == "FAULT_INJECTED"
        tx = root / "acee6_transactions" / g1["transaction_id"]
        (tx / "backup_manifest.json").unlink()
        degraded = engine._g2_rollback_fault(g1)
        assert degraded["transaction_state"] == "QUARANTINE", degraded
        assert degraded["rollback_verified"] is False, degraded
        assert degraded["quarantined"] is True, degraded
        assert degraded["committed"] is False, degraded
        assert degraded["partial_success"] is False, degraded
        assert "backup_manifest_missing" in degraded["blocking_reasons"]
    print("ACEE6_G2_GOVERNED_ROLLBACK_DEGRADATION_OK")


if __name__ == "__main__":
    main()
