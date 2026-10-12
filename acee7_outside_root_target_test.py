from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.acee_validation_runner import AceeValidationRunner


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        root = base / "root"
        root.mkdir()

        marker = root / "should_not_exist.txt"
        outside = base / "outside_test.py"

        outside.write_text(
            "from pathlib import Path\n"
            + "Path("
            + repr(str(marker))
            + ").write_text('RUN', encoding='utf-8')\n",
            encoding="utf-8",
        )

        result = AceeValidationRunner(root=root).step(
            inputs={
                "validation_id": "outside-root",
                "scope": "acee7",
                "mode": "targeted",
                "execute_commands": True,
                "commands": [
                    {
                        "name": "outside_test",
                        "argv": [
                            "python3",
                            str(outside),
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

    print("ACEE7_OUTSIDE_ROOT_TARGET_BLOCKED_OK")


if __name__ == "__main__":
    main()
