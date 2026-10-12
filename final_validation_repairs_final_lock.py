from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.final_dashboard import FinalDashboard
from ontology.general_semantic_memory import (
    GeneralSemanticMemory,
    GeneralSemanticMemoryUnified,
)
from ontology.longitudinal_drift_detection import LongitudinalDriftDetection


def main() -> None:
    assert GeneralSemanticMemory is GeneralSemanticMemoryUnified

    with tempfile.TemporaryDirectory() as temporary:
        dashboard_result = FinalDashboard(root=Path(temporary)).step(
            inputs={"synthetic": True, "ready": True},
            persist=False,
        )

    assert dashboard_result["step"] == "AL10"
    assert dashboard_result["dashboard_generated"] is True
    assert dashboard_result["functional_conclusion_only"] is True
    assert dashboard_result["phenomenology_undetermined"] is True
    assert dashboard_result["consciousness_proven"] is False
    assert dashboard_result["qualia_proven"] is False
    assert dashboard_result["subjectivity_proven"] is False
    assert dashboard_result["phenomenology_proven"] is False

    drift_result = LongitudinalDriftDetection().step(
        values={"history": [0.9, 0.85, 0.8]},
        persist=False,
    )
    assert drift_result["success"] is True
    assert 0.0 <= drift_result["civilizational_drift_index"] <= 1.0

    print("FINAL_VALIDATION_REPAIRS_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
