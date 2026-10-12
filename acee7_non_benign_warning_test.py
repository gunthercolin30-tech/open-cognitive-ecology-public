from __future__ import annotations

from ontology.acee_validation_runner import AceeValidationRunner


def main() -> None:
    result = AceeValidationRunner().step(
        inputs={
            "validation_id": "non-benign-warning",
            "scope": "acee7",
            "mode": "targeted",
            "command_results": [
                {
                    "name": "warning_case",
                    "returncode": 0,
                    "stdout": "OK",
                    "stderr": (
                        "SecurityWarning: validation evidence "
                        "integrity uncertain"
                    ),
                    "duration_seconds": 0.1,
                }
            ],
        },
        persist=False,
    )

    assert result["warning_count"] >= 1
    assert any(
        "SecurityWarning" in warning
        for warning in result["non_benign_warnings"]
    )

    print("ACEE7_NON_BENIGN_WARNING_CLASSIFIED_OK")


if __name__ == "__main__":
    main()
