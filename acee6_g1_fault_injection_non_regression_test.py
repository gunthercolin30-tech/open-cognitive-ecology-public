from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_installation_executor import AceeInstallationExecutor


def main() -> None:
    with TemporaryDirectory() as tmp:
        executor = AceeInstallationExecutor(root=Path(tmp))
        original = {
            "primitive": "ACEE_INSTALLATION_EXECUTOR",
            "stage": "ACEE6-F2",
            "status": "ACEE6_GLOBAL_VALIDATION_COMPLETE",
            "transaction_state": "GLOBALLY_VALIDATED",
            "global_validation_passed": True,
            "committed": False,
        }
        for boundary in ("backup", "write", "compile", "inventory", "tests", "validation.main", "report"):
            assert executor._fault_injection_boundary(original, None, boundary) == original
            assert executor._fault_injection_boundary(original, {}, boundary) == original
        assert executor.step(inputs={}, persist=False)["status"] == "ACEE6_INSTALLATION_PLAN_REJECTED"
    print("ACEE6_G1_FAULT_INJECTION_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
