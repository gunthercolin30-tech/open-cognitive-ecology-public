from ontology.developmental_blueprint import DevelopmentalBlueprint


def main():
    first = DevelopmentalBlueprint().step(
        inputs={},
        persist=False,
    )

    second = DevelopmentalBlueprint().step(
        inputs={},
        persist=False,
    )

    assert first["blueprint_hash"] == second["blueprint_hash"]
    assert first["developmental_axes"] == second["developmental_axes"]
    assert first["event_types"] == second["event_types"]
    assert first["developmental_stages"] == second["developmental_stages"]
    assert first["downstream_contract"] == second["downstream_contract"]

    assert first["persisted"] is False
    assert second["persisted"] is False

    print("AV0_NON_REGRESSION_AND_DETERMINISM_OK")


if __name__ == "__main__":
    main()
