from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.comparative_dashboard import ComparativeDashboard
from ontology.comparative_history import ComparativeHistory
from ontology.comparative_science_certifier import ComparativeScienceCertifier


def main() -> None:
    dashboard = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    with tempfile.TemporaryDirectory(
        prefix="oce_au10_no_change_hash_",
    ) as tmp:
        history_engine = ComparativeHistory(root=Path(tmp))

        first_history = history_engine.step(
            inputs={"comparative_dashboard": dashboard},
            persist=True,
        )
        assert first_history["record_hash"] is not None

        no_change_history = history_engine.step(
            inputs={"comparative_dashboard": dashboard},
            persist=False,
        )

        assert no_change_history["change_set"]["change_type"] == "NO_CHANGE"
        assert no_change_history["record_hash"] is None
        assert no_change_history["chain_integrity"]["chain_valid"] is True

        head_hash = no_change_history["chain_integrity"]["head_hash"]
        assert isinstance(head_hash, str)
        assert len(head_hash) == 64

        sources = ComparativeScienceCertifier()._build_sources()
        sources["comparative_dashboard"] = dashboard
        sources["comparative_history"] = no_change_history

        result = ComparativeScienceCertifier().step(
            inputs=sources,
            persist=False,
        )

        assert result["certification_checks"]["hash_integrity"] is True
        assert result["history_record_hash"] == head_hash
        assert result["history_record_created_in_call"] is False
        assert result["comparative_science_certification_status"] == (
            "COMPARATIVE_RF_SCIENCE_COMPLETE"
        )
        assert result["comparative_rf_science_complete"] is True

    print("AU10_NO_CHANGE_HASH_INTEGRITY_OK")


if __name__ == "__main__":
    main()
