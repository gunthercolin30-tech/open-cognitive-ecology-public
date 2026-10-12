#!/usr/bin/env python3
import py_compile
from pathlib import Path
from ontology.degeneration_detector import DegenerationDetector

ROOT = Path.home() / "open-cognitive-ecology"
py_compile.compile(str(ROOT / "ontology" / "degeneration_detector.py"), cfile="/private/tmp/oce_av5_degeneration_detector.pyc", doraise=True)


def obs(day, value, quality=0.98):
    return {
        "timestamp_utc": f"2027-02-{day:02d}T00:00:00Z",
        "state_vector": {
            "stability": value,
            "integration": value,
            "continuity": value,
            "governance": value,
            "complexity": value,
            "diversity": value,
            "recovery_capacity": value,
            "openness": value,
        },
        "data_quality": quality,
        "synthetic": True,
    }


def assert_guards(result):
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def main():
    engine = DegenerationDetector()
    progressive = engine.step(inputs={"observations": [obs(1, .88), obs(2, .86), obs(3, .72), obs(4, .60), obs(5, .48)]}, persist=False)
    assert progressive["degeneration_detected"] is True
    assert progressive["degeneration_status"] in {"FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED", "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED", "FUNCTIONAL_COLLAPSE_DETECTED"}
    assert progressive["degeneration_score"] > 0.10
    assert len(progressive["affected_dimensions"]) >= 3
    assert progressive["degeneration_hash"]
    assert_guards(progressive)

    stable = engine.step(inputs={"observations": [obs(1, .80), obs(2, .81), obs(3, .79), obs(4, .80), obs(5, .81)]}, persist=False)
    assert stable["degeneration_detected"] is False
    assert stable["degeneration_status"] == "FUNCTIONAL_DEGENERATION_NOT_DETECTED"

    persisted = engine.step(inputs={"observations": [obs(1, .90), obs(2, .88), obs(3, .60), obs(4, .52), obs(5, .45)]}, persist=True)
    assert Path(persisted["output_path"]).exists()
    print("AV5_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
