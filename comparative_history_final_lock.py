from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.comparative_dashboard import ComparativeDashboard
from ontology.comparative_history import ComparativeHistory

READY_OR_SYNTHETIC_CONTEXT = {
    "comparative_dashboard": ComparativeDashboard().step(inputs={}, persist=False),
}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="oce_au9_lock_") as tmp:
        result = ComparativeHistory(root=Path(tmp)).step(
            inputs=READY_OR_SYNTHETIC_CONTEXT,
            persist=False,
        )
    assert result["step"] == "AU9"
    assert result["comparative_history_status"] == "COMPARATIVE_HISTORY_READY"
    assert result["comparative_history_ready"] is True
    assert result["dashboard_ready"] is True
    assert result["append_only"] is True
    assert result["change_set"]["change_type"] == "INITIAL_SNAPSHOT"
    assert len(result["snapshot_hash"]) == 64
    assert result["chain_integrity"]["chain_valid"] is True
    assert result["persisted"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    print("AU9_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
