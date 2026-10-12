from __future__ import annotations
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
        }
        inputs["admission_context"] = context
        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
            inputs=inputs, persist=True
        )
        assert result["stage"] == "ACEE6-G1", result
        assert result["transaction_state"] == "FAULT_INJECTED", result
        assert result["rollback_executed"] is False, result
        assert result["rollback_required"] is True, result
        assert result["quarantined"] is False, result
    print("ACEE6_G2_GOVERNED_ROLLBACK_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
