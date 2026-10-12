#!/usr/bin/env python3
from ontology.degeneration_detector import DegenerationDetector


def obs(day, value, quality=.98):
    return {
        "timestamp_utc": f"2027-04-{day:02d}T00:00:00Z",
        "state_vector": {k: value for k in ["stability", "integration", "continuity", "governance", "complexity", "diversity", "recovery_capacity", "openness"]},
        "data_quality": quality,
    }


def main():
    engine = DegenerationDetector()
    empty = engine.step(inputs={}, persist=False)
    assert empty["degeneration_status"] == "FUNCTIONAL_DEGENERATION_UNDETERMINED"

    transient = engine.step(inputs={"observations": [obs(1,.82), obs(2,.81), obs(3,.45), obs(4,.80), obs(5,.82)]}, persist=False)
    assert transient["degeneration_detected"] is False
    assert transient["degeneration_status"] == "FUNCTIONAL_TRANSIENT_DECLINE_RECOVERED"

    poor = engine.step(inputs={"observations": [obs(1,.90,.2), obs(2,.85,.2), obs(3,.60,.2), obs(4,.45,.2), obs(5,.30,.2)]}, persist=False)
    assert poor["degeneration_status"] == "FUNCTIONAL_DEGENERATION_UNDETERMINED"

    unordered = engine.step(inputs={"observations": [obs(3,.80), obs(1,.60), obs(2,.40)]}, persist=False)
    assert unordered["degeneration_detected"] is False
    assert unordered["degeneration_status"] == "FUNCTIONAL_DEGENERATION_UNDETERMINED"

    print("AV5_DEGRADATION_OK")


if __name__ == "__main__":
    main()
