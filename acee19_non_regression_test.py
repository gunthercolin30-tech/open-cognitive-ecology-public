#!/usr/bin/env python3
from copy import deepcopy
from ontology.acee_meta_analysis import ACEEMetaAnalysis


def main():
    inputs = {
        "observations": [
            {"observation_id": "immutable", "effect_size": 0.1, "variance": 1.0}
        ]
    }
    before = deepcopy(inputs)
    ACEEMetaAnalysis().step(inputs=inputs, persist=False)
    assert inputs == before
    print("ACEE19_NON_REGRESSION_TEST_OK")


if __name__ == "__main__":
    main()
