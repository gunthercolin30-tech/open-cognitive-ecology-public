from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.acee_validation_runner import AceeValidationRunner


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        root.mkdir()

        marker = root / "should_not_exist.txt"

        result = AceeValidationRunner(root=root).step(
            inputs={
                "validation_id": "disallowed-command",
                "scope": "acee7",
                "mode": "targeted",
                "execute_commands": True,
                "commands": [
                    {
                        "name": "forbidden",
                        "argv": [
                            "bash",
                            "-c",
                            f"printf RUN > {marker}",
                        ],
                        "timeout_seconds": 5.0,
                    }
                ],
            },
            persist=False,
        )

        assert result["validation_passed"] is False
        assert result["rollback_required"] is True
        assert result["validation_status"] in {
            "ACEE_VALIDATION_BLOCKED",
            "ACEE_VALIDATION_FAILED",
        }
        assert marker.exists() is False
        assert len(result["command_results"]) == 1

    print("ACEE7_DISALLOWED_COMMAND_BLOCKED_OK")


if __name__ == "__main__":
    main()
