
from __future__ import annotations

from pathlib import Path
import py_compile

from ontology.comparative_blueprint import ComparativeBlueprint

ROOT = Path(__file__).resolve().parent


def main() -> None:
    py_compile.compile(str(ROOT / "ontology" / "comparative_blueprint.py"), cfile="/private/tmp/comparative_blueprint.pyc", doraise=True)
    py_compile.compile(str(ROOT / "au0_final_lock.py"), cfile="/private/tmp/au0_final_lock.pyc", doraise=True)
    result = ComparativeBlueprint().step(inputs={"source": "au0_fast_acceptance"}, persist=False)
    assert result["primitive"] == "COMPARATIVE_BLUEPRINT"
    assert result["step"] == "AU0"
    assert result["status"] == "COMPARATIVE_BLUEPRINT_READY"
    assert result["comparative_science_program_ready"] is True
    assert result["target_axis_status"] == "COMPARATIVE_RF_SCIENCE_COMPLETE"
    assert result["architecture_class_count"] >= 5
    assert result["comparison_dimension_count"] >= 5
    assert result["reference_frame_count"] >= 5
    assert result["normalization_method_count"] >= 3
    for key in ["RF", "Omega", "Pi", "MEI", "CRI"]:
        assert key in result["reference_frames"]
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["epistemic_guards"]["similarity_does_not_imply_subjectivity"] is True
    print("AU0_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
