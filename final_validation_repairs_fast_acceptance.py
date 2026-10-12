from __future__ import annotations

import tempfile
from pathlib import Path

from ontology.final_dashboard import FinalDashboard
from ontology.general_semantic_memory import (
    GeneralSemanticMemory,
    GeneralSemanticMemoryUnified,
)
from ontology.longitudinal_drift_detection import LongitudinalDriftDetection
from validation.full_validation_runner import _scientific_report


def main() -> None:
    assert GeneralSemanticMemory is GeneralSemanticMemoryUnified

    with tempfile.TemporaryDirectory() as temporary:
        dashboard = FinalDashboard(root=Path(temporary))
        result = dashboard.step(
            inputs={"synthetic": True, "ready": True},
            persist=False,
        )
        rendered = dashboard._render_html(result)
        assert "width:100%;" in rendered
        assert "FINAL_DASHBOARD_GENERATED" in rendered
        assert "phenomenology remains undetermined" in rendered

    detector = LongitudinalDriftDetection()
    nominal = detector.step(values=[0.8, 0.75, 0.7], persist=False)
    assert nominal["success"] is True
    assert nominal["sample_count"] == 3

    mapped = detector.step(
        values={
            "primitive": "VALIDATION_CONTEXT",
            "history": [0.9, 0.85, 0.8],
        },
        persist=False,
    )
    assert mapped["success"] is True
    assert mapped["sample_count"] == 3

    degraded = detector.step(
        values={"primitive": "VALIDATION_CONTEXT"},
        persist=False,
    )
    assert degraded["success"] is False
    assert degraded["reason"] == "insufficient_history"

    synthetic_results = [
        {
            "module": "ontology.import_failure",
            "import_success": False,
            "import_error": "ImportError: synthetic",
            "classes": [],
        },
        {
            "module": "ontology.step_failure",
            "import_success": True,
            "import_error": None,
            "probe_returncode": 0,
            "classes": [
                {
                    "step_analysis": {
                        "step_error": "ValueError: synthetic",
                        "step_executed": False,
                    }
                }
            ],
        },
        {
            "module": "ontology.step_failure",
            "import_success": True,
            "import_error": None,
            "probe_returncode": 0,
            "classes": [
                {
                    "step_analysis": {
                        "step_error": "ValueError: synthetic",
                        "step_executed": False,
                    }
                }
            ],
        },
    ]
    report = _scientific_report(synthetic_results, {"test": True})
    failed = report["diagnostics"]["failed_modules"]
    assert failed == [
        "ontology.import_failure",
        "ontology.step_failure",
    ]
    assert report["summary"]["overall_success"] is False

    print("FINAL_VALIDATION_REPAIRS_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
