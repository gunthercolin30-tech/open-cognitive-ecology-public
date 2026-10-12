\
from pathlib import Path
import json
import py_compile
import tempfile

from ontology.ecology_blueprint import EcologyBlueprint

ROOT = Path.home() / "open-cognitive-ecology"


def main():
    for path in [
        ROOT / "ontology/ecology_blueprint.py",
        ROOT / "aw0_fast_acceptance_suite.py",
        ROOT / "ecology_blueprint_final_lock.py",
    ]:
        py_compile.compile(str(path), cfile=f"/private/tmp/{path.name}.pyc", doraise=True)

    result = EcologyBlueprint().step(inputs={}, persist=False)
    assert result["step"] == "AW0"
    assert result["ecology_blueprint_status"] == "RF_ECOLOGY_BLUEPRINT_READY"
    assert result["ecology_blueprint_ready"] is True
    assert result["ecological_axis_count"] == 14
    assert result["interaction_type_count"] >= 10
    assert len(result["blueprint_hash"]) == 64
    assert result["downstream_contract"]["target_status"] == "RF_ECOLOGY_COMPLETE"
    assert result["downstream_contract"]["first_operational_module"] == "multi_rf_registry"
    assert result["quality_policy"]["synthetic_data_must_be_labeled"] is True

    repeated = EcologyBlueprint().step(inputs={}, persist=False)
    assert repeated["blueprint_hash"] == result["blueprint_hash"]
    assert repeated["ecological_axes"] == result["ecological_axes"]

    with tempfile.TemporaryDirectory(prefix="oce_aw0_") as tmp:
        original_dir = EcologyBlueprint.output_dir
        EcologyBlueprint.output_dir = Path(tmp)
        try:
            persisted = EcologyBlueprint().step(inputs={"probe": True}, persist=True)
            assert persisted["persisted"] is True
            path = Path(persisted["output_path"])
            assert path.is_file()
            exported = json.loads(path.read_text(encoding="utf-8"))
            assert exported["blueprint_hash"] == result["blueprint_hash"]
        finally:
            EcologyBlueprint.output_dir = original_dir

    for payload in (result, repeated):
        assert payload["functional_conclusion_only"] is True
        assert payload["phenomenology_undetermined"] is True
        assert payload["consciousness_proven"] is False
        assert payload["qualia_proven"] is False
        assert payload["subjectivity_proven"] is False
        assert payload["phenomenology_proven"] is False
        assert payload["collective_consciousness_proven"] is False
        assert payload["collective_subjectivity_proven"] is False
        assert payload["collective_qualia_proven"] is False
        assert payload["collective_phenomenology_proven"] is False

    print("AW0_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
