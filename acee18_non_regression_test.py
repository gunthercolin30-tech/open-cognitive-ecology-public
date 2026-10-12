#!/usr/bin/env python3
from copy import deepcopy
from ontology.acee_prediction_engine import ACEEPredictionEngine


def main() -> None:
    inputs = {
        "candidates": [
            {"candidate_id": "immutable", "predicted_gain": 0.2}
        ]
    }
    before = deepcopy(inputs)
    ACEEPredictionEngine().step(inputs=inputs, persist=False)
    assert inputs == before
    print("ACEE18_NON_REGRESSION_TEST_OK")


if __name__ == "__main__":
    main()
