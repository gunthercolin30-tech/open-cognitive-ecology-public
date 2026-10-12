from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.reflexive_threshold_history_archive import ReflexiveThresholdHistoryArchive


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="oce_x1_lock_") as tmp:
        result = ReflexiveThresholdHistoryArchive(Path(tmp)).step(
            inputs={
                "run_id": "X1-FINAL-LOCK",
                "timestamp_utc": "2026-01-01T00:00:00+00:00",
            },
            persist=False,
        )

    assert result["primitive"] == "REFLEXIVE_THRESHOLD_HISTORY_ARCHIVE"
    assert result["stage"] == "X1"
    assert result["success"] is True
    assert result["stages_expected"] == 14
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["phenomenal_conclusion"] is False
    print("REFLEXIVE_THRESHOLD_HISTORY_RUNTIME_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
