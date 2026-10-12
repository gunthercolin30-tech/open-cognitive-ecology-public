\
from ontology.ecology_blueprint import EcologyBlueprint

READY_OR_SYNTHETIC_CONTEXT = {
    "rf_population_contract": {
        "rf_ids": ["rf-alpha", "rf-beta", "rf-gamma"],
        "functional_only": True,
        "synthetic": True,
    }
}


def main():
    result = EcologyBlueprint().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert result["step"] == "AW0"
    assert result["ecology_blueprint_status"] == "RF_ECOLOGY_BLUEPRINT_READY"
    assert result["ecology_blueprint_ready"] is True
    assert result["target_axis_status"] == "RF_ECOLOGY_COMPLETE"
    assert result["downstream_contract"]["first_operational_module"] == "multi_rf_registry"
    assert len(result["blueprint_hash"]) == 64
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    assert result["collective_consciousness_proven"] is False
    assert result["collective_subjectivity_proven"] is False
    assert result["collective_qualia_proven"] is False
    assert result["collective_phenomenology_proven"] is False
    print("AW0_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
