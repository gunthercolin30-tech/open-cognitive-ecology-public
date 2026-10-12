from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.acee_validation_runner import AceeValidationRunner


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        root.mkdir()

        script = root / "large_output_test.py"
        script.write_text(
            "print('X' * 500000)\n",
            encoding="utf-8",
        )

        result = AceeValidationRunner(root=root).step(
            inputs={
                "validation_id": "large-output",
                "scope": "acee7",
                "mode": "targeted",
                "execute_commands": True,
                "commands": [
                    {
                        "name": "large_output",
                        "argv": [
                            "python3",
                            str(script),
                        ],
                        "timeout_seconds": 10.0,
                    }
                ],
            },
            persist=False,
        )

        command = result["command_results"][0]

        assert command["returncode"] == 0
        assert command["timed_out"] is False
        assert result["validation_passed"] is True

    print("ACEE7_LARGE_OUTPUT_OK")


if __name__ == "__main__":
    main()
