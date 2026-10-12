\
from ontology.multi_rf_registry import MultiRFRegistry


def main() -> None:
    exact = {
        "rf_id": "RF-SAME",
        "display_name": "Same",
        "status": "ACTIVE",
        "origin": "synthetic",
        "synthetic": True,
    }
    deduplicated = MultiRFRegistry().step(
        inputs={"rf_records": [exact, dict(exact)]},
        persist=False,
    )
    assert deduplicated["multi_rf_registry_ready"] is True
    assert deduplicated["registry_count"] == 1
    assert deduplicated["exact_duplicate_count"] == 1
    assert deduplicated["collision_count"] == 0

    conflict = MultiRFRegistry().step(
        inputs={
            "rf_records": [
                exact,
                {
                    "rf_id": "RF-SAME",
                    "display_name": "Different",
                    "status": "REVOKED",
                    "origin": "synthetic",
                    "synthetic": True,
                },
            ]
        },
        persist=False,
    )
    assert conflict["multi_rf_registry_ready"] is False
    assert conflict["collision_count"] == 1
    assert conflict["collisions"][0]["resolution"] == \
        "REJECT_INCOMING_REQUIRE_EXPLICIT_REVISION"

    aliases = MultiRFRegistry().step(
        inputs={
            "rf_records": [
                {
                    "rf_id": "RF-X",
                    "aliases": ["shared"],
                    "origin": "synthetic",
                    "synthetic": True,
                },
                {
                    "rf_id": "RF-Y",
                    "aliases": ["shared"],
                    "origin": "synthetic",
                    "synthetic": True,
                },
            ]
        },
        persist=False,
    )
    assert aliases["multi_rf_registry_ready"] is False
    assert aliases["alias_conflict_count"] == 1

    print("AW1_COLLISION_AND_DEDUPLICATION_OK")


if __name__ == "__main__":
    main()
