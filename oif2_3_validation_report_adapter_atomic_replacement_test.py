from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path

from oif.adapters.validation_report_adapter import (
    ValidationReportAdapter,
    ValidationReportAdapterError,
)


def fixture(name: str, modules: int) -> dict[str, object]:
    return {
        "diagnostics": {
            "modules_discovered": modules,
            "error_count": 0,
            "failed_calls": 0,
            "timeouts": 0,
            "failed_modules": [],
        },
        "metadata": {"elapsed_seconds": 0.1},
        "summary": {
            "overall_success": True,
            "tests_total": 1,
            "tests_passed": 1,
            "tests_failed": 0,
        },
        "tests": [{"name": name, "passed": True}],
        "timestamp_utc": "2026-07-18T06:00:00+00:00",
        "validation_mode": name,
    }


def atomic_write(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload), encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oif2_3_atomic_") as tmp:
        root = Path(tmp)
        source = root / "scientific_validation_report.json"
        first = fixture("first", 1)
        second = fixture("second", 2)
        atomic_write(source, first)
        adapter = ValidationReportAdapter(root=root)

        stop = threading.Event()
        errors: list[BaseException] = []

        def writer() -> None:
            try:
                for index in range(500):
                    atomic_write(source, first if index % 2 == 0 else second)
            except BaseException as exc:
                errors.append(exc)
            finally:
                stop.set()

        thread = threading.Thread(target=writer, daemon=True)
        thread.start()

        observed: set[tuple[str, int]] = set()
        while not stop.is_set():
            try:
                payload = adapter.read()
            except ValidationReportAdapterError as exc:
                errors.append(exc)
                break
            observed.add(
                (payload["validation_mode"], payload["modules_discovered"])
            )

        thread.join(timeout=10)
        assert not thread.is_alive()
        assert not errors, errors
        assert observed.issubset({("first", 1), ("second", 2)})
        assert observed

    print("OIF2_3_ATOMIC_REPLACEMENT_READ_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
