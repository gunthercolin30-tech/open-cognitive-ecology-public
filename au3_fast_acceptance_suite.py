
#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.rf_profile_builder import RFProfileBuilder

ROOT = Path.home() / "open-cognitive-ecology"

READY_CONTEXT = {
    "measurement_dimensions": [
        {"dimension_id": "RF"},
        {"dimension_id": "OMEGA"},
        {"dimension_id": "PI"},
        {"dimension_id": "MEI"},
        {"dimension_id": "CRI"},
        {"dimension_id": "GOV"},
        {"dimension_id": "LONG"},
        {"dimension_id": "AUDIT"},
    ]
}


def main() -> None:
    py_compile.compile(str(ROOT / "ontology" / "rf_profile_builder.py"), cfile="/private/tmp/au3_rf_profile_builder.pyc", doraise=True)
    result = RFProfileBuilder().step(inputs=READY_CONTEXT, persist=False)
    assert result["primitive"] == "rf_profile_builder"
    assert result["step"] == "AU3"
    assert result["rf_profile_builder_status"] == "RF_PROFILE_BUILDER_READY"
    assert result["rf_profile_ready"] is True
    assert result["comparative_profile_ready"] is True
    assert result["profile_count"] >= 4
    assert result["comparison_ready_profile_count"] >= 1
    assert result["feature_count"] >= 5
    assert result["core_dimensions_present"] is True
    assert result["canonical_profile_id"] == "oce_rf_star"
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    degraded = RFProfileBuilder().step(inputs={"architectures": [], "measurement_dimensions": []}, persist=False)
    assert degraded["rf_profile_ready"] is False
    assert degraded["functional_conclusion_only"] is True
    assert degraded["consciousness_proven"] is False

    print("AU3_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
