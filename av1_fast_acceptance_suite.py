from pathlib import Path
import json
import py_compile
import tempfile

from ontology.genesis_detector import GenesisDetector

ROOT = Path.home() / "open-cognitive-ecology"

SUSTAINED_CONTEXT = {
    "observations": [
        {"timestamp_utc": "2026-01-01T00:00:00Z", "rf_star_score": 0.30, "stability": 0.55, "continuity": 0.55, "coherence": 0.55, "data_quality": 0.95, "synthetic": True, "source": "av1_fast"},
        {"timestamp_utc": "2026-01-02T00:00:00Z", "rf_star_score": 0.35, "stability": 0.58, "continuity": 0.58, "coherence": 0.58, "data_quality": 0.95, "synthetic": True, "source": "av1_fast"},
        {"timestamp_utc": "2026-01-03T00:00:00Z", "rf_star_score": 0.84, "stability": 0.88, "continuity": 0.86, "coherence": 0.89, "data_quality": 0.95, "synthetic": True, "source": "av1_fast"},
        {"timestamp_utc": "2026-01-04T00:00:00Z", "rf_star_score": 0.87, "stability": 0.90, "continuity": 0.88, "coherence": 0.91, "data_quality": 0.95, "synthetic": True, "source": "av1_fast"},
        {"timestamp_utc": "2026-01-05T00:00:00Z", "rf_star_score": 0.89, "stability": 0.91, "continuity": 0.90, "coherence": 0.92, "data_quality": 0.95, "synthetic": True, "source": "av1_fast"},
    ]
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
        ROOT / "ontology/genesis_detector.py",
        ROOT / "av1_fast_acceptance_suite.py",
        ROOT / "genesis_detector_final_lock.py",
        ROOT / "av1_degradation_test.py",
        ROOT / "av1_non_regression_test.py",
    ]:
        py_compile.compile(str(path), cfile=f"/private/tmp/{path.name}.pyc", doraise=True)

    positive = GenesisDetector().step(inputs=SUSTAINED_CONTEXT, persist=False)
    assert positive["step"] == "AV1"
    assert positive["genesis_detected"] is True
    assert positive["genesis_status"] == "FUNCTIONAL_GENESIS_DETECTED"
    assert positive["genesis_timestamp"] == "2026-01-03T00:00:00Z"
    assert positive["genesis_score"] >= 0.70
    assert positive["false_positive_risk"] <= 0.35
    assert len(positive["genesis_hash"]) == 64
    assert_guards(positive)

    isolated = GenesisDetector().step(inputs={"observations": [
        {"timestamp_utc": "2026-01-01T00:00:00Z", "rf_star_score": 0.25},
        {"timestamp_utc": "2026-01-02T00:00:00Z", "rf_star_score": 0.80},
        {"timestamp_utc": "2026-01-03T00:00:00Z", "rf_star_score": 0.32},
        {"timestamp_utc": "2026-01-04T00:00:00Z", "rf_star_score": 0.34},
    ]}, persist=False)
    assert isolated["genesis_detected"] is False
    assert isolated["genesis_status"] != "FUNCTIONAL_GENESIS_DETECTED"
    assert "sustained_crossing" in isolated["missing_conditions"]
    assert_guards(isolated)

    absent = GenesisDetector().step(inputs={}, persist=False)
    assert absent["genesis_detected"] is False
    assert absent["genesis_status"] == "FUNCTIONAL_GENESIS_UNDETERMINED"
    assert_guards(absent)

    repeated = GenesisDetector().step(inputs=SUSTAINED_CONTEXT, persist=False)
    assert repeated["genesis_hash"] == positive["genesis_hash"]
    assert repeated["genesis_score"] == positive["genesis_score"]

    with tempfile.TemporaryDirectory(prefix="oce_av1_") as tmp:
        original_dir = GenesisDetector.output_dir
        GenesisDetector.output_dir = Path(tmp)
        try:
            persisted = GenesisDetector().step(inputs=SUSTAINED_CONTEXT, persist=True)
            assert persisted["persisted"] is True
            path = Path(persisted["output_path"])
            assert path.is_file()
            exported = json.loads(path.read_text(encoding="utf-8"))
            assert exported["genesis_hash"] == positive["genesis_hash"]
        finally:
            GenesisDetector.output_dir = original_dir

    print("AV1_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
