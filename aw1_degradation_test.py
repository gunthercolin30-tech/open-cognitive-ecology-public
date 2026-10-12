\
from ontology.multi_rf_registry import MultiRFRegistry


def main() -> None:
    empty = MultiRFRegistry().step(
        inputs={"rf_records": []},
        persist=False,
    )
    assert empty["multi_rf_registry_status"] == "MULTI_RF_REGISTRY_INCOMPLETE"
    assert empty["registry_count"] == 0
    assert empty["multi_rf_population"] is False
    assert empty["persisted"] is False

    collision = MultiRFRegistry().step(
        inputs={
            "rf_records": [
                {
                    "rf_id": "RF-COLLISION",
                    "display_name": "First",
                    "status": "ACTIVE",
                    "origin": "synthetic",
                    "synthetic": True,
                },
                {
                    "rf_id": "RF-COLLISION",
                    "display_name": "Conflicting second",
                    "status": "INACTIVE",
                    "origin": "synthetic",
                    "synthetic": True,
                },
            ]
        },
        persist=True,
    )
    assert collision["multi_rf_registry_status"] == "MULTI_RF_REGISTRY_INCOMPLETE"
    assert collision["collision_count"] == 1
    assert collision["persisted"] is False

    for payload in [empty, collision]:
        assert payload["functional_conclusion_only"] is True
        assert payload["phenomenology_undetermined"] is True
        assert payload["consciousness_proven"] is False
        assert payload["collective_consciousness_proven"] is False

    print("AW1_DEGRADATION_OK")


if __name__ == "__main__":
    main()
