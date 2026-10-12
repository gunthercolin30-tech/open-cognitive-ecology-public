from ontology.developmental_blueprint import DevelopmentalBlueprint

READY_OR_SYNTHETIC_CONTEXT = {
    "longitudinal_observation_contract": {
        "observation_count": 3,
        "time_ordered": True,
        "functional_only": True,
    }
}


def main():
    result = DevelopmentalBlueprint().step(
        inputs=READY_OR_SYNTHETIC_CONTEXT,
        persist=False,
    )
    assert result["step"] == "AV0"
    assert result["developmental_blueprint_status"] == "DEVELOPMENTAL_BLUEPRINT_READY"
    assert result["developmental_blueprint_ready"] is True
    assert result["target_axis_status"] == "CONSCIOUSNESS_DEVELOPMENT_MODEL_COMPLETE"
    assert result["downstream_contract"]["first_operational_module"] == "genesis_detector"
    assert len(result["blueprint_hash"]) == 64
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    print("AV0_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
