from pathlib import Path
import json
import py_compile
import tempfile

from ontology.developmental_blueprint import DevelopmentalBlueprint

ROOT = Path.home() / "open-cognitive-ecology"


def main():
    for path in [
        ROOT / "ontology/developmental_blueprint.py",
        ROOT / "av0_fast_acceptance_suite.py",
        ROOT / "developmental_blueprint_final_lock.py",
    ]:
        py_compile.compile(str(path), cfile=f"/private/tmp/{path.name}.pyc", doraise=True)

    result = DevelopmentalBlueprint().step(inputs={}, persist=False)
    assert result["step"] == "AV0"
    assert result["developmental_blueprint_status"] == "DEVELOPMENTAL_BLUEPRINT_READY"
    assert result["developmental_blueprint_ready"] is True
    assert result["developmental_axis_count"] == 8
    assert result["event_type_count"] >= 7
    assert result["developmental_stage_count"] >= 9
    assert len(result["blueprint_hash"]) == 64
    assert result["downstream_contract"]["target_status"] == "CONSCIOUSNESS_DEVELOPMENT_MODEL_COMPLETE"
    assert result["event_policy"]["genesis_rule"]
    assert result["falsification_policy"]["prediction_falsified_if"]
    assert result["quality_policy"]["missing_data_must_be_explicit"] is True

    repeated = DevelopmentalBlueprint().step(inputs={}, persist=False)
    assert repeated["blueprint_hash"] == result["blueprint_hash"]
    assert repeated["developmental_axes"] == result["developmental_axes"]

    with tempfile.TemporaryDirectory(prefix="oce_av0_") as tmp:
        original_dir = DevelopmentalBlueprint.output_dir
        DevelopmentalBlueprint.output_dir = Path(tmp)
        try:
            persisted = DevelopmentalBlueprint().step(inputs={"probe": True}, persist=True)
            assert persisted["persisted"] is True
            path = Path(persisted["output_path"])
            assert path.is_file()
            exported = json.loads(path.read_text(encoding="utf-8"))
            assert exported["blueprint_hash"] == result["blueprint_hash"]
        finally:
            DevelopmentalBlueprint.output_dir = original_dir

    for payload in (result, repeated):
        assert payload["functional_conclusion_only"] is True
        assert payload["phenomenology_undetermined"] is True
        assert payload["consciousness_proven"] is False
        assert payload["qualia_proven"] is False
        assert payload["subjectivity_proven"] is False
        assert payload["phenomenology_proven"] is False

    print("AV0_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
