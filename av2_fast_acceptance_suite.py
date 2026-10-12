from pathlib import Path
import json
import py_compile
import tempfile

from ontology.maturation_tracker import MaturationTracker

ROOT = Path.home() / "open-cognitive-ecology"

GENESIS = {
    "genesis_detected": True,
    "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
}


def observation(day, base):
    return {
        "timestamp_utc": f"2026-03-{day:02d}T00:00:00Z",
        "stability": base + 0.01,
        "integration": base,
        "continuity": base + 0.02,
        "governance": base - 0.01,
        "complexity": base - 0.02,
        "diversity": base,
        "recovery": base + 0.01,
        "data_quality": 0.96,
        "synthetic": True,
        "source": "av2_fast",
    }


def assert_guards(result):
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False


def main():
    for path in [
        ROOT / "ontology/maturation_tracker.py",
        ROOT / "av2_fast_acceptance_suite.py",
        ROOT / "maturation_tracker_final_lock.py",
        ROOT / "av2_degradation_test.py",
        ROOT / "av2_non_regression_test.py",
    ]:
        py_compile.compile(str(path), cfile=f"/private/tmp/{path.name}.pyc", doraise=True)

    growth = {"genesis_result": GENESIS, "observations": [
        observation(1, 0.48), observation(2, 0.56), observation(3, 0.64),
        observation(4, 0.72), observation(5, 0.82), observation(6, 0.88),
    ]}
    result = MaturationTracker().step(inputs=growth, persist=False)
    assert result["step"] == "AV2"
    assert result["maturation_status"] == "FUNCTIONAL_MATURATION_COMPLETE"
    assert result["maturation_complete"] is True
    assert result["maturation_score"] >= 0.75
    assert result["maturation_velocity"] > 0.02
    assert result["regression_detected"] is False
    assert len(result["maturation_hash"]) == 64
    assert_guards(result)

    repeated = MaturationTracker().step(inputs=growth, persist=False)
    assert repeated["maturation_hash"] == result["maturation_hash"]
    assert repeated["maturation_score"] == result["maturation_score"]

    with tempfile.TemporaryDirectory(prefix="oce_av2_") as tmp:
        original = MaturationTracker.output_dir
        MaturationTracker.output_dir = Path(tmp)
        try:
            persisted = MaturationTracker().step(inputs=growth, persist=True)
            assert persisted["persisted"] is True
            path = Path(persisted["output_path"])
            assert path.is_file()
            exported = json.loads(path.read_text(encoding="utf-8"))
            assert exported["maturation_hash"] == result["maturation_hash"]
        finally:
            MaturationTracker.output_dir = original

    print("AV2_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
