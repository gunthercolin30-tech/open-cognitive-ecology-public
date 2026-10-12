from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_installation_executor import AceeInstallationExecutor


def main() -> None:
    with TemporaryDirectory() as tmp:
        executor = AceeInstallationExecutor(root=Path(tmp))
        baseline = {
            "primitive": "ACEE_INSTALLATION_EXECUTOR",
            "transaction_id": "tx-degradation",
            "transaction_state": "COMPILED",
        }
        cases = [
            {},
            {"admission_context": {"fault_injection": {"enabled": False, "point": "compile"}}},
            {"admission_context": {"fault_injection": {"enabled": True, "point": "unknown"}}},
            {"admission_context": {"fault_injection": {"enabled": True, "point": ["compile"]}}},
            {"admission_context": {"fault_injection": {"enabled": True, "point": "compile", "occurrence": 0}}},
            {"admission_context": {"fault_injection": {"enabled": True, "point": "compile", "occurrence": 2}}},
        ]
        for inputs in cases:
            result = executor._fault_injection_boundary(baseline, inputs, "compile")
            assert result == baseline
        mismatch = executor._fault_injection_boundary(
            baseline,
            {"admission_context": {"fault_injection": {"enabled": True, "point": "tests", "occurrence": 1}}},
            "compile",
        )
        assert mismatch == baseline
    print("ACEE6_G1_FAULT_INJECTION_DEGRADATION_OK")


if __name__ == "__main__":
    main()
